"""
Documentation API endpoints.

Provides access to in-app documentation including:
- List all documentation files
- Get specific document content
- Search across all documentation
- Browse by category
"""

import os
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from datetime import datetime

from app.models.docs_metadata import (
    DOCS_METADATA,
    CATEGORIES,
    get_doc_metadata,
    get_all_docs_metadata,
    get_docs_by_category,
)
from app.utils.doc_search import search_docs, get_doc_content


router = APIRouter()

# Get docs directory path (relative to project root)
DOCS_DIR = Path(__file__).parent.parent.parent.parent / "docs"


# Pydantic models for API responses
class DocListItem(BaseModel):
    """Document list item with basic info."""
    name: str
    title: str
    category: str
    description: str
    tags: List[str]
    size: Optional[int] = None
    last_updated: Optional[str] = None
    icon: str


class DocContentResponse(BaseModel):
    """Document content response."""
    name: str
    title: str
    content: str
    category: str
    description: str
    tags: List[str]
    related: List[str]
    last_updated: Optional[str] = None


class SearchResultItem(BaseModel):
    """Search result item."""
    doc_name: str
    title: str
    excerpt: str
    matches: int
    relevance: float
    section: Optional[str] = None


class SearchResponse(BaseModel):
    """Search results response."""
    query: str
    results: List[SearchResultItem]
    total: int


class CategoryInfo(BaseModel):
    """Category information."""
    key: str
    name: str
    icon: str
    description: str
    doc_count: int
    docs: List[DocListItem]


class CategoriesResponse(BaseModel):
    """Categories response."""
    categories: List[CategoryInfo]


@router.get("/list", response_model=List[DocListItem])
async def list_docs():
    """
    Get list of all available documentation files.

    Returns:
        List of documents with metadata
    """
    docs = []

    for doc_metadata in get_all_docs_metadata():
        # Get file stats if file exists
        file_path = DOCS_DIR / doc_metadata.name
        size = None
        last_updated = None

        if file_path.exists():
            stat = file_path.stat()
            size = stat.st_size
            last_updated = datetime.fromtimestamp(stat.st_mtime).isoformat()

        docs.append(DocListItem(
            name=doc_metadata.name,
            title=doc_metadata.title,
            category=doc_metadata.category,
            description=doc_metadata.description,
            tags=doc_metadata.tags,
            size=size,
            last_updated=last_updated,
            icon=doc_metadata.icon
        ))

    return docs


@router.get("/search", response_model=SearchResponse)
async def search(
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of results")
):
    """
    Search across all documentation files.

    Args:
        q: Search query string (minimum 2 characters)
        limit: Maximum number of results to return (1-100)

    Returns:
        Search results with excerpts and relevance scores
    """
    results = search_docs(q, str(DOCS_DIR), limit)

    result_items = [
        SearchResultItem(
            doc_name=result.doc_name,
            title=result.title,
            excerpt=result.excerpt,
            matches=result.matches,
            relevance=result.relevance,
            section=result.section
        )
        for result in results
    ]

    return SearchResponse(
        query=q,
        results=result_items,
        total=len(result_items)
    )


@router.get("/categories", response_model=CategoriesResponse)
async def get_categories():
    """
    Get all documentation organized by category.

    Returns:
        List of categories with their documents
    """
    categories = []

    for category_key, category_info in CATEGORIES.items():
        # Get docs in this category
        category_docs = get_docs_by_category(category_key)

        # Convert to DocListItem
        doc_items = []
        for doc_metadata in category_docs:
            file_path = DOCS_DIR / doc_metadata.name
            size = None
            last_updated = None

            if file_path.exists():
                stat = file_path.stat()
                size = stat.st_size
                last_updated = datetime.fromtimestamp(stat.st_mtime).isoformat()

            doc_items.append(DocListItem(
                name=doc_metadata.name,
                title=doc_metadata.title,
                category=doc_metadata.category,
                description=doc_metadata.description,
                tags=doc_metadata.tags,
                size=size,
                last_updated=last_updated,
                icon=doc_metadata.icon
            ))

        categories.append(CategoryInfo(
            key=category_key,
            name=category_info["name"],
            icon=category_info["icon"],
            description=category_info["description"],
            doc_count=len(doc_items),
            docs=doc_items
        ))

    return CategoriesResponse(categories=categories)


@router.get("/{doc_name}", response_model=DocContentResponse)
async def get_doc(doc_name: str):
    """
    Get content of a specific documentation file.

    Args:
        doc_name: Name of the documentation file (e.g., USER_GUIDE.md)

    Returns:
        Document content and metadata

    Raises:
        HTTPException: 404 if document not found
    """
    # Validate doc_name (prevent path traversal)
    if ".." in doc_name or "/" in doc_name or "\\" in doc_name:
        raise HTTPException(status_code=400, detail="Invalid document name")

    # Get metadata
    metadata = get_doc_metadata(doc_name)
    if not metadata:
        raise HTTPException(status_code=404, detail="Document not found")

    # Get content
    content = get_doc_content(doc_name, str(DOCS_DIR))
    if content is None:
        raise HTTPException(status_code=404, detail="Document file not found")

    # Get file stats
    file_path = DOCS_DIR / doc_name
    last_updated = None
    if file_path.exists():
        stat = file_path.stat()
        last_updated = datetime.fromtimestamp(stat.st_mtime).isoformat()

    return DocContentResponse(
        name=metadata.name,
        title=metadata.title,
        content=content,
        category=metadata.category,
        description=metadata.description,
        tags=metadata.tags,
        related=metadata.related,
        last_updated=last_updated
    )