#!/usr/bin/env python3
"""Test script for API endpoints"""

import requests
import json
from datetime import date

BASE_URL = "http://localhost:8000"

def test_auth():
    """Test authentication"""
    print("Testing authentication...")

    # Login
    response = requests.post(
        f"{BASE_URL}/api/auth/token",
        data={"username": "demouser", "password": "demo123"}
    )
    if response.status_code == 200:
        token = response.json()["access_token"]
        print("✓ Login successful")
        return token
    else:
        print(f"✗ Login failed: {response.status_code}")
        return None

def test_iht_calculation(token):
    """Test IHT calculation"""
    print("\nTesting IHT calculation...")

    headers = {"Authorization": f"Bearer {token}"}

    data = {
        "assets": [
            {"asset_type": "property", "value": 500000, "description": "Main residence"},
            {"asset_type": "cash", "value": 100000, "description": "Bank accounts"}
        ],
        "gifts": [],
        "trusts": [],
        "marital_status": "single",
        "residence_value": 500000,
        "charitable_gifts": 0
    }

    response = requests.post(
        f"{BASE_URL}/api/iht/calculate",
        headers=headers,
        json=data
    )

    if response.status_code == 200:
        result = response.json()
        print(f"✓ IHT calculation successful")
        print(f"  Total estate: £{result['total_estate_value']:,.0f}")
        print(f"  IHT due: £{result['iht_due']:,.0f}")
        print(f"  Effective rate: {result['effective_rate']:.1f}%")
    else:
        print(f"✗ IHT calculation failed: {response.status_code}")
        print(f"  Response: {response.text}")

def test_financial_summary(token):
    """Test financial summary"""
    print("\nTesting financial summary...")

    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(
        f"{BASE_URL}/api/financial/summary",
        headers=headers
    )

    if response.status_code == 200:
        result = response.json()
        print(f"✓ Financial summary successful")
        print(f"  Net worth: £{result['net_worth']:,.0f}")
        print(f"  Monthly income: £{result['monthly_income']:,.0f}")
        print(f"  Monthly expenses: £{result['monthly_expenses']:,.0f}")
    else:
        print(f"✗ Financial summary failed: {response.status_code}")

def test_portfolio_summary(token):
    """Test portfolio summary"""
    print("\nTesting portfolio summary...")

    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(
        f"{BASE_URL}/api/products/portfolio/summary",
        headers=headers
    )

    if response.status_code == 200:
        result = response.json()
        print(f"✓ Portfolio summary successful")
        print(f"  Total value: £{result['total_value']:,.0f}")
        print(f"  Product count: {result['product_count']}")
    else:
        print(f"✗ Portfolio summary failed: {response.status_code}")

def main():
    """Run all tests"""
    print("=" * 50)
    print("API Test Suite")
    print("=" * 50)

    # Test authentication
    token = test_auth()

    if token:
        # Test other endpoints
        test_iht_calculation(token)
        test_financial_summary(token)
        test_portfolio_summary(token)

    print("\n" + "=" * 50)
    print("Test complete")
    print("=" * 50)

if __name__ == "__main__":
    main()