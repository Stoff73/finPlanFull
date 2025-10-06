"""Tests for IHT Module API

Tests coverage for:
- IHT dashboard endpoint
- IHT summary endpoint
- IHT calculator endpoint
- IHT gifts CRUD operations
- IHT trusts CRUD operations
"""

import pytest
from fastapi.testclient import TestClient
from datetime import date, datetime, timedelta


class TestIHTDashboard:
    """Test IHT dashboard endpoint"""

    def test_get_iht_dashboard_empty(self, client: TestClient, auth_headers):
        """Test dashboard with no IHT data"""
        response = client.get("/api/modules/iht/dashboard", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()

        assert "estate_value" in data
        assert "iht_liability" in data
        assert "nil_rate_band_available" in data
        assert "gifts" in data
        assert "trusts" in data

    def test_get_iht_dashboard_with_calculation(self, client: TestClient, auth_headers):
        """Test dashboard with IHT calculation"""
        # Create test calculation
        calculation_data = {
            "assets": {
                "property": 400000,
                "savings": 50000,
                "investments": 100000,
                "pensions": 200000
            },
            "liabilities": {
                "mortgage": 150000,
                "other_debts": 10000
            },
            "gifts_last_7_years": 50000
        }

        calc_response = client.post(
            "/api/modules/iht/calculator",
            json=calculation_data,
            headers=auth_headers
        )
        assert calc_response.status_code == 200

        # Get dashboard
        response = client.get("/api/modules/iht/dashboard", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()

        assert data["estate_value"] > 0
        assert "iht_liability" in data
        assert "nil_rate_band_available" in data

    def test_get_iht_dashboard_unauthorized(self, client: TestClient):
        """Test dashboard requires authentication"""
        response = client.get("/api/modules/iht/dashboard")
        assert response.status_code == 401


class TestIHTSummary:
    """Test IHT summary endpoint"""

    def test_get_iht_summary(self, client: TestClient, auth_headers):
        """Test summary endpoint"""
        response = client.get("/api/modules/iht/summary", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()

        assert "estate_value" in data
        assert "iht_liability" in data
        assert "status" in data
        assert "message" in data
        assert data["status"] in ["no_liability", "low_risk", "attention_needed", "high_risk"]

    def test_iht_summary_message_format(self, client: TestClient, auth_headers):
        """Test that summary message follows narrative style"""
        response = client.get("/api/modules/iht/summary", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()

        # Message should follow STYLEGUIDE.md narrative approach
        message = data["message"]
        assert isinstance(message, str)
        assert len(message) > 0


class TestIHTCalculator:
    """Test IHT calculator endpoint"""

    def test_calculate_iht_basic(self, client: TestClient, auth_headers):
        """Test basic IHT calculation"""
        calculation_data = {
            "assets": {
                "property": 500000,
                "savings": 100000,
                "investments": 50000,
                "pensions": 150000
            },
            "liabilities": {
                "mortgage": 200000,
                "other_debts": 0
            },
            "gifts_last_7_years": 0
        }

        response = client.post(
            "/api/modules/iht/calculator",
            json=calculation_data,
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()

        assert "estate_value" in data
        assert "taxable_estate" in data
        assert "iht_liability" in data
        assert "nil_rate_band_used" in data
        assert "effective_rate" in data

        # Estate value should be assets - liabilities
        assert data["estate_value"] == 600000  # 800000 - 200000

    def test_calculate_iht_with_gifts(self, client: TestClient, auth_headers):
        """Test IHT calculation with gifts"""
        calculation_data = {
            "assets": {
                "property": 400000,
                "savings": 50000
            },
            "liabilities": {
                "mortgage": 100000
            },
            "gifts_last_7_years": 50000
        }

        response = client.post(
            "/api/modules/iht/calculator",
            json=calculation_data,
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()

        assert "estate_value" in data
        assert "gifts_included" in data
        assert data["gifts_included"] == 50000

    def test_calculate_iht_no_liability(self, client: TestClient, auth_headers):
        """Test calculation with estate below nil-rate band"""
        calculation_data = {
            "assets": {
                "property": 200000,
                "savings": 50000
            },
            "liabilities": {
                "mortgage": 0
            },
            "gifts_last_7_years": 0
        }

        response = client.post(
            "/api/modules/iht/calculator",
            json=calculation_data,
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()

        # Estate below £325k nil-rate band should have no IHT
        assert data["iht_liability"] == 0

    def test_calculate_iht_with_residence_nil_rate_band(self, client: TestClient, auth_headers):
        """Test calculation including residence nil-rate band"""
        calculation_data = {
            "assets": {
                "property": 600000,
                "savings": 100000
            },
            "liabilities": {
                "mortgage": 0
            },
            "gifts_last_7_years": 0,
            "has_main_residence": True,
            "leaving_to_direct_descendants": True
        }

        response = client.post(
            "/api/modules/iht/calculator",
            json=calculation_data,
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()

        # Should include residence nil-rate band (£175k)
        assert "residence_nil_rate_band" in data


class TestIHTGiftsCRUD:
    """Test IHT gifts CRUD operations"""

    def test_create_gift(self, client: TestClient, auth_headers):
        """Test creating a gift record"""
        gift_data = {
            "recipient_name": "Son",
            "recipient_relationship": "child",
            "gift_date": "2022-01-15",
            "gift_amount": 50000,
            "gift_type": "cash",
            "notes": "Wedding gift"
        }

        response = client.post(
            "/api/modules/iht/gifts",
            json=gift_data,
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()

        assert "id" in data
        assert data["recipient_name"] == gift_data["recipient_name"]
        assert data["gift_amount"] == gift_data["gift_amount"]
        assert "taper_relief" in data
        assert "message" in data

    def test_create_gift_validation_error(self, client: TestClient, auth_headers):
        """Test validation error for invalid gift data"""
        invalid_data = {
            "recipient_name": "",  # Empty name should fail
            "gift_amount": -1000  # Negative amount should fail
        }

        response = client.post(
            "/api/modules/iht/gifts",
            json=invalid_data,
            headers=auth_headers
        )
        assert response.status_code == 422  # Validation error

    def test_list_gifts(self, client: TestClient, auth_headers):
        """Test listing gifts"""
        # Create test gift
        gift_data = {
            "recipient_name": "Daughter",
            "recipient_relationship": "child",
            "gift_date": "2023-06-01",
            "gift_amount": 30000,
            "gift_type": "cash"
        }
        client.post("/api/modules/iht/gifts", json=gift_data, headers=auth_headers)

        # List gifts
        response = client.get("/api/modules/iht/gifts", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()

        assert "total" in data
        assert "gifts" in data
        assert data["total"] > 0
        assert len(data["gifts"]) > 0

    def test_get_gift_by_id(self, client: TestClient, auth_headers):
        """Test getting specific gift by ID"""
        # Create gift
        gift_data = {
            "recipient_name": "Grandchild",
            "recipient_relationship": "grandchild",
            "gift_date": "2024-01-01",
            "gift_amount": 20000,
            "gift_type": "property"
        }
        create_response = client.post(
            "/api/modules/iht/gifts",
            json=gift_data,
            headers=auth_headers
        )
        gift_id = create_response.json()["id"]

        # Get gift
        response = client.get(
            f"/api/modules/iht/gifts/{gift_id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()

        assert data["id"] == gift_id
        assert data["recipient_name"] == gift_data["recipient_name"]
        assert data["gift_amount"] == gift_data["gift_amount"]

    def test_update_gift(self, client: TestClient, auth_headers):
        """Test updating a gift record"""
        # Create gift
        gift_data = {
            "recipient_name": "Original Name",
            "recipient_relationship": "child",
            "gift_date": "2023-03-15",
            "gift_amount": 25000,
            "gift_type": "cash"
        }
        create_response = client.post(
            "/api/modules/iht/gifts",
            json=gift_data,
            headers=auth_headers
        )
        gift_id = create_response.json()["id"]

        # Update gift
        update_data = {
            "recipient_name": "Updated Name",
            "gift_amount": 30000
        }
        response = client.put(
            f"/api/modules/iht/gifts/{gift_id}",
            json=update_data,
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()

        assert data["recipient_name"] == update_data["recipient_name"]
        assert data["gift_amount"] == update_data["gift_amount"]

    def test_delete_gift(self, client: TestClient, auth_headers):
        """Test deleting a gift record"""
        # Create gift
        gift_data = {
            "recipient_name": "Gift to Delete",
            "recipient_relationship": "child",
            "gift_date": "2022-12-01",
            "gift_amount": 15000,
            "gift_type": "cash"
        }
        create_response = client.post(
            "/api/modules/iht/gifts",
            json=gift_data,
            headers=auth_headers
        )
        gift_id = create_response.json()["id"]

        # Delete gift
        response = client.delete(
            f"/api/modules/iht/gifts/{gift_id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()

        assert "message" in data
        assert data["id"] == gift_id

    def test_gift_taper_relief_calculation(self, client: TestClient, auth_headers):
        """Test taper relief is calculated correctly"""
        # Create gift from 5 years ago (should have 60% taper relief)
        five_years_ago = (datetime.now() - timedelta(days=5*365)).date()

        gift_data = {
            "recipient_name": "Test",
            "recipient_relationship": "child",
            "gift_date": five_years_ago.isoformat(),
            "gift_amount": 100000,
            "gift_type": "cash"
        }

        response = client.post(
            "/api/modules/iht/gifts",
            json=gift_data,
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()

        assert "taper_relief" in data
        # Taper relief should be 60% after 5 years
        assert data["taper_relief"] == 60


class TestIHTTrustsCRUD:
    """Test IHT trusts CRUD operations"""

    def test_create_trust(self, client: TestClient, auth_headers):
        """Test creating a trust record"""
        trust_data = {
            "trust_name": "Family Trust",
            "trust_type": "discretionary",
            "establishment_date": "2020-01-01",
            "trust_value": 500000,
            "beneficiaries": "Children and grandchildren",
            "trustees": "Professional trustees"
        }

        response = client.post(
            "/api/modules/iht/trusts",
            json=trust_data,
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()

        assert "id" in data
        assert data["trust_name"] == trust_data["trust_name"]
        assert data["trust_value"] == trust_data["trust_value"]
        assert "message" in data

    def test_list_trusts(self, client: TestClient, auth_headers):
        """Test listing trusts"""
        response = client.get("/api/modules/iht/trusts", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()

        assert "total" in data
        assert "trusts" in data

    def test_get_trust_by_id(self, client: TestClient, auth_headers):
        """Test getting specific trust by ID"""
        # Create trust
        trust_data = {
            "trust_name": "Specific Trust",
            "trust_type": "bare",
            "establishment_date": "2019-06-15",
            "trust_value": 250000
        }
        create_response = client.post(
            "/api/modules/iht/trusts",
            json=trust_data,
            headers=auth_headers
        )
        trust_id = create_response.json()["id"]

        # Get trust
        response = client.get(
            f"/api/modules/iht/trusts/{trust_id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()

        assert data["id"] == trust_id
        assert data["trust_name"] == trust_data["trust_name"]

    def test_update_trust(self, client: TestClient, auth_headers):
        """Test updating a trust record"""
        # Create trust
        trust_data = {
            "trust_name": "Original Trust",
            "trust_type": "discretionary",
            "establishment_date": "2021-01-01",
            "trust_value": 300000
        }
        create_response = client.post(
            "/api/modules/iht/trusts",
            json=trust_data,
            headers=auth_headers
        )
        trust_id = create_response.json()["id"]

        # Update trust
        update_data = {
            "trust_name": "Updated Trust",
            "trust_value": 350000
        }
        response = client.put(
            f"/api/modules/iht/trusts/{trust_id}",
            json=update_data,
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()

        assert data["trust_name"] == update_data["trust_name"]
        assert data["trust_value"] == update_data["trust_value"]

    def test_delete_trust(self, client: TestClient, auth_headers):
        """Test deleting a trust record"""
        # Create trust
        trust_data = {
            "trust_name": "Trust to Delete",
            "trust_type": "interest_in_possession",
            "establishment_date": "2018-03-01",
            "trust_value": 200000
        }
        create_response = client.post(
            "/api/modules/iht/trusts",
            json=trust_data,
            headers=auth_headers
        )
        trust_id = create_response.json()["id"]

        # Delete trust
        response = client.delete(
            f"/api/modules/iht/trusts/{trust_id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()

        assert "message" in data
        assert data["id"] == trust_id


class TestIHTAuthorization:
    """Test authorization and security"""

    def test_all_endpoints_require_auth(self, client: TestClient):
        """Test that all endpoints require authentication"""
        endpoints = [
            "/api/modules/iht/dashboard",
            "/api/modules/iht/summary",
            "/api/modules/iht/calculator",
            "/api/modules/iht/gifts",
            "/api/modules/iht/trusts"
        ]

        for endpoint in endpoints:
            if endpoint == "/api/modules/iht/calculator":
                response = client.post(endpoint, json={})
            else:
                response = client.get(endpoint)
            assert response.status_code == 401
