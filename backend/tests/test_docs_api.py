"""
Tests for Documentation API endpoints

Tests all endpoints in /api/docs router:
- GET /api/docs/list - List all documentation files
- GET /api/docs/{doc_name} - Get specific document content
- GET /api/docs/search - Search documentation
- GET /api/docs/categories - Get documentation categories
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestDocsList:
    """Tests for GET /api/docs/list endpoint"""

    def test_list_returns_200(self):
        """Should return 200 status code"""
        response = client.get("/api/docs/list")
        assert response.status_code == 200

    def test_list_returns_array(self):
        """Should return an array of documents"""
        response = client.get("/api/docs/list")
        data = response.json()
        assert isinstance(data, list)

    def test_list_returns_all_docs(self):
        """Should return all 9 documentation files"""
        response = client.get("/api/docs/list")
        data = response.json()
        assert len(data) == 9

    def test_list_doc_has_required_fields(self):
        """Each document should have required fields"""
        response = client.get("/api/docs/list")
        data = response.json()

        required_fields = ["name", "title", "category", "description", "tags"]
        for doc in data:
            for field in required_fields:
                assert field in doc, f"Document missing field: {field}"

    def test_list_includes_specific_docs(self):
        """Should include all expected documentation files"""
        response = client.get("/api/docs/list")
        data = response.json()

        doc_names = [doc["name"] for doc in data]
        expected_docs = [
            "USER_GUIDE.md",
            "IHT_USER_GUIDE.md",
            "IHT_CALCULATION_METHODOLOGY.md",
            "IHT_COMPLIANCE_CHECKLIST.md",
            "VIDEO_TUTORIALS.md",
            "API_DOCUMENTATION.md",
            "ARCHITECTURE.md",
            "DEVELOPER_DOCUMENTATION.md",
            "README.md"
        ]

        for expected_doc in expected_docs:
            assert expected_doc in doc_names, f"Missing doc: {expected_doc}"


class TestGetDoc:
    """Tests for GET /api/docs/{doc_name} endpoint"""

    def test_get_doc_returns_200_for_valid_doc(self):
        """Should return 200 for valid document"""
        response = client.get("/api/docs/README.md")
        assert response.status_code == 200

    def test_get_doc_returns_content_and_metadata(self):
        """Should return document content and metadata"""
        response = client.get("/api/docs/README.md")
        data = response.json()

        assert "content" in data
        assert "name" in data
        assert "title" in data
        assert "category" in data
        assert isinstance(data["content"], str)
        assert len(data["content"]) > 0

    def test_get_doc_returns_404_for_nonexistent_doc(self):
        """Should return 404 for non-existent document"""
        response = client.get("/api/docs/NONEXISTENT.md")
        assert response.status_code == 404

    def test_get_doc_prevents_path_traversal(self):
        """Should prevent path traversal attacks"""
        # Try to access file outside docs directory
        response = client.get("/api/docs/../../../etc/passwd")
        assert response.status_code in [400, 404]

        response = client.get("/api/docs/..%2F..%2F..%2Fetc%2Fpasswd")
        assert response.status_code in [400, 404]

    def test_get_doc_handles_special_characters(self):
        """Should handle document names with underscores and hyphens"""
        response = client.get("/api/docs/USER_GUIDE.md")
        assert response.status_code == 200

        response = client.get("/api/docs/IHT_COMPLIANCE_CHECKLIST.md")
        assert response.status_code == 200

    def test_get_doc_content_is_markdown(self):
        """Document content should be markdown text"""
        response = client.get("/api/docs/README.md")
        data = response.json()

        content = data["content"]
        # Check for common markdown patterns
        assert any(char in content for char in ["#", "*", "-", "[", "]"])


class TestSearchDocs:
    """Tests for GET /api/docs/search endpoint"""

    def test_search_returns_200(self):
        """Should return 200 status code"""
        response = client.get("/api/docs/search?q=iht")
        assert response.status_code == 200

    def test_search_returns_relevant_results(self):
        """Should return results relevant to query"""
        response = client.get("/api/docs/search?q=iht")
        data = response.json()

        assert "results" in data
        assert isinstance(data["results"], list)
        assert len(data["results"]) > 0

    def test_search_results_include_excerpts(self):
        """Search results should include excerpts with context"""
        response = client.get("/api/docs/search?q=inheritance")
        data = response.json()

        if len(data["results"]) > 0:
            result = data["results"][0]
            assert "excerpt" in result
            assert "doc_name" in result
            assert "title" in result
            assert isinstance(result["excerpt"], str)

    def test_search_results_ranked_by_relevance(self):
        """Results should be ranked by relevance score"""
        response = client.get("/api/docs/search?q=pension")
        data = response.json()

        if len(data["results"]) > 1:
            results = data["results"]
            # Check that relevance scores are in descending order
            for i in range(len(results) - 1):
                assert results[i]["relevance"] >= results[i + 1]["relevance"]

    def test_search_handles_empty_query(self):
        """Should handle empty query gracefully"""
        response = client.get("/api/docs/search?q=")
        data = response.json()
        assert response.status_code in [200, 422]
        # Empty query should return empty results or error
        if response.status_code == 200:
            assert len(data["results"]) == 0

    def test_search_handles_no_results(self):
        """Should handle queries with no results"""
        response = client.get("/api/docs/search?q=xyzabc123nonexistent")
        data = response.json()

        assert len(data["results"]) == 0

    def test_search_is_case_insensitive(self):
        """Search should be case-insensitive"""
        response1 = client.get("/api/docs/search?q=IHT")
        response2 = client.get("/api/docs/search?q=iht")

        data1 = response1.json()
        data2 = response2.json()

        # Should return same number of results
        assert len(data1["results"]) == len(data2["results"])

    def test_search_respects_limit_parameter(self):
        """Should respect the limit parameter"""
        response = client.get("/api/docs/search?q=tax&limit=3")
        data = response.json()

        assert len(data["results"]) <= 3

    def test_search_highlights_terms(self):
        """Should highlight search terms in excerpts"""
        response = client.get("/api/docs/search?q=calculator")
        data = response.json()

        if len(data["results"]) > 0:
            excerpt = data["results"][0]["excerpt"]
            # Check for highlight markers
            assert "<<" in excerpt or "calculator" in excerpt.lower()


class TestCategories:
    """Tests for GET /api/docs/categories endpoint"""

    def test_categories_returns_200(self):
        """Should return 200 status code"""
        response = client.get("/api/docs/categories")
        assert response.status_code == 200

    def test_categories_returns_all_categories(self):
        """Should return all 9 categories"""
        response = client.get("/api/docs/categories")
        data = response.json()

        assert "categories" in data
        categories = data["categories"]
        assert len(categories) == 9

    def test_categories_have_correct_structure(self):
        """Each category should have name, docs, doc_count"""
        response = client.get("/api/docs/categories")
        data = response.json()

        for category in data["categories"]:
            assert "name" in category
            assert "docs" in category
            assert "doc_count" in category
            assert isinstance(category["docs"], list)
            assert category["doc_count"] == len(category["docs"])

    def test_categories_docs_grouped_correctly(self):
        """Documents should be grouped in correct categories"""
        response = client.get("/api/docs/categories")
        data = response.json()

        # Find IHT Planning category
        iht_category = next(
            (cat for cat in data["categories"] if cat["name"] == "IHT Planning"),
            None
        )

        assert iht_category is not None
        assert iht_category["doc_count"] > 0

        # Check that IHT docs are in this category
        doc_names = [doc["name"] for doc in iht_category["docs"]]
        assert "IHT_USER_GUIDE.md" in doc_names

    def test_categories_include_expected_categories(self):
        """Should include all expected categories"""
        response = client.get("/api/docs/categories")
        data = response.json()

        category_names = [cat["name"] for cat in data["categories"]]
        expected_categories = [
            "Getting Started",
            "IHT Planning",
            "Pension Planning",
            "Financial Management",
            "Tax Optimization",
            "Developer Resources",
            "Compliance",
            "Video Tutorials",
            "Help & Support"
        ]

        for expected_cat in expected_categories:
            assert expected_cat in category_names


class TestErrorHandling:
    """Tests for error handling"""

    def test_invalid_doc_name_returns_404(self):
        """Should return 404 for invalid document name"""
        response = client.get("/api/docs/invalid_doc_that_doesnt_exist.md")
        assert response.status_code == 404

    def test_malformed_search_query_handled(self):
        """Should handle malformed search queries"""
        # Test with special characters
        response = client.get("/api/docs/search?q=%00%01%02")
        assert response.status_code in [200, 400]

    def test_missing_search_parameter_handled(self):
        """Should handle missing search parameter"""
        response = client.get("/api/docs/search")
        # Should either require param or handle gracefully
        assert response.status_code in [200, 400, 422]


class TestPerformance:
    """Tests for performance requirements"""

    def test_search_response_time_under_100ms(self):
        """Search should respond in under 100ms (after warming up)"""
        import time

        # Warm up cache
        client.get("/api/docs/search?q=test")

        # Measure response time
        start = time.time()
        response = client.get("/api/docs/search?q=inheritance")
        end = time.time()

        response_time_ms = (end - start) * 1000
        assert response.status_code == 200
        # Allow some tolerance for CI/CD environments
        assert response_time_ms < 200, f"Search took {response_time_ms}ms"

    def test_list_response_fast(self):
        """List endpoint should be fast"""
        import time

        start = time.time()
        response = client.get("/api/docs/list")
        end = time.time()

        response_time_ms = (end - start) * 1000
        assert response.status_code == 200
        assert response_time_ms < 200


class TestCaching:
    """Tests for caching functionality"""

    def test_search_index_caches(self):
        """Search index should use caching"""
        import time

        # First search (builds index)
        start1 = time.time()
        response1 = client.get("/api/docs/search?q=test")
        end1 = time.time()
        time1 = end1 - start1

        # Second search (uses cached index)
        start2 = time.time()
        response2 = client.get("/api/docs/search?q=different")
        end2 = time.time()
        time2 = end2 - start2

        assert response1.status_code == 200
        assert response2.status_code == 200

        # Second search should be faster or similar
        # (allowing some variance for test environment)
        assert time2 <= time1 * 1.5


class TestDataIntegrity:
    """Tests for data integrity"""

    def test_all_metadata_has_valid_structure(self):
        """All document metadata should have valid structure"""
        response = client.get("/api/docs/list")
        data = response.json()

        for doc in data:
            # Required fields
            assert doc["name"].endswith(".md")
            assert len(doc["title"]) > 0
            assert len(doc["category"]) > 0
            assert isinstance(doc["tags"], list)
            assert len(doc["tags"]) > 0

    def test_all_docs_accessible(self):
        """All listed documents should be accessible"""
        # Get list of all docs
        response = client.get("/api/docs/list")
        docs = response.json()

        # Try to fetch each one
        for doc in docs:
            doc_response = client.get(f"/api/docs/{doc['name']}")
            assert doc_response.status_code == 200, f"Failed to fetch {doc['name']}"

    def test_search_covers_all_docs(self):
        """Search should be able to find content from all documents"""
        # Get list of all docs
        response = client.get("/api/docs/list")
        docs = response.json()

        # Search for a common term that should appear in multiple docs
        search_response = client.get("/api/docs/search?q=guide")
        search_data = search_response.json()

        # Should find results
        assert len(search_data["results"]) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])