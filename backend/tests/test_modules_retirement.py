"""Tests for Retirement Module API

Tests coverage for:
- Retirement dashboard endpoint
- Retirement summary endpoint
- Retirement pensions CRUD operations
- Retirement projections endpoint
- Monte Carlo simulation endpoint
"""

import pytest
from fastapi.testclient import TestClient
from datetime import date, datetime


class TestRetirementDashboard:
    """Test retirement dashboard endpoint"""

    def test_get_retirement_dashboard_empty(self, client: TestClient, auth_headers):
        """Test dashboard with no pensions"""
        response = client.get("/api/modules/retirement/dashboard", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()

        assert data["total_pension_value"] == 0
        assert data["pension_count"] == 0
        assert data["projected_annual_income"] == 0
        assert data["pensions"] == []

    def test_get_retirement_dashboard_with_pensions(self, client: TestClient, auth_headers):
        """Test dashboard with pension products"""
        # Create test pensions
        pensions = [
            {
                "name": "Workplace Pension",
                "product_type": "workplace_pension",
                "provider": "Example Pension Provider",
                "current_value": 150000,
                "annual_contribution": 12000,
                "employer_contribution": 4000
            },
            {
                "name": "Personal SIPP",
                "product_type": "sipp",
                "provider": "Example SIPP Provider",
                "current_value": 75000,
                "annual_contribution": 6000
            }
        ]

        for pension_data in pensions:
            response = client.post(
                "/api/modules/retirement/pensions",
                json=pension_data,
                headers=auth_headers
            )
            assert response.status_code == 200

        # Get dashboard
        response = client.get("/api/modules/retirement/dashboard", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()

        assert data["total_pension_value"] == 225000
        assert data["pension_count"] == 2
        assert data["projected_annual_income"] > 0  # Should calculate 4% withdrawal
        assert len(data["pensions"]) == 2

    def test_get_retirement_dashboard_retirement_readiness(self, client: TestClient, auth_headers):
        """Test retirement readiness calculation"""
        response = client.get("/api/modules/retirement/dashboard", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()

        assert "retirement_age" in data
        assert "years_to_retirement" in data
        assert "retirement_readiness" in data
        assert data["retirement_readiness"] in ["on_track", "ahead", "behind", "at_risk"]

    def test_get_retirement_dashboard_unauthorized(self, client: TestClient):
        """Test dashboard requires authentication"""
        response = client.get("/api/modules/retirement/dashboard")
        assert response.status_code == 401


class TestRetirementSummary:
    """Test retirement summary endpoint"""

    def test_get_retirement_summary(self, client: TestClient, auth_headers):
        """Test summary endpoint"""
        response = client.get("/api/modules/retirement/summary", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()

        assert "total_pension_value" in data
        assert "pension_count" in data
        assert "projected_income" in data
        assert "status" in data
        assert "message" in data
        assert data["status"] in ["on_track", "ahead", "behind", "at_risk"]


class TestRetirementPensionsCRUD:
    """Test retirement pensions CRUD operations"""

    def test_create_pension_product(self, client: TestClient, auth_headers):
        """Test creating a pension product"""
        pension_data = {
            "name": "New Workplace Pension",
            "product_type": "workplace_pension",
            "provider": "Test Pension Provider",
            "current_value": 100000,
            "annual_contribution": 10000,
            "employer_contribution": 3000,
            "start_date": "2020-01-01"
        }

        response = client.post(
            "/api/modules/retirement/pensions",
            json=pension_data,
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()

        assert "id" in data
        assert data["name"] == pension_data["name"]
        assert data["product_type"] == pension_data["product_type"]
        assert data["current_value"] == pension_data["current_value"]
        assert "message" in data

    def test_create_pension_validation_error(self, client: TestClient, auth_headers):
        """Test validation error for invalid data"""
        invalid_data = {
            "name": "",  # Empty name should fail
            "product_type": "workplace_pension",
            "current_value": -1000  # Negative value should fail
        }

        response = client.post(
            "/api/modules/retirement/pensions",
            json=invalid_data,
            headers=auth_headers
        )
        assert response.status_code == 422  # Validation error

    def test_list_pension_products(self, client: TestClient, auth_headers):
        """Test listing pension products"""
        # Create test pension
        pension_data = {
            "name": "Test Pension",
            "product_type": "sipp",
            "provider": "Test Provider",
            "current_value": 50000,
            "annual_contribution": 5000
        }
        client.post("/api/modules/retirement/pensions", json=pension_data, headers=auth_headers)

        # List pensions
        response = client.get("/api/modules/retirement/pensions", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()

        assert "total" in data
        assert "pensions" in data
        assert data["total"] > 0
        assert len(data["pensions"]) > 0

    def test_get_pension_product_by_id(self, client: TestClient, auth_headers):
        """Test getting specific pension by ID"""
        # Create pension
        pension_data = {
            "name": "Specific Pension",
            "product_type": "workplace_pension",
            "provider": "Test Provider",
            "current_value": 80000,
            "annual_contribution": 8000
        }
        create_response = client.post(
            "/api/modules/retirement/pensions",
            json=pension_data,
            headers=auth_headers
        )
        pension_id = create_response.json()["id"]

        # Get pension
        response = client.get(
            f"/api/modules/retirement/pensions/{pension_id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()

        assert data["id"] == pension_id
        assert data["name"] == pension_data["name"]
        assert data["product_type"] == pension_data["product_type"]

    def test_get_pension_product_not_found(self, client: TestClient, auth_headers):
        """Test 404 for non-existent pension"""
        response = client.get(
            "/api/modules/retirement/pensions/99999",
            headers=auth_headers
        )
        assert response.status_code == 404

    def test_update_pension_product(self, client: TestClient, auth_headers):
        """Test updating a pension product"""
        # Create pension
        pension_data = {
            "name": "Original Pension",
            "product_type": "sipp",
            "provider": "Original Provider",
            "current_value": 60000,
            "annual_contribution": 6000
        }
        create_response = client.post(
            "/api/modules/retirement/pensions",
            json=pension_data,
            headers=auth_headers
        )
        pension_id = create_response.json()["id"]

        # Update pension
        update_data = {
            "name": "Updated Pension",
            "current_value": 65000,
            "annual_contribution": 7000
        }
        response = client.put(
            f"/api/modules/retirement/pensions/{pension_id}",
            json=update_data,
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()

        assert data["name"] == update_data["name"]
        assert data["current_value"] == update_data["current_value"]

    def test_delete_pension_product(self, client: TestClient, auth_headers):
        """Test soft delete (archive) of pension product"""
        # Create pension
        pension_data = {
            "name": "Pension to Delete",
            "product_type": "workplace_pension",
            "provider": "Test Provider",
            "current_value": 40000,
            "annual_contribution": 4000
        }
        create_response = client.post(
            "/api/modules/retirement/pensions",
            json=pension_data,
            headers=auth_headers
        )
        pension_id = create_response.json()["id"]

        # Delete pension
        response = client.delete(
            f"/api/modules/retirement/pensions/{pension_id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()

        assert "message" in data
        assert data["id"] == pension_id


class TestRetirementProjections:
    """Test retirement projections endpoint"""

    def test_get_retirement_projections(self, client: TestClient, auth_headers):
        """Test projections endpoint"""
        response = client.get(
            "/api/modules/retirement/projections?retirement_age=65",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()

        assert "retirement_age" in data
        assert "years_to_retirement" in data
        assert "projected_pension_value" in data
        assert "projected_annual_income" in data
        assert "annual_drawdown" in data

    def test_retirement_projections_with_different_ages(self, client: TestClient, auth_headers):
        """Test projections with different retirement ages"""
        for age in [60, 65, 70]:
            response = client.get(
                f"/api/modules/retirement/projections?retirement_age={age}",
                headers=auth_headers
            )
            assert response.status_code == 200
            data = response.json()
            assert data["retirement_age"] == age


class TestMonteCarloSimulation:
    """Test Monte Carlo simulation endpoint"""

    def test_get_monte_carlo_simulation(self, client: TestClient, auth_headers):
        """Test Monte Carlo simulation endpoint"""
        response = client.get("/api/modules/retirement/monte-carlo", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()

        assert "simulations" in data
        assert "success_rate" in data
        assert "percentiles" in data
        assert "median_outcome" in data

    def test_monte_carlo_simulation_with_parameters(self, client: TestClient, auth_headers):
        """Test simulation with custom parameters"""
        response = client.get(
            "/api/modules/retirement/monte-carlo?simulations=1000&retirement_age=65",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()

        assert "simulations" in data
        assert "success_rate" in data
        # Success rate should be between 0 and 100
        assert 0 <= data["success_rate"] <= 100


class TestRetirementAuthorization:
    """Test authorization and security"""

    def test_all_endpoints_require_auth(self, client: TestClient):
        """Test that all endpoints require authentication"""
        endpoints = [
            "/api/modules/retirement/dashboard",
            "/api/modules/retirement/summary",
            "/api/modules/retirement/pensions",
            "/api/modules/retirement/projections?retirement_age=65",
            "/api/modules/retirement/monte-carlo"
        ]

        for endpoint in endpoints:
            response = client.get(endpoint)
            assert response.status_code == 401
