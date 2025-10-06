import pytest
from fastapi.testclient import TestClient


def test_calculate_iht(client: TestClient, auth_headers):
    iht_data = {
        "assets": [
            {"asset_type": "property", "value": 500000, "owner": "individual"},
            {"asset_type": "cash", "value": 100000, "owner": "individual"}
        ],
        "gifts": [
            {"amount": 50000, "recipient": "child", "date": "2023-01-01", "gift_type": "cash"}
        ],
        "trusts": [],
        "reliefs": {
            "business_relief": 0,
            "agricultural_relief": 0,
            "charitable_giving": 10000
        }
    }

    response = client.post("/api/iht/calculate", json=iht_data, headers=auth_headers)
    assert response.status_code == 200

    data = response.json()
    assert "total_assets" in data
    assert "taxable_estate" in data
    assert "tax_due" in data
    assert "effective_rate" in data
    assert data["total_assets"] == 600000


def test_calculate_iht_unauthorized(client: TestClient):
    iht_data = {
        "assets": [{"asset_type": "property", "value": 500000, "owner": "individual"}],
        "gifts": [],
        "trusts": [],
        "reliefs": {}
    }

    response = client.post("/api/iht/calculate", json=iht_data)
    assert response.status_code == 401


def test_taper_relief(client: TestClient, auth_headers):
    response = client.get(
        "/api/iht/taper-relief/2020-01-01?amount=100000",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert "years_since_gift" in data
    assert "taper_relief_percentage" in data
    assert "taxable_amount" in data


def test_save_iht_profile(client: TestClient, auth_headers):
    profile_data = {
        "nil_rate_band": 325000,
        "residence_nil_rate_band": 175000,
        "assets": [
            {"asset_type": "property", "value": 750000, "owner": "individual"}
        ],
        "gifts": [],
        "trusts": []
    }

    response = client.post("/api/iht/save-profile", json=profile_data, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["nil_rate_band"] == 325000
    assert data["residence_nil_rate_band"] == 175000


def test_get_iht_profile(client: TestClient, auth_headers):
    # First save a profile
    profile_data = {
        "nil_rate_band": 325000,
        "residence_nil_rate_band": 175000,
        "assets": [],
        "gifts": [],
        "trusts": []
    }
    client.post("/api/iht/save-profile", json=profile_data, headers=auth_headers)

    # Then retrieve it
    response = client.get("/api/iht/profile", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["nil_rate_band"] == 325000