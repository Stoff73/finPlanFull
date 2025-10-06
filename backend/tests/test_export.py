import pytest
from fastapi.testclient import TestClient
import json


def test_export_iht_pdf(client: TestClient, auth_headers):
    # First create an IHT profile
    profile_data = {
        "nil_rate_band": 325000,
        "residence_nil_rate_band": 175000,
        "assets": [
            {"asset_type": "property", "value": 500000, "owner": "individual"}
        ],
        "gifts": [],
        "trusts": []
    }
    client.post("/api/iht/save-profile", json=profile_data, headers=auth_headers)

    # Export as PDF
    response = client.get("/api/export/iht/pdf", headers=auth_headers)
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert len(response.content) > 0


def test_export_financial_excel(client: TestClient, auth_headers):
    # First create some financial data
    balance_sheet = {
        "period": "2024-01-01",
        "current_assets": 100000,
        "fixed_assets": 200000,
        "total_assets": 300000,
        "current_liabilities": 50000,
        "long_term_liabilities": 100000,
        "total_liabilities": 150000,
        "equity": 150000
    }
    client.post("/api/financial/balance-sheet", json=balance_sheet, headers=auth_headers)

    # Export as Excel
    response = client.get("/api/export/financial/excel", headers=auth_headers)
    assert response.status_code == 200
    assert "spreadsheetml" in response.headers["content-type"]
    assert len(response.content) > 0


def test_export_products_csv(client: TestClient, auth_headers):
    # First create a product
    product = {
        "product_type": "pension",
        "provider": "Test Provider",
        "product_name": "Test Pension",
        "value": 50000
    }
    client.post("/api/products/pensions", json=product, headers=auth_headers)

    # Export as CSV
    response = client.get("/api/export/products/csv", headers=auth_headers)
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/csv"
    assert b"product_type" in response.content


def test_backup_restore(client: TestClient, auth_headers):
    # Create backup
    response = client.get("/api/export/backup", headers=auth_headers)
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"

    backup_data = response.content

    # Verify it's valid JSON
    data = json.loads(backup_data)
    assert "timestamp" in data
    assert "version" in data
    assert "data" in data


def test_csv_import(client: TestClient, auth_headers):
    # Create CSV content
    csv_content = b"product_type,provider,product_name,value\npension,Test Provider,Test Pension,50000"

    response = client.post(
        "/api/export/products/csv/import",
        files={"file": ("test.csv", csv_content, "text/csv")},
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["count"] > 0