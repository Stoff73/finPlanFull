"""
Integration tests for the Financial Planning Application API.
Tests end-to-end workflows and API interactions.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import Base, engine
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import tempfile
import os

# Create a test database
test_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
TEST_DATABASE_URL = f"sqlite:///{test_db.name}"

@pytest.fixture(scope="module")
def client():
    """Create a test client with a fresh database."""
    # Create test engine and tables
    test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=test_engine)

    # Create test client
    with TestClient(app) as test_client:
        yield test_client

    # Cleanup
    os.unlink(test_db.name)


class TestUserWorkflow:
    """Test complete user registration and authentication workflow."""

    def test_complete_user_workflow(self, client):
        """Test user registration, login, and profile access."""
        # 1. Register a new user
        register_data = {
            "username": "integrationtest",
            "email": "integration@test.com",
            "password": "TestPassword123!",
            "full_name": "Integration Test User"
        }
        response = client.post("/api/auth/register", json=register_data)
        assert response.status_code == 200
        user_data = response.json()
        assert user_data["username"] == "integrationtest"
        assert user_data["email"] == "integration@test.com"

        # 2. Login with the new user
        login_data = {
            "username": "integrationtest",
            "password": "TestPassword123!"
        }
        response = client.post("/api/auth/token", data=login_data)
        assert response.status_code == 200
        token_data = response.json()
        assert "access_token" in token_data
        assert token_data["token_type"] == "bearer"

        # 3. Access protected endpoint
        headers = {"Authorization": f"Bearer {token_data['access_token']}"}
        response = client.get("/api/auth/me", headers=headers)
        assert response.status_code == 200
        profile = response.json()
        assert profile["username"] == "integrationtest"

        # 4. Create and save IHT profile
        iht_data = {
            "estate_value": 1000000,
            "assets": [
                {
                    "asset_type": "property",
                    "description": "Main residence",
                    "value": 750000,
                    "is_main_residence": True
                },
                {
                    "asset_type": "cash",
                    "description": "Savings",
                    "value": 250000
                }
            ],
            "gifts": [],
            "trusts": [],
            "marital_status": "married",
            "uk_resident": True
        }
        response = client.post("/api/iht/save-profile", json=iht_data, headers=headers)
        assert response.status_code == 200

        # 5. Retrieve saved IHT profile
        response = client.get("/api/iht/profile", headers=headers)
        assert response.status_code == 200
        saved_profile = response.json()
        assert saved_profile["estate_value"] == 1000000
        assert len(saved_profile["assets"]) == 2


class TestFinancialWorkflow:
    """Test financial statements and product management workflow."""

    @pytest.fixture(autouse=True)
    def setup(self, client):
        """Setup test user and authenticate."""
        # Register user
        register_data = {
            "username": "financetest",
            "email": "finance@test.com",
            "password": "FinanceTest123!",
            "full_name": "Finance Test User"
        }
        client.post("/api/auth/register", json=register_data)

        # Login
        login_data = {
            "username": "financetest",
            "password": "FinanceTest123!"
        }
        response = client.post("/api/auth/token", data=login_data)
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}

    def test_financial_statements_workflow(self, client):
        """Test creating and retrieving financial statements."""
        # 1. Create balance sheet
        balance_sheet_data = {
            "statement_date": "2024-01-01",
            "cash": 50000,
            "investments": 200000,
            "property": 500000,
            "other_assets": 10000,
            "total_assets": 760000,
            "mortgages": 200000,
            "loans": 10000,
            "credit_cards": 5000,
            "other_liabilities": 0,
            "total_liabilities": 215000,
            "net_worth": 545000
        }
        response = client.post("/api/financial/balance-sheet",
                              json=balance_sheet_data,
                              headers=self.headers)
        assert response.status_code == 200

        # 2. Create P&L statement
        pl_data = {
            "statement_date": "2024-01-01",
            "period_months": 12,
            "salary": 80000,
            "bonuses": 10000,
            "investment_income": 5000,
            "rental_income": 0,
            "other_income": 0,
            "total_income": 95000,
            "mortgage_payments": 24000,
            "utilities": 3000,
            "insurance": 2000,
            "groceries": 6000,
            "transport": 4000,
            "entertainment": 3000,
            "other_expenses": 8000,
            "total_expenses": 50000,
            "net_income": 45000
        }
        response = client.post("/api/financial/profit-loss",
                              json=pl_data,
                              headers=self.headers)
        assert response.status_code == 200

        # 3. Get financial summary
        response = client.get("/api/financial/summary", headers=self.headers)
        assert response.status_code == 200
        summary = response.json()
        assert summary["balance_sheet"]["net_worth"] == 545000
        assert summary["profit_loss"]["net_income"] == 45000
        assert "metrics" in summary

    def test_product_management_workflow(self, client):
        """Test creating and managing products."""
        # 1. Create pension
        pension_data = {
            "product_name": "Workplace Pension",
            "provider": "Aviva",
            "current_value": 150000,
            "monthly_contribution": 500,
            "pension_type": "defined_contribution",
            "employer_contribution": 250,
            "retirement_age": 65
        }
        response = client.post("/api/products/pensions",
                              json=pension_data,
                              headers=self.headers)
        assert response.status_code == 200
        pension = response.json()
        pension_id = pension["id"]

        # 2. Create investment
        investment_data = {
            "product_name": "ISA Portfolio",
            "provider": "Hargreaves Lansdown",
            "current_value": 50000,
            "monthly_contribution": 200,
            "investment_type": "isa",
            "risk_level": "medium",
            "asset_allocation": {
                "equities": 60,
                "bonds": 30,
                "cash": 10
            }
        }
        response = client.post("/api/products/investments",
                              json=investment_data,
                              headers=self.headers)
        assert response.status_code == 200

        # 3. Get portfolio summary
        response = client.get("/api/products/portfolio/summary", headers=self.headers)
        assert response.status_code == 200
        portfolio = response.json()
        assert portfolio["total_value"] == 200000
        assert portfolio["total_monthly_contributions"] == 950

        # 4. Get retirement projection
        response = client.get("/api/products/retirement/projection?retirement_age=65&expected_return=5.0",
                            headers=self.headers)
        assert response.status_code == 200
        projection = response.json()
        assert "projected_value" in projection
        assert "years_to_retirement" in projection

        # 5. Delete pension
        response = client.delete(f"/api/products/{pension_id}", headers=self.headers)
        assert response.status_code == 200


class TestChatWorkflow:
    """Test AI chat functionality workflow."""

    @pytest.fixture(autouse=True)
    def setup(self, client):
        """Setup test user and authenticate."""
        # Register user
        register_data = {
            "username": "chattest",
            "email": "chat@test.com",
            "password": "ChatTest123!",
            "full_name": "Chat Test User"
        }
        client.post("/api/auth/register", json=register_data)

        # Login
        login_data = {
            "username": "chattest",
            "password": "ChatTest123!"
        }
        response = client.post("/api/auth/token", data=login_data)
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}

    def test_chat_conversation_workflow(self, client):
        """Test creating chat sessions and messages."""
        # 1. Send initial message (creates session automatically)
        message_data = {
            "message": "What is inheritance tax?"
        }
        response = client.post("/api/chat/send",
                              json=message_data,
                              headers=self.headers)
        assert response.status_code == 200
        chat_response = response.json()
        assert "response" in chat_response
        assert "session_id" in chat_response
        session_id = chat_response["session_id"]

        # 2. Continue conversation
        followup_data = {
            "message": "What are the current thresholds?",
            "session_id": session_id
        }
        response = client.post("/api/chat/send",
                              json=followup_data,
                              headers=self.headers)
        assert response.status_code == 200

        # 3. Get chat history
        response = client.get(f"/api/chat/history/{session_id}",
                            headers=self.headers)
        assert response.status_code == 200
        history = response.json()
        assert len(history) >= 2  # At least 2 messages in conversation

        # 4. Get all sessions
        response = client.get("/api/chat/sessions", headers=self.headers)
        assert response.status_code == 200
        sessions = response.json()
        assert len(sessions) >= 1


class TestExportWorkflow:
    """Test data export functionality workflow."""

    @pytest.fixture(autouse=True)
    def setup(self, client):
        """Setup test user with data."""
        # Register user
        register_data = {
            "username": "exporttest",
            "email": "export@test.com",
            "password": "ExportTest123!",
            "full_name": "Export Test User"
        }
        client.post("/api/auth/register", json=register_data)

        # Login
        login_data = {
            "username": "exporttest",
            "password": "ExportTest123!"
        }
        response = client.post("/api/auth/token", data=login_data)
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}

        # Add some test data
        balance_sheet_data = {
            "statement_date": "2024-01-01",
            "cash": 100000,
            "investments": 300000,
            "property": 600000,
            "other_assets": 0,
            "total_assets": 1000000,
            "mortgages": 300000,
            "loans": 0,
            "credit_cards": 0,
            "other_liabilities": 0,
            "total_liabilities": 300000,
            "net_worth": 700000
        }
        client.post("/api/financial/balance-sheet",
                   json=balance_sheet_data,
                   headers=self.headers)

    def test_export_formats(self, client):
        """Test exporting data in different formats."""
        # 1. Export financial summary as JSON
        response = client.get("/api/export/financial-summary?format=json",
                            headers=self.headers)
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"
        data = response.json()
        assert "financial_summary" in data

        # 2. Export financial summary as CSV
        response = client.get("/api/export/financial-summary?format=csv",
                            headers=self.headers)
        assert response.status_code == 200
        assert "text/csv" in response.headers["content-type"]

        # 3. Export financial summary as Excel
        response = client.get("/api/export/financial-summary?format=excel",
                            headers=self.headers)
        assert response.status_code == 200
        assert "spreadsheet" in response.headers["content-type"]

        # 4. Export IHT report as PDF (if IHT profile exists)
        iht_data = {
            "estate_value": 1000000,
            "assets": [
                {
                    "asset_type": "property",
                    "description": "Home",
                    "value": 600000,
                    "is_main_residence": True
                }
            ],
            "gifts": [],
            "trusts": [],
            "marital_status": "married",
            "uk_resident": True
        }
        client.post("/api/iht/save-profile", json=iht_data, headers=self.headers)

        response = client.get("/api/export/iht-report?format=pdf",
                            headers=self.headers)
        assert response.status_code == 200
        assert "pdf" in response.headers["content-type"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])