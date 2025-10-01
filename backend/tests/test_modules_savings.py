"""Tests for Savings Module API

Tests coverage for:
- Savings dashboard endpoint
- Savings summary endpoint
- Savings accounts CRUD operations
- Savings analytics endpoint
- Savings goals endpoint
"""

import pytest
from fastapi.testclient import TestClient
from datetime import date, datetime


class TestSavingsDashboard:
    """Test savings dashboard endpoint"""

    def test_get_savings_dashboard_empty(self, client: TestClient, auth_headers):
        """Test dashboard with no savings accounts"""
        response = client.get("/api/modules/savings/dashboard", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()

        assert data["total_balance"] == 0
        assert data["account_count"] == 0
        assert "emergency_fund" in data
        assert data["emergency_fund"]["status"] in ["excellent", "adequate", "needs_improvement", "insufficient"]
        assert data["balance_by_type"] == {}
        assert data["accounts"] == []

    def test_get_savings_dashboard_with_accounts(self, client: TestClient, auth_headers):
        """Test dashboard with savings accounts"""
        # Create test savings accounts
        accounts = [
            {
                "name": "Emergency Fund",
                "account_type": "savings_account",
                "provider": "Example Bank",
                "balance": 15000,
                "interest_rate": 2.5,
                "account_number": "****1234"
            },
            {
                "name": "ISA Account",
                "account_type": "isa",
                "provider": "Example Bank",
                "balance": 10000,
                "interest_rate": 3.0,
                "account_number": "****5678"
            }
        ]

        for account_data in accounts:
            response = client.post(
                "/api/modules/savings/accounts",
                json=account_data,
                headers=auth_headers
            )
            assert response.status_code == 200

        # Get dashboard
        response = client.get("/api/modules/savings/dashboard", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()

        assert data["total_balance"] == 25000
        assert data["account_count"] == 2
        assert "emergency_fund" in data
        assert data["emergency_fund"]["months_covered"] > 0
        assert len(data["balance_by_type"]) == 2
        assert "savings_account" in data["balance_by_type"]
        assert "isa" in data["balance_by_type"]
        assert len(data["accounts"]) == 2

    def test_get_savings_dashboard_emergency_fund_status(self, client: TestClient, auth_headers):
        """Test emergency fund status calculation"""
        response = client.get("/api/modules/savings/dashboard", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()

        emergency_fund = data["emergency_fund"]
        assert "months_covered" in emergency_fund
        assert "status" in emergency_fund
        assert "target_months" in emergency_fund
        assert "amount" in emergency_fund
        assert "target_amount" in emergency_fund
        assert emergency_fund["target_months"] == 6

    def test_get_savings_dashboard_unauthorized(self, client: TestClient):
        """Test dashboard requires authentication"""
        response = client.get("/api/modules/savings/dashboard")
        assert response.status_code == 401


class TestSavingsSummary:
    """Test savings summary endpoint"""

    def test_get_savings_summary(self, client: TestClient, auth_headers):
        """Test summary endpoint"""
        response = client.get("/api/modules/savings/summary", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()

        assert "total_balance" in data
        assert "account_count" in data
        assert "emergency_fund_months" in data
        assert "status" in data
        assert "message" in data
        assert data["status"] in ["excellent", "adequate", "attention_needed", "insufficient"]

    def test_savings_summary_message_format(self, client: TestClient, auth_headers):
        """Test that summary message follows narrative style"""
        response = client.get("/api/modules/savings/summary", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()

        # Message should follow STYLEGUIDE.md narrative approach
        message = data["message"]
        assert isinstance(message, str)
        assert len(message) > 0
        # Should use conversational language like "you", "your"


class TestSavingsAccountsCRUD:
    """Test savings accounts CRUD operations"""

    def test_create_savings_account(self, client: TestClient, auth_headers):
        """Test creating a savings account"""
        account_data = {
            "name": "High Interest Savings",
            "account_type": "savings_account",
            "provider": "Test Bank",
            "balance": 5000,
            "interest_rate": 4.5,
            "account_number": "****9999"
        }

        response = client.post(
            "/api/modules/savings/accounts",
            json=account_data,
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()

        assert "id" in data
        assert data["name"] == account_data["name"]
        assert data["account_type"] == account_data["account_type"]
        assert data["balance"] == account_data["balance"]
        assert "message" in data

    def test_create_savings_account_validation_error(self, client: TestClient, auth_headers):
        """Test validation error for invalid data"""
        invalid_data = {
            "name": "",  # Empty name should fail
            "account_type": "savings_account",
            "balance": -1000  # Negative balance should fail
        }

        response = client.post(
            "/api/modules/savings/accounts",
            json=invalid_data,
            headers=auth_headers
        )
        assert response.status_code == 422  # Validation error

    def test_list_savings_accounts(self, client: TestClient, auth_headers):
        """Test listing savings accounts"""
        # Create test account
        account_data = {
            "name": "Test Savings",
            "account_type": "savings_account",
            "provider": "Test Bank",
            "balance": 10000,
            "interest_rate": 2.0
        }
        client.post("/api/modules/savings/accounts", json=account_data, headers=auth_headers)

        # List accounts
        response = client.get("/api/modules/savings/accounts", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()

        assert "total" in data
        assert "accounts" in data
        assert data["total"] > 0
        assert len(data["accounts"]) > 0

    def test_list_savings_accounts_with_pagination(self, client: TestClient, auth_headers):
        """Test pagination"""
        response = client.get(
            "/api/modules/savings/accounts?skip=0&limit=10",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()

        assert "total" in data
        assert "accounts" in data
        assert len(data["accounts"]) <= 10

    def test_get_savings_account_by_id(self, client: TestClient, auth_headers):
        """Test getting specific account by ID"""
        # Create account
        account_data = {
            "name": "Specific Savings Account",
            "account_type": "isa",
            "provider": "Test Bank",
            "balance": 8000,
            "interest_rate": 3.5
        }
        create_response = client.post(
            "/api/modules/savings/accounts",
            json=account_data,
            headers=auth_headers
        )
        account_id = create_response.json()["id"]

        # Get account
        response = client.get(
            f"/api/modules/savings/accounts/{account_id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()

        assert data["id"] == account_id
        assert data["name"] == account_data["name"]
        assert data["account_type"] == account_data["account_type"]

    def test_get_savings_account_not_found(self, client: TestClient, auth_headers):
        """Test 404 for non-existent account"""
        response = client.get(
            "/api/modules/savings/accounts/99999",
            headers=auth_headers
        )
        assert response.status_code == 404

    def test_update_savings_account(self, client: TestClient, auth_headers):
        """Test updating a savings account"""
        # Create account
        account_data = {
            "name": "Original Account",
            "account_type": "savings_account",
            "provider": "Original Bank",
            "balance": 5000,
            "interest_rate": 2.0
        }
        create_response = client.post(
            "/api/modules/savings/accounts",
            json=account_data,
            headers=auth_headers
        )
        account_id = create_response.json()["id"]

        # Update account
        update_data = {
            "name": "Updated Account",
            "balance": 6000,
            "interest_rate": 2.5
        }
        response = client.put(
            f"/api/modules/savings/accounts/{account_id}",
            json=update_data,
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()

        assert data["name"] == update_data["name"]
        assert data["balance"] == update_data["balance"]

        # Verify update persisted
        get_response = client.get(
            f"/api/modules/savings/accounts/{account_id}",
            headers=auth_headers
        )
        assert get_response.json()["name"] == update_data["name"]

    def test_update_savings_account_not_found(self, client: TestClient, auth_headers):
        """Test 404 when updating non-existent account"""
        update_data = {"name": "Updated Account"}
        response = client.put(
            "/api/modules/savings/accounts/99999",
            json=update_data,
            headers=auth_headers
        )
        assert response.status_code == 404

    def test_delete_savings_account(self, client: TestClient, auth_headers):
        """Test soft delete (archive) of savings account"""
        # Create account
        account_data = {
            "name": "Account to Delete",
            "account_type": "savings_account",
            "provider": "Test Bank",
            "balance": 3000,
            "interest_rate": 1.5
        }
        create_response = client.post(
            "/api/modules/savings/accounts",
            json=account_data,
            headers=auth_headers
        )
        account_id = create_response.json()["id"]

        # Delete account
        response = client.delete(
            f"/api/modules/savings/accounts/{account_id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()

        assert "message" in data
        assert data["id"] == account_id

        # Verify account is archived
        get_response = client.get(
            f"/api/modules/savings/accounts/{account_id}",
            headers=auth_headers
        )
        assert get_response.json()["status"] == "archived"

    def test_delete_savings_account_not_found(self, client: TestClient, auth_headers):
        """Test 404 when deleting non-existent account"""
        response = client.delete(
            "/api/modules/savings/accounts/99999",
            headers=auth_headers
        )
        assert response.status_code == 404


class TestSavingsAnalytics:
    """Test savings analytics endpoint"""

    def test_get_savings_analytics(self, client: TestClient, auth_headers):
        """Test analytics endpoint"""
        response = client.get("/api/modules/savings/analytics", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()

        # Check for expected analytics data structure
        assert "balance_trends" in data
        assert "interest_analysis" in data
        assert "savings_rate" in data


class TestSavingsGoals:
    """Test savings goals endpoint"""

    def test_get_savings_goals(self, client: TestClient, auth_headers):
        """Test goals endpoint"""
        response = client.get("/api/modules/savings/goals", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()

        assert "goals" in data

    def test_create_savings_goal(self, client: TestClient, auth_headers):
        """Test creating a savings goal"""
        goal_data = {
            "name": "Emergency Fund",
            "target_amount": 18000,
            "target_date": "2025-12-31",
            "monthly_contribution": 500
        }

        response = client.post(
            "/api/modules/savings/goals",
            json=goal_data,
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()

        assert "id" in data
        assert data["name"] == goal_data["name"]
        assert data["target_amount"] == goal_data["target_amount"]


class TestSavingsAuthorization:
    """Test authorization and security"""

    def test_all_endpoints_require_auth(self, client: TestClient):
        """Test that all endpoints require authentication"""
        endpoints = [
            "/api/modules/savings/dashboard",
            "/api/modules/savings/summary",
            "/api/modules/savings/accounts",
            "/api/modules/savings/analytics",
            "/api/modules/savings/goals"
        ]

        for endpoint in endpoints:
            response = client.get(endpoint)
            assert response.status_code == 401

    def test_cannot_access_other_users_accounts(self, client: TestClient, auth_headers):
        """Test users cannot access accounts from other users"""
        response = client.get("/api/modules/savings/accounts", headers=auth_headers)
        assert response.status_code == 200
        # All returned accounts should belong to the authenticated user
