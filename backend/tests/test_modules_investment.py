"""Tests for Investment Module API

Tests coverage for:
- Investment dashboard endpoint
- Investment summary endpoint
- Investment portfolio CRUD operations
- Investment analytics endpoint
- Investment rebalancing endpoint
"""

import pytest
from fastapi.testclient import TestClient
from datetime import date, datetime


class TestInvestmentDashboard:
    """Test investment dashboard endpoint"""

    def test_get_investment_dashboard_empty(self, client: TestClient, auth_headers):
        """Test dashboard with no investments"""
        response = client.get("/api/modules/investment/dashboard", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()

        assert data["total_value"] == 0
        assert data["total_contributions"] == 0
        assert data["total_gain_loss"] == 0
        assert data["account_count"] == 0
        assert data["asset_allocation"] == []
        assert data["holdings"] == []

    def test_get_investment_dashboard_with_investments(self, client: TestClient, auth_headers):
        """Test dashboard with investment holdings"""
        # Create test investments
        investments = [
            {
                "name": "FTSE 100 Index Fund",
                "product_type": "etf",
                "provider": "Example Broker",
                "current_value": 15000,
                "total_contributions": 12000,
                "units": 100,
                "purchase_price": 120
            },
            {
                "name": "Tech Stock Portfolio",
                "product_type": "stocks",
                "provider": "Example Broker",
                "current_value": 25000,
                "total_contributions": 20000,
                "units": 50,
                "purchase_price": 400
            }
        ]

        for investment_data in investments:
            response = client.post(
                "/api/modules/investment/portfolio",
                json=investment_data,
                headers=auth_headers
            )
            assert response.status_code == 200

        # Get dashboard
        response = client.get("/api/modules/investment/dashboard", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()

        assert data["total_value"] == 40000
        assert data["total_contributions"] == 32000
        assert data["total_gain_loss"] == 8000  # 40000 - 32000
        assert data["account_count"] == 2
        assert len(data["asset_allocation"]) > 0
        assert len(data["holdings"]) == 2

    def test_get_investment_dashboard_unauthorized(self, client: TestClient):
        """Test dashboard requires authentication"""
        response = client.get("/api/modules/investment/dashboard")
        assert response.status_code == 401


class TestInvestmentSummary:
    """Test investment summary endpoint"""

    def test_get_investment_summary(self, client: TestClient, auth_headers):
        """Test summary endpoint"""
        response = client.get("/api/modules/investment/summary", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()

        assert "total_value" in data
        assert "gain_loss" in data
        assert "gain_loss_percentage" in data
        assert "status" in data
        assert "message" in data
        assert data["status"] in ["growing", "stable", "attention_needed", "negative"]


class TestInvestmentPortfolioCRUD:
    """Test investment portfolio CRUD operations"""

    def test_create_investment_product(self, client: TestClient, auth_headers):
        """Test creating an investment product"""
        product_data = {
            "name": "Global Equity Fund",
            "product_type": "mutual_fund",
            "provider": "Test Asset Manager",
            "current_value": 10000,
            "total_contributions": 9000,
            "units": 1000,
            "purchase_price": 9.0,
            "annual_dividend": 200
        }

        response = client.post(
            "/api/modules/investment/portfolio",
            json=product_data,
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()

        assert "id" in data
        assert data["name"] == product_data["name"]
        assert data["product_type"] == product_data["product_type"]
        assert data["current_value"] == product_data["current_value"]
        assert "message" in data

    def test_create_investment_validation_error(self, client: TestClient, auth_headers):
        """Test validation error for invalid data"""
        invalid_data = {
            "name": "",  # Empty name should fail
            "product_type": "stocks",
            "current_value": -1000  # Negative value should fail
        }

        response = client.post(
            "/api/modules/investment/portfolio",
            json=invalid_data,
            headers=auth_headers
        )
        assert response.status_code == 422  # Validation error

    def test_list_investment_products(self, client: TestClient, auth_headers):
        """Test listing investment products"""
        # Create test investment
        product_data = {
            "name": "Test Investment",
            "product_type": "etf",
            "provider": "Test Broker",
            "current_value": 5000,
            "total_contributions": 4500
        }
        client.post("/api/modules/investment/portfolio", json=product_data, headers=auth_headers)

        # List products
        response = client.get("/api/modules/investment/portfolio", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()

        assert "total" in data
        assert "products" in data
        assert data["total"] > 0
        assert len(data["products"]) > 0

    def test_get_investment_product_by_id(self, client: TestClient, auth_headers):
        """Test getting specific investment by ID"""
        # Create investment
        product_data = {
            "name": "Specific Investment",
            "product_type": "stocks",
            "provider": "Test Broker",
            "current_value": 8000,
            "total_contributions": 7000
        }
        create_response = client.post(
            "/api/modules/investment/portfolio",
            json=product_data,
            headers=auth_headers
        )
        product_id = create_response.json()["id"]

        # Get investment
        response = client.get(
            f"/api/modules/investment/portfolio/{product_id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()

        assert data["id"] == product_id
        assert data["name"] == product_data["name"]
        assert data["product_type"] == product_data["product_type"]

    def test_get_investment_product_not_found(self, client: TestClient, auth_headers):
        """Test 404 for non-existent investment"""
        response = client.get(
            "/api/modules/investment/portfolio/99999",
            headers=auth_headers
        )
        assert response.status_code == 404

    def test_update_investment_product(self, client: TestClient, auth_headers):
        """Test updating an investment product"""
        # Create investment
        product_data = {
            "name": "Original Investment",
            "product_type": "etf",
            "provider": "Original Broker",
            "current_value": 6000,
            "total_contributions": 5500
        }
        create_response = client.post(
            "/api/modules/investment/portfolio",
            json=product_data,
            headers=auth_headers
        )
        product_id = create_response.json()["id"]

        # Update investment
        update_data = {
            "name": "Updated Investment",
            "current_value": 6500
        }
        response = client.put(
            f"/api/modules/investment/portfolio/{product_id}",
            json=update_data,
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()

        assert data["name"] == update_data["name"]
        assert data["current_value"] == update_data["current_value"]

    def test_delete_investment_product(self, client: TestClient, auth_headers):
        """Test soft delete (archive) of investment product"""
        # Create investment
        product_data = {
            "name": "Investment to Delete",
            "product_type": "stocks",
            "provider": "Test Broker",
            "current_value": 3000,
            "total_contributions": 3000
        }
        create_response = client.post(
            "/api/modules/investment/portfolio",
            json=product_data,
            headers=auth_headers
        )
        product_id = create_response.json()["id"]

        # Delete investment
        response = client.delete(
            f"/api/modules/investment/portfolio/{product_id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()

        assert "message" in data
        assert data["id"] == product_id


class TestInvestmentAnalytics:
    """Test investment analytics endpoint"""

    def test_get_investment_analytics(self, client: TestClient, auth_headers):
        """Test analytics endpoint"""
        response = client.get("/api/modules/investment/analytics", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()

        # Check for expected analytics data structure
        assert "performance" in data
        assert "asset_allocation" in data
        assert "risk_metrics" in data
        assert "diversification" in data
        assert "income_analysis" in data
        assert "recommendations" in data

    def test_investment_analytics_performance_metrics(self, client: TestClient, auth_headers):
        """Test performance metrics structure"""
        response = client.get("/api/modules/investment/analytics", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()

        performance = data["performance"]
        assert "total_value" in performance
        assert "total_return" in performance
        assert "contributions" in performance
        assert "total_yield" in performance


class TestInvestmentRebalancing:
    """Test investment rebalancing endpoint"""

    def test_get_rebalancing_analysis(self, client: TestClient, auth_headers):
        """Test rebalancing analysis endpoint"""
        response = client.get("/api/modules/investment/rebalancing", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()

        assert "current_allocation" in data
        assert "target_allocation" in data
        assert "rebalancing_recommendations" in data
        assert "last_rebalanced" in data

    def test_rebalancing_recommendations(self, client: TestClient, auth_headers):
        """Test rebalancing recommendations structure"""
        response = client.get("/api/modules/investment/rebalancing", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()

        if len(data["rebalancing_recommendations"]) > 0:
            recommendation = data["rebalancing_recommendations"][0]
            assert "asset_class" in recommendation
            assert "action" in recommendation
            assert "amount" in recommendation


class TestInvestmentAuthorization:
    """Test authorization and security"""

    def test_all_endpoints_require_auth(self, client: TestClient):
        """Test that all endpoints require authentication"""
        endpoints = [
            "/api/modules/investment/dashboard",
            "/api/modules/investment/summary",
            "/api/modules/investment/portfolio",
            "/api/modules/investment/analytics",
            "/api/modules/investment/rebalancing"
        ]

        for endpoint in endpoints:
            response = client.get(endpoint)
            assert response.status_code == 401
