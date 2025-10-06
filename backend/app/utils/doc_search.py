"""
Documentation search utility.

Provides full-text search across markdown documentation files with:
- Relevance ranking (headings weighted higher)
- Excerpt generation with context
- Search term highlighting
- Caching for performance
"""

import os
import re
from typing import List, Dict, Optional
from dataclasses import dataclass
from pathlib import Path


@dataclass
class SearchResult:
    """A single search result."""
    doc_name: str
    title: str
    excerpt: str
    matches: int
    relevance: float
    section: Optional[str] = None


class DocSearchIndex:
    """Search index for documentation files."""

    def __init__(self, docs_dir: str):
        self.docs_dir = Path(docs_dir)
        self._index: Dict[str, str] = {}
        self._build_index()

    def _build_index(self):
        """Build search index from all markdown files."""
        if not self.docs_dir.exists():
            return

        for file_path in self.docs_dir.glob("*.md"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self._index[file_path.name] = content
            except Exception as e:
                print(f"Error reading {file_path.name}: {e}")

    def search(self, query: str, limit: int = 20) -> List[SearchResult]:
        """
        Search all documents for the query string.

        Args:
            query: Search query string
            limit: Maximum number of results to return

        Returns:
            List of SearchResult objects, ranked by relevance
        """
        if not query or len(query.strip()) < 2:
            return []

        query = query.strip()
        results = []

        for doc_name, content in self._index.items():
            # Calculate matches and relevance
            result = self._search_document(doc_name, content, query)
            if result:
                results.append(result)

        # Sort by relevance (descending)
        results.sort(key=lambda x: x.relevance, reverse=True)

        return results[:limit]

    def _search_document(
        self, doc_name: str, content: str, query: str
    ) -> Optional[SearchResult]:
        """
        Search a single document.

        Returns:
            SearchResult if matches found, None otherwise
        """
        query_lower = query.lower()
        content_lower = content.lower()

        # Count total matches
        matches = content_lower.count(query_lower)
        if matches == 0:
            return None

        # Calculate relevance score
        relevance = self._calculate_relevance(content, query_lower, matches)

        # Extract title (first # heading)
        title = self._extract_title(content) or doc_name.replace('.md', '').replace('_', ' ')

        # Generate excerpt
        excerpt = self._generate_excerpt(content, query_lower)

        # Find best matching section
        section = self._find_section(content, query_lower)

        return SearchResult(
            doc_name=doc_name,
            title=title,
            excerpt=excerpt,
            matches=matches,
            relevance=relevance,
            section=section
        )

    def _calculate_relevance(
        self, content: str, query: str, matches: int
    ) -> float:
        """
        Calculate relevance score for search result.

        Factors:
        - Matches in headings (weight: 3.0)
        - Matches in first 500 chars (weight: 2.0)
        - Total number of matches (weight: 1.0)
        - Match density (matches per 1000 chars)
        """
        score = 0.0

        # Weight matches in headings higher
        heading_matches = len(re.findall(
            rf'^#+\s+.*{re.escape(query)}.*$',
            content,
            re.IGNORECASE | re.MULTILINE
        ))
        score += heading_matches * 3.0

        # Weight matches in intro higher (first 500 chars)
        intro = content[:500].lower()
        intro_matches = intro.count(query)
        score += intro_matches * 2.0

        # Add base matches
        score += matches * 1.0

        # Add density score
        density = (matches / max(len(content), 1)) * 1000
        score += density

        return score

    def _extract_title(self, content: str) -> Optional[str]:
        """Extract document title from first heading."""
        match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        return match.group(1).strip() if match else None

    def _generate_excerpt(self, content: str, query: str, context_chars: int = 100) -> str:
        """
        Generate excerpt with highlighted search term.

        Args:
            content: Document content
            query: Search query
            context_chars: Characters of context before/after match

        Returns:
            Excerpt string with <<highlight>> markers
        """
        content_lower = content.lower()

        # Find first occurrence
        pos = content_lower.find(query)
        if pos == -1:
            # Return first 200 chars if no match (shouldn't happen)
            return content[:200].strip() + "..."

        # Extract context
        start = max(0, pos - context_chars)
        end = min(len(content), pos + len(query) + context_chars)

        excerpt = content[start:end]

        # Clean up excerpt (avoid breaking mid-word)
        if start > 0:
            # Find first space after start
            space_pos = excerpt.find(' ')
            if space_pos > 0:
                excerpt = excerpt[space_pos:].lstrip()

        if end < len(content):
            # Find last space before end
            space_pos = excerpt.rfind(' ')
            if space_pos > 0:
                excerpt = excerpt[:space_pos].rstrip()

        # Add ellipsis
        if start > 0:
            excerpt = "..." + excerpt
        if end < len(content):
            excerpt = excerpt + "..."

        # Highlight search term (case-insensitive)
        # Use <<>> markers that will be converted to <mark> tags in frontend
        highlighted = re.sub(
            f'({re.escape(query)})',
            r'<<\1>>',
            excerpt,
            flags=re.IGNORECASE
        )

        return highlighted

    def _find_section(self, content: str, query: str) -> Optional[str]:
        """
        Find the section (heading) where the match occurs.

        Returns:
            Section heading text, or None
        """
        lines = content.split('\n')
        current_section = None

        for line in lines:
            # Check if line is a heading
            heading_match = re.match(r'^(#+)\s+(.+)$', line)
            if heading_match:
                current_section = heading_match.group(2).strip()

            # Check if query appears in this line
            if query in line.lower():
                return current_section

        return None

    def get_document_content(self, doc_name: str) -> Optional[str]:
        """Get the full content of a document."""
        return self._index.get(doc_name)

    def refresh_index(self):
        """Rebuild the search index."""
        self._index.clear()
        self._build_index()


# Global search index instance (initialized in API)
_search_index: Optional[DocSearchIndex] = None


def get_search_index(docs_dir: str) -> DocSearchIndex:
    """Get or create the global search index."""
    global _search_index

    if _search_index is None:
        _search_index = DocSearchIndex(docs_dir)

    return _search_index


def search_docs(query: str, docs_dir: str, limit: int = 20) -> List[SearchResult]:
    """
    Search documentation files.

    Args:
        query: Search query string
        docs_dir: Directory containing documentation files
        limit: Maximum number of results

    Returns:
        List of SearchResult objects
    """
    index = get_search_index(docs_dir)
    return index.search(query, limit)


def get_doc_content(doc_name: str, docs_dir: str) -> Optional[str]:
    """
    Get content of a specific document.

    Args:
        doc_name: Name of the document file
        docs_dir: Directory containing documentation files

    Returns:
        Document content as string, or None if not found
    """
    index = get_search_index(docs_dir)
    return index.get_document_content(doc_name)