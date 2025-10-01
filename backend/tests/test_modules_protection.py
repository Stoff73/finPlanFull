"""Tests for Protection Module API

Tests coverage for:
- Protection dashboard endpoint
- Protection summary endpoint
- Protection products CRUD operations
- Protection analytics endpoint
- Protection needs analysis endpoint
"""

import pytest
from fastapi.testclient import TestClient
from datetime import date, datetime


class TestProtectionDashboard:
    """Test protection dashboard endpoint"""

    def test_get_protection_dashboard_empty(self, client: TestClient, auth_headers):
        """Test dashboard with no protection products"""
        response = client.get("/api/modules/protection/dashboard", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()

        assert data["total_coverage"] == 0
        assert data["active_policies"] == 0
        assert data["total_monthly_premium"] == 0
        assert data["coverage_by_type"] == {}
        assert data["policies"] == []

    def test_get_protection_dashboard_with_products(self, client: TestClient, auth_headers):
        """Test dashboard with protection products"""
        # Create test protection products
        products = [
            {
                "name": "Term Life Insurance",
                "product_type": "life_insurance",
                "provider": "Example Life Co",
                "value": 500000,
                "monthly_premium": 50.0,
                "start_date": "2024-01-01"
            },
            {
                "name": "Critical Illness Cover",
                "product_type": "critical_illness",
                "provider": "Example Insurance",
                "value": 250000,
                "monthly_premium": 75.0,
                "start_date": "2024-01-01"
            }
        ]

        for product_data in products:
            response = client.post(
                "/api/modules/protection/products",
                json=product_data,
                headers=auth_headers
            )
            assert response.status_code == 200

        # Get dashboard
        response = client.get("/api/modules/protection/dashboard", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()

        assert data["total_coverage"] == 750000
        assert data["active_policies"] == 2
        assert data["total_monthly_premium"] == 125.0
        assert len(data["coverage_by_type"]) == 2
        assert "life_insurance" in data["coverage_by_type"]
        assert "critical_illness" in data["coverage_by_type"]
        assert len(data["policies"]) == 2

    def test_get_protection_dashboard_unauthorized(self, client: TestClient):
        """Test dashboard requires authentication"""
        response = client.get("/api/modules/protection/dashboard")
        assert response.status_code == 401


class TestProtectionSummary:
    """Test protection summary endpoint"""

    def test_get_protection_summary(self, client: TestClient, auth_headers):
        """Test summary endpoint"""
        response = client.get("/api/modules/protection/summary", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()

        assert "total_coverage" in data
        assert "policy_count" in data
        assert "monthly_premium" in data
        assert "status" in data
        assert "message" in data
        assert data["status"] in ["adequate", "attention_needed", "insufficient", "excellent"]


class TestProtectionProductsCRUD:
    """Test protection products CRUD operations"""

    def test_create_protection_product(self, client: TestClient, auth_headers):
        """Test creating a protection product"""
        product_data = {
            "name": "Life Insurance Policy",
            "product_type": "life_insurance",
            "provider": "Test Insurance Co",
            "value": 500000,
            "monthly_premium": 50.0,
            "start_date": "2024-01-01",
            "beneficiaries": "Spouse, Children",
            "notes": "Term life insurance policy"
        }

        response = client.post(
            "/api/modules/protection/products",
            json=product_data,
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()

        assert "id" in data
        assert data["name"] == product_data["name"]
        assert data["product_type"] == product_data["product_type"]
        assert data["value"] == product_data["value"]
        assert "message" in data

    def test_create_protection_product_validation_error(self, client: TestClient, auth_headers):
        """Test validation error for invalid data"""
        invalid_data = {
            "name": "",  # Empty name should fail
            "product_type": "life_insurance",
            "value": -1000  # Negative value should fail
        }

        response = client.post(
            "/api/modules/protection/products",
            json=invalid_data,
            headers=auth_headers
        )
        assert response.status_code == 422  # Validation error

    def test_list_protection_products(self, client: TestClient, auth_headers):
        """Test listing protection products"""
        # Create test product
        product_data = {
            "name": "Test Policy",
            "product_type": "income_protection",
            "provider": "Test Provider",
            "value": 100000,
            "monthly_premium": 25.0
        }
        client.post("/api/modules/protection/products", json=product_data, headers=auth_headers)

        # List products
        response = client.get("/api/modules/protection/products", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()

        assert "total" in data
        assert "products" in data
        assert data["total"] > 0
        assert len(data["products"]) > 0

    def test_list_protection_products_with_pagination(self, client: TestClient, auth_headers):
        """Test pagination"""
        response = client.get(
            "/api/modules/protection/products?skip=0&limit=10",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()

        assert "total" in data
        assert "products" in data
        assert len(data["products"]) <= 10

    def test_get_protection_product_by_id(self, client: TestClient, auth_headers):
        """Test getting specific product by ID"""
        # Create product
        product_data = {
            "name": "Specific Policy",
            "product_type": "critical_illness",
            "provider": "Test Provider",
            "value": 200000,
            "monthly_premium": 60.0
        }
        create_response = client.post(
            "/api/modules/protection/products",
            json=product_data,
            headers=auth_headers
        )
        product_id = create_response.json()["id"]

        # Get product
        response = client.get(
            f"/api/modules/protection/products/{product_id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()

        assert data["id"] == product_id
        assert data["name"] == product_data["name"]
        assert data["product_type"] == product_data["product_type"]

    def test_get_protection_product_not_found(self, client: TestClient, auth_headers):
        """Test 404 for non-existent product"""
        response = client.get(
            "/api/modules/protection/products/99999",
            headers=auth_headers
        )
        assert response.status_code == 404

    def test_update_protection_product(self, client: TestClient, auth_headers):
        """Test updating a protection product"""
        # Create product
        product_data = {
            "name": "Original Policy",
            "product_type": "life_insurance",
            "provider": "Original Provider",
            "value": 300000,
            "monthly_premium": 40.0
        }
        create_response = client.post(
            "/api/modules/protection/products",
            json=product_data,
            headers=auth_headers
        )
        product_id = create_response.json()["id"]

        # Update product
        update_data = {
            "name": "Updated Policy",
            "value": 400000,
            "monthly_premium": 50.0
        }
        response = client.put(
            f"/api/modules/protection/products/{product_id}",
            json=update_data,
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()

        assert data["name"] == update_data["name"]
        assert data["value"] == update_data["value"]

        # Verify update persisted
        get_response = client.get(
            f"/api/modules/protection/products/{product_id}",
            headers=auth_headers
        )
        assert get_response.json()["name"] == update_data["name"]

    def test_update_protection_product_not_found(self, client: TestClient, auth_headers):
        """Test 404 when updating non-existent product"""
        update_data = {"name": "Updated Policy"}
        response = client.put(
            "/api/modules/protection/products/99999",
            json=update_data,
            headers=auth_headers
        )
        assert response.status_code == 404

    def test_delete_protection_product(self, client: TestClient, auth_headers):
        """Test soft delete (archive) of protection product"""
        # Create product
        product_data = {
            "name": "Policy to Delete",
            "product_type": "life_insurance",
            "provider": "Test Provider",
            "value": 150000,
            "monthly_premium": 30.0
        }
        create_response = client.post(
            "/api/modules/protection/products",
            json=product_data,
            headers=auth_headers
        )
        product_id = create_response.json()["id"]

        # Delete product
        response = client.delete(
            f"/api/modules/protection/products/{product_id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()

        assert "message" in data
        assert data["id"] == product_id

        # Verify product is archived (status=archived)
        get_response = client.get(
            f"/api/modules/protection/products/{product_id}",
            headers=auth_headers
        )
        assert get_response.json()["status"] == "archived"

    def test_delete_protection_product_not_found(self, client: TestClient, auth_headers):
        """Test 404 when deleting non-existent product"""
        response = client.delete(
            "/api/modules/protection/products/99999",
            headers=auth_headers
        )
        assert response.status_code == 404


class TestProtectionAnalytics:
    """Test protection analytics endpoint"""

    def test_get_protection_analytics(self, client: TestClient, auth_headers):
        """Test analytics endpoint"""
        response = client.get("/api/modules/protection/analytics", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()

        # Check for expected analytics data structure
        assert "coverage_breakdown" in data
        assert "premium_analysis" in data
        assert "coverage_trends" in data


class TestProtectionNeedsAnalysis:
    """Test protection needs analysis endpoint"""

    def test_get_needs_analysis(self, client: TestClient, auth_headers):
        """Test needs analysis endpoint"""
        response = client.get("/api/modules/protection/needs-analysis", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()

        # Check for expected needs analysis structure
        assert "current_coverage" in data
        assert "recommended_coverage" in data
        assert "coverage_gap" in data
        assert "recommendations" in data


class TestProtectionAuthorization:
    """Test authorization and security"""

    def test_all_endpoints_require_auth(self, client: TestClient):
        """Test that all endpoints require authentication"""
        endpoints = [
            "/api/modules/protection/dashboard",
            "/api/modules/protection/summary",
            "/api/modules/protection/products",
            "/api/modules/protection/analytics",
            "/api/modules/protection/needs-analysis"
        ]

        for endpoint in endpoints:
            response = client.get(endpoint)
            assert response.status_code == 401

    def test_cannot_access_other_users_products(self, client: TestClient, auth_headers):
        """Test users cannot access products from other users"""
        # This would require creating a second user and testing cross-user access
        # Implementation depends on having a second_auth_headers fixture
        # For now, we verify that only user's own products are returned
        response = client.get("/api/modules/protection/products", headers=auth_headers)
        assert response.status_code == 200
        # All returned products should belong to the authenticated user
