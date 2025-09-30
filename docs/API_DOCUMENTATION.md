# API Documentation

**Financial Planning Application - REST API Reference**

Version: 1.0.0
Base URL: `http://localhost:8000`
Documentation: http://localhost:8000/docs (Swagger UI)
Alternative Docs: http://localhost:8000/redoc (ReDoc)

---

## Table of Contents

1. [Authentication](#authentication)
2. [IHT Calculator](#iht-calculator)
3. [IHT Enhanced](#iht-enhanced)
4. [Financial Statements](#financial-statements)
5. [Products](#products)
6. [UK Pensions](#uk-pensions)
7. [Bank Accounts](#bank-accounts)
8. [AI Chat](#ai-chat)
9. [Simulations](#simulations)
10. [Financial Projections](#financial-projections)
11. [Tax Optimization](#tax-optimization)
12. [Portfolio Rebalancing](#portfolio-rebalancing)
13. [Export](#export)
14. [Error Handling](#error-handling)
15. [Rate Limits](#rate-limits)

---

## Authentication

All protected endpoints require JWT authentication via Bearer token.

### POST /api/auth/token

**Description**: Login with username/email and password to receive JWT token.

**Request Body**:
```json
{
  "username": "testuser",
  "password": "testpass123"
}
```

**Response** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Headers for Protected Endpoints**:
```
Authorization: Bearer <access_token>
```

---

### POST /api/auth/register

**Description**: Register a new user account.

**Request Body**:
```json
{
  "username": "newuser",
  "email": "user@example.com",
  "password": "securepass123",
  "full_name": "John Doe",
  "risk_tolerance": "moderate"
}
```

**Response** (201 Created):
```json
{
  "id": 1,
  "username": "newuser",
  "email": "user@example.com",
  "full_name": "John Doe",
  "risk_tolerance": "moderate",
  "created_at": "2025-09-30T10:00:00Z"
}
```

---

### GET /api/auth/me

**Description**: Get current authenticated user information.

**Headers**: `Authorization: Bearer <token>`

**Response** (200 OK):
```json
{
  "id": 1,
  "username": "testuser",
  "email": "test@example.com",
  "full_name": "Test User",
  "risk_tolerance": "moderate"
}
```

---

## IHT Calculator

### POST /api/iht/calculate

**Description**: Calculate inheritance tax with basic rules.

**Headers**: `Authorization: Bearer <token>`

**Request Body**:
```json
{
  "estate_value": 1000000,
  "property_value": 500000,
  "gifts": [
    {
      "amount": 50000,
      "date": "2020-01-15",
      "recipient": "Daughter"
    }
  ],
  "spouse_nil_rate_band_used": 0,
  "charitable_donation": 50000
}
```

**Response** (200 OK):
```json
{
  "estate_value": 1000000,
  "nil_rate_band": 325000,
  "residence_nil_rate_band": 175000,
  "total_nil_rate_band": 500000,
  "taxable_estate": 500000,
  "tax_due": 200000,
  "effective_rate": 20.0,
  "gifts_within_7_years": [
    {
      "amount": 50000,
      "date": "2020-01-15",
      "taper_relief_percentage": 80,
      "tax_due": 10000
    }
  ]
}
```

---

### GET /api/iht/taper-relief/{gift_date}

**Description**: Calculate taper relief percentage for a gift made on specific date.

**Parameters**:
- `gift_date` (path): Date in format YYYY-MM-DD
- `amount` (query): Gift amount (optional)

**Response** (200 OK):
```json
{
  "years_ago": 5.2,
  "taper_relief_percentage": 40,
  "tax_reduction": 8000
}
```

---

### POST /api/iht/save-profile

**Description**: Save IHT profile data for current user.

**Headers**: `Authorization: Bearer <token>`

**Request Body**: Same as `/calculate` endpoint

**Response** (201 Created):
```json
{
  "id": 1,
  "user_id": 1,
  "estate_value": 1000000,
  "created_at": "2025-09-30T10:00:00Z"
}
```

---

### GET /api/iht/profile

**Description**: Get saved IHT profile for current user.

**Headers**: `Authorization: Bearer <token>`

**Response** (200 OK): Returns saved IHT profile or empty object if none exists.

---

## IHT Enhanced

Advanced IHT calculator with complete UK tax law implementation.

### POST /api/iht-enhanced/calculate-enhanced

**Description**: Comprehensive IHT calculation with all UK tax rules.

**Headers**: `Authorization: Bearer <token>`

**Request Body**:
```json
{
  "estate_value": 2500000,
  "assets": [
    {
      "type": "property",
      "value": 800000,
      "business_relief_type": "none",
      "agricultural_relief": false
    },
    {
      "type": "business_assets",
      "value": 500000,
      "business_relief_type": "unquoted_trading",
      "ownership_years": 3
    }
  ],
  "gifts": [
    {
      "amount": 100000,
      "date": "2021-06-15",
      "gift_type": "PET",
      "exemptions_used": ["annual_3000"]
    }
  ],
  "trusts": [
    {
      "type": "discretionary",
      "value": 400000,
      "creation_date": "2015-01-01"
    }
  ],
  "tnrb_percentage": 100,
  "trnrb_percentage": 100,
  "charitable_legacy": 100000
}
```

**Response** (200 OK):
```json
{
  "gross_estate": 2500000,
  "reliefs_applied": {
    "business_relief": 500000,
    "agricultural_relief": 0
  },
  "net_estate": 2000000,
  "nil_rate_band": 325000,
  "tnrb": 325000,
  "total_nrb": 650000,
  "residence_nil_rate_band": 0,
  "rnrb_tapered_amount": 175000,
  "trnrb": 175000,
  "total_threshold": 650000,
  "baseline_estate": 1900000,
  "charitable_rate_applies": false,
  "tax_rate": 40,
  "taxable_estate": 1350000,
  "tax_due": 540000,
  "effective_rate": 21.6,
  "gift_tax": 28000,
  "trust_charges": 15000,
  "total_iht": 583000
}
```

---

### POST /api/iht-enhanced/gift/validate

**Description**: Validate gift and check exemption eligibility.

**Request Body**:
```json
{
  "amount": 50000,
  "gift_date": "2025-01-15",
  "recipient": "daughter",
  "relationship": "child",
  "gift_type": "PET"
}
```

**Response** (200 OK):
```json
{
  "valid": true,
  "available_exemptions": ["annual_3000", "wedding_5000"],
  "recommended_exemptions": ["annual_3000"],
  "remaining_taxable": 47000,
  "warnings": []
}
```

---

### POST /api/iht-enhanced/trust/ten-year-charge

**Description**: Calculate 10-year periodic charge for discretionary trust.

**Request Body**:
```json
{
  "trust_value": 500000,
  "trust_creation_date": "2015-03-20",
  "charge_date": "2025-03-20",
  "nil_rate_band": 325000
}
```

**Response** (200 OK):
```json
{
  "trust_value": 500000,
  "chargeable_value": 175000,
  "settlement_rate": 0.06,
  "charge_due": 10500,
  "next_charge_date": "2035-03-20"
}
```

---

### POST /api/iht-enhanced/trust/exit-charge

**Description**: Calculate exit charge when assets leave discretionary trust.

**Request Body**:
```json
{
  "exit_amount": 100000,
  "trust_value": 500000,
  "exit_date": "2023-06-15",
  "last_ten_year_charge_date": "2015-03-20",
  "last_charge_rate": 0.06
}
```

**Response** (200 OK):
```json
{
  "exit_amount": 100000,
  "effective_charge_rate": 0.03,
  "exit_charge": 3000,
  "net_distribution": 97000
}
```

---

### GET /api/iht-enhanced/forms/iht400-data

**Description**: Generate IHT400 form data from user's profile.

**Headers**: `Authorization: Bearer <token>`

**Response** (200 OK):
```json
{
  "form_type": "IHT400",
  "deceased_details": {
    "name": "John Doe",
    "date_of_death": "2025-01-15"
  },
  "estate_summary": {
    "gross_estate": 2500000,
    "deductions": 500000,
    "net_estate": 2000000
  },
  "assets": [...],
  "liabilities": [...],
  "gifts": [...],
  "tax_calculation": {...}
}
```

---

### GET /api/iht-enhanced/excepted-estate/check

**Description**: Check if estate qualifies as excepted estate (IHT205/207/400C).

**Headers**: `Authorization: Bearer <token>`

**Query Parameters**:
- `estate_value` (required): Total estate value
- `exempt_assets` (optional): Value of exempt assets

**Response** (200 OK):
```json
{
  "is_excepted_estate": true,
  "form_type": "IHT205",
  "reasons": [
    "Estate under £325,000",
    "No chargeable gifts in 7 years",
    "All UK assets"
  ]
}
```

---

### POST /api/iht-enhanced/quick-succession-relief

**Description**: Calculate Quick Succession Relief for multiple deaths within 5 years.

**Request Body**:
```json
{
  "first_death_date": "2020-03-15",
  "second_death_date": "2024-06-20",
  "tax_paid_on_first_death": 80000,
  "property_value_received": 200000
}
```

**Response** (200 OK):
```json
{
  "years_between_deaths": 4.25,
  "relief_percentage": 40,
  "relief_amount": 32000,
  "applicable_tax": 48000
}
```

---

## Financial Statements

### GET /api/financial/balance-sheet/latest

**Description**: Get most recent balance sheet for current user.

**Headers**: `Authorization: Bearer <token>`

**Response** (200 OK):
```json
{
  "id": 1,
  "user_id": 1,
  "as_of_date": "2025-09-30",
  "assets": {
    "current_assets": 50000,
    "investments": 200000,
    "property": 500000,
    "other_assets": 50000
  },
  "liabilities": {
    "current_liabilities": 10000,
    "mortgage": 300000,
    "other_liabilities": 20000
  },
  "net_worth": 470000
}
```

---

### GET /api/financial/balance-sheet

**Description**: Get balance sheet history (paginated).

**Headers**: `Authorization: Bearer <token>`

**Query Parameters**:
- `limit` (optional): Number of records (default: 10)
- `offset` (optional): Skip records (default: 0)

**Response** (200 OK):
```json
{
  "items": [...],
  "total": 25,
  "limit": 10,
  "offset": 0
}
```

---

### POST /api/financial/balance-sheet

**Description**: Create new balance sheet entry.

**Headers**: `Authorization: Bearer <token>`

**Request Body**:
```json
{
  "as_of_date": "2025-09-30",
  "current_assets": 50000,
  "investments": 200000,
  "property": 500000,
  "other_assets": 50000,
  "current_liabilities": 10000,
  "mortgage": 300000,
  "other_liabilities": 20000
}
```

**Response** (201 Created): Returns created balance sheet.

---

### PUT /api/financial/balance-sheet/{id}

**Description**: Update existing balance sheet.

**Headers**: `Authorization: Bearer <token>`

**Parameters**: `id` (path): Balance sheet ID

**Request Body**: Same as POST

**Response** (200 OK): Returns updated balance sheet.

---

### GET /api/financial/profit-loss/latest

**Description**: Get most recent profit & loss statement.

**Headers**: `Authorization: Bearer <token>`

**Response** (200 OK):
```json
{
  "id": 1,
  "user_id": 1,
  "period_start": "2025-01-01",
  "period_end": "2025-12-31",
  "income": {
    "salary": 80000,
    "dividends": 10000,
    "rental_income": 15000,
    "other_income": 5000
  },
  "expenses": {
    "housing": 30000,
    "utilities": 6000,
    "food": 12000,
    "transport": 8000,
    "other_expenses": 14000
  },
  "net_income": 50000
}
```

---

### POST /api/financial/profit-loss

**Description**: Create profit & loss statement.

**Headers**: `Authorization: Bearer <token>`

**Request Body**: Income and expense categories with amounts.

**Response** (201 Created): Returns created P&L statement.

---

### GET /api/financial/cash-flow/latest

**Description**: Get most recent cash flow statement.

**Headers**: `Authorization: Bearer <token>`

**Response** (200 OK):
```json
{
  "id": 1,
  "user_id": 1,
  "period_start": "2025-01-01",
  "period_end": "2025-12-31",
  "operating_cash_flow": 60000,
  "investing_cash_flow": -30000,
  "financing_cash_flow": -20000,
  "net_cash_flow": 10000
}
```

---

### POST /api/financial/cash-flow

**Description**: Create cash flow statement.

**Headers**: `Authorization: Bearer <token>`

**Request Body**: Cash flow categories with amounts.

**Response** (201 Created): Returns created cash flow statement.

---

### GET /api/financial/summary

**Description**: Get comprehensive financial summary with key metrics.

**Headers**: `Authorization: Bearer <token>`

**Response** (200 OK):
```json
{
  "balance_sheet": {...},
  "profit_loss": {...},
  "cash_flow": {...},
  "metrics": {
    "net_worth": 470000,
    "savings_rate": 45.5,
    "debt_to_income_ratio": 32.5,
    "emergency_fund_months": 6.2,
    "investment_allocation": 42.6
  }
}
```

---

## Products

### GET /api/products/

**Description**: Get all products for current user.

**Headers**: `Authorization: Bearer <token>`

**Query Parameters**:
- `product_type` (optional): Filter by type (pension, investment, protection)

**Response** (200 OK):
```json
{
  "products": [
    {
      "id": 1,
      "product_type": "pension",
      "name": "Company Pension",
      "provider": "Aviva",
      "value": 150000,
      "created_at": "2025-01-01T00:00:00Z"
    }
  ]
}
```

---

### GET /api/products/{product_id}

**Description**: Get specific product by ID.

**Headers**: `Authorization: Bearer <token>`

**Parameters**: `product_id` (path): Product ID

**Response** (200 OK): Returns product details.

---

### DELETE /api/products/{product_id}

**Description**: Delete product.

**Headers**: `Authorization: Bearer <token>`

**Parameters**: `product_id` (path): Product ID

**Response** (200 OK):
```json
{
  "message": "Product deleted successfully"
}
```

---

### GET /api/products/pensions/all

**Description**: Get all pension products.

**Headers**: `Authorization: Bearer <token>`

**Response** (200 OK):
```json
{
  "pensions": [
    {
      "id": 1,
      "scheme_type": "DC",
      "provider": "Aviva",
      "value": 150000,
      "annual_contribution": 12000,
      "employer_match": 5000
    }
  ]
}
```

---

### POST /api/products/pensions

**Description**: Create new pension product.

**Headers**: `Authorization: Bearer <token>`

**Request Body**:
```json
{
  "name": "Company Pension",
  "provider": "Aviva",
  "scheme_type": "DC",
  "value": 150000,
  "annual_contribution": 12000,
  "employer_match_percentage": 5.0
}
```

**Response** (201 Created): Returns created pension.

---

### PUT /api/products/pensions/{id}

**Description**: Update pension product.

**Headers**: `Authorization: Bearer <token>`

**Parameters**: `id` (path): Pension ID

**Request Body**: Same as POST

**Response** (200 OK): Returns updated pension.

---

### GET /api/products/investments/all

**Description**: Get all investment products.

**Headers**: `Authorization: Bearer <token>`

**Response** (200 OK):
```json
{
  "investments": [
    {
      "id": 1,
      "name": "ISA Account",
      "provider": "Vanguard",
      "investment_type": "stocks_and_shares_isa",
      "value": 80000,
      "annual_return": 7.5
    }
  ]
}
```

---

### POST /api/products/investments

**Description**: Create investment product.

**Headers**: `Authorization: Bearer <token>`

**Request Body**:
```json
{
  "name": "ISA Account",
  "provider": "Vanguard",
  "investment_type": "stocks_and_shares_isa",
  "value": 80000,
  "purchase_date": "2020-04-06"
}
```

**Response** (201 Created): Returns created investment.

---

### GET /api/products/protection/all

**Description**: Get all protection products (life, critical illness, income protection).

**Headers**: `Authorization: Bearer <token>`

**Response** (200 OK):
```json
{
  "protection_products": [
    {
      "id": 1,
      "name": "Life Insurance",
      "provider": "Legal & General",
      "protection_type": "life_insurance",
      "coverage_amount": 500000,
      "premium": 50
    }
  ]
}
```

---

### POST /api/products/protection

**Description**: Create protection product.

**Headers**: `Authorization: Bearer <token>`

**Request Body**:
```json
{
  "name": "Life Insurance",
  "provider": "Legal & General",
  "protection_type": "life_insurance",
  "coverage_amount": 500000,
  "premium": 50
}
```

**Response** (201 Created): Returns created protection product.

---

### GET /api/products/portfolio/summary

**Description**: Get portfolio analytics and summary.

**Headers**: `Authorization: Bearer <token>`

**Response** (200 OK):
```json
{
  "total_value": 430000,
  "asset_allocation": {
    "pensions": 150000,
    "investments": 200000,
    "cash": 80000
  },
  "annual_contributions": 24000,
  "projected_growth": 32250,
  "risk_score": 6.5
}
```

---

### GET /api/products/retirement/projection

**Description**: Calculate retirement projection.

**Headers**: `Authorization: Bearer <token>`

**Query Parameters**:
- `retirement_age` (optional): Target retirement age (default: 65)
- `expected_return` (optional): Expected annual return % (default: 5.0)

**Response** (200 OK):
```json
{
  "current_age": 45,
  "retirement_age": 65,
  "years_to_retirement": 20,
  "current_pension_value": 150000,
  "projected_pension_value": 425000,
  "annual_income_at_retirement": 21250,
  "replacement_ratio": 42.5
}
```

---

## UK Pensions

### POST /api/pension/annual-allowance/calculate

**Description**: Calculate Annual Allowance usage for current tax year.

**Headers**: `Authorization: Bearer <token>`

**Request Body**:
```json
{
  "tax_year": "2025/26",
  "pension_contributions": [
    {
      "scheme_id": 1,
      "employee_contribution": 10000,
      "employer_contribution": 5000
    }
  ]
}
```

**Response** (200 OK):
```json
{
  "tax_year": "2025/26",
  "standard_aa": 60000,
  "tapered_aa": null,
  "total_contributions": 15000,
  "aa_used": 15000,
  "aa_remaining": 45000,
  "carry_forward_available": 120000
}
```

---

### POST /api/pension/taper/calculate

**Description**: Calculate tapered Annual Allowance for high earners.

**Headers**: `Authorization: Bearer <token>`

**Request Body**:
```json
{
  "threshold_income": 210000,
  "adjusted_income": 275000,
  "pension_contributions": 15000
}
```

**Response** (200 OK):
```json
{
  "threshold_income": 210000,
  "adjusted_income": 275000,
  "taper_applies": true,
  "income_over_threshold": 15000,
  "aa_reduction": 7500,
  "tapered_aa": 52500,
  "minimum_aa_applies": false
}
```

---

### POST /api/pension/tax-relief/calculate

**Description**: Calculate tax relief on pension contributions.

**Headers**: `Authorization: Bearer <token>`

**Request Body**:
```json
{
  "gross_contribution": 10000,
  "income": 60000,
  "relief_method": "relief_at_source",
  "scotland_resident": false
}
```

**Response** (200 OK):
```json
{
  "gross_contribution": 10000,
  "relief_method": "relief_at_source",
  "basic_rate_relief": 2000,
  "higher_rate_relief": 2000,
  "additional_rate_relief": 0,
  "total_relief": 4000,
  "effective_cost": 6000,
  "relief_percentage": 40
}
```

---

### GET /api/pension/schemes/all

**Description**: Get all pension schemes for current user.

**Headers**: `Authorization: Bearer <token>`

**Response** (200 OK):
```json
{
  "schemes": [
    {
      "id": 1,
      "name": "Company Pension",
      "scheme_type": "DC",
      "provider": "Aviva",
      "current_value": 150000,
      "annual_contribution": 15000,
      "employer_match_percentage": 5.0,
      "mpaa_triggered": false
    }
  ]
}
```

---

### POST /api/pension/schemes

**Description**: Create new pension scheme.

**Headers**: `Authorization: Bearer <token>`

**Request Body**:
```json
{
  "name": "New SIPP",
  "scheme_type": "DC",
  "provider": "Vanguard",
  "current_value": 50000,
  "relief_method": "relief_at_source"
}
```

**Response** (201 Created): Returns created scheme.

---

### POST /api/pension/optimization/optimize-contributions

**Description**: Get contribution optimization recommendations.

**Headers**: `Authorization: Bearer <token>`

**Request Body**:
```json
{
  "income": 60000,
  "current_contributions": 10000,
  "employer_match_available": 5000,
  "retirement_age": 65
}
```

**Response** (200 OK):
```json
{
  "current_contributions": 10000,
  "recommended_contributions": 15000,
  "tax_saved": 6000,
  "employer_match_optimized": true,
  "aa_efficient": true,
  "rationale": "Increase to maximize employer match and utilize basic rate relief"
}
```

---

### POST /api/pension/projection/monte-carlo

**Description**: Run Monte Carlo simulation for pension projection.

**Headers**: `Authorization: Bearer <token>`

**Request Body**:
```json
{
  "current_value": 150000,
  "annual_contribution": 15000,
  "years_to_retirement": 20,
  "expected_return": 5.0,
  "volatility": 15.0,
  "simulations": 1000
}
```

**Response** (200 OK):
```json
{
  "median_outcome": 485000,
  "percentile_10": 320000,
  "percentile_90": 680000,
  "probability_above_target": 75.5,
  "simulations_run": 1000
}
```

---

## Bank Accounts

### GET /api/bank-accounts/

**Description**: Get all bank accounts for current user.

**Headers**: `Authorization: Bearer <token>`

**Response** (200 OK):
```json
{
  "accounts": [
    {
      "id": 1,
      "account_name": "Current Account",
      "account_type": "checking",
      "balance": 5000,
      "currency": "GBP"
    }
  ]
}
```

---

### POST /api/bank-accounts/

**Description**: Create new bank account.

**Headers**: `Authorization: Bearer <token>`

**Request Body**:
```json
{
  "account_name": "Savings Account",
  "account_type": "savings",
  "balance": 15000,
  "currency": "GBP"
}
```

**Response** (201 Created): Returns created account.

---

### GET /api/bank-accounts/{account_id}/transactions

**Description**: Get transactions for specific account.

**Headers**: `Authorization: Bearer <token>`

**Parameters**: `account_id` (path): Account ID

**Query Parameters**:
- `limit` (optional): Number of transactions (default: 50)
- `offset` (optional): Skip transactions (default: 0)

**Response** (200 OK):
```json
{
  "transactions": [
    {
      "id": 1,
      "date": "2025-09-30",
      "description": "Salary",
      "amount": 3000,
      "category": "income",
      "balance_after": 8000
    }
  ]
}
```

---

### POST /api/bank-accounts/import-csv

**Description**: Import transactions from CSV file.

**Headers**: `Authorization: Bearer <token>`

**Request Body** (multipart/form-data):
- `file`: CSV file with columns: date, description, amount, category
- `account_id`: Target account ID

**Response** (201 Created):
```json
{
  "imported": 125,
  "skipped": 5,
  "errors": []
}
```

---

## AI Chat

### POST /api/chat/message

**Description**: Send message to AI assistant.

**Headers**: `Authorization: Bearer <token>`

**Request Body**:
```json
{
  "message": "What is my current pension value?",
  "session_id": "abc123"
}
```

**Response** (200 OK):
```json
{
  "message_id": 1,
  "response": "Based on your current pension schemes, your total pension value is £150,000. This includes your company pension with Aviva.",
  "intent": "query_pension_value",
  "extracted_data": {
    "pension_value": 150000
  },
  "suggestions": [
    "Would you like to see your retirement projection?",
    "Calculate Annual Allowance usage"
  ]
}
```

---

### GET /api/chat/history

**Description**: Get chat history for current user.

**Headers**: `Authorization: Bearer <token>`

**Query Parameters**:
- `session_id` (optional): Filter by session
- `limit` (optional): Number of messages (default: 50)

**Response** (200 OK):
```json
{
  "messages": [
    {
      "id": 1,
      "message": "What is my pension value?",
      "response": "Your pension value is £150,000",
      "timestamp": "2025-09-30T10:00:00Z"
    }
  ]
}
```

---

## Simulations

### POST /api/simulations/portfolio-monte-carlo

**Description**: Run Monte Carlo simulation for portfolio growth.

**Headers**: `Authorization: Bearer <token>`

**Request Body**:
```json
{
  "initial_value": 200000,
  "annual_contribution": 20000,
  "years": 20,
  "expected_return": 7.0,
  "volatility": 15.0,
  "simulations": 1000
}
```

**Response** (200 OK):
```json
{
  "median_value": 885000,
  "mean_value": 920000,
  "percentile_10": 580000,
  "percentile_25": 720000,
  "percentile_75": 1100000,
  "percentile_90": 1350000,
  "probability_above_1m": 62.5,
  "var_95": 550000,
  "cvar_95": 480000
}
```

---

### POST /api/simulations/iht-scenario

**Description**: Run IHT scenario simulation.

**Headers**: `Authorization: Bearer <token>`

**Request Body**:
```json
{
  "estate_value": 2000000,
  "life_expectancy_years": 25,
  "gift_strategy": "annual_exemptions",
  "charitable_legacy_percentage": 10
}
```

**Response** (200 OK):
```json
{
  "current_iht": 540000,
  "projected_iht_with_strategy": 320000,
  "tax_saved": 220000,
  "optimal_gifting_schedule": [...],
  "recommendations": [...]
}
```

---

## Financial Projections

### POST /api/projections/calculate

**Description**: Calculate multi-year financial projections.

**Headers**: `Authorization: Bearer <token>`

**Request Body**:
```json
{
  "projection_years": 30,
  "current_age": 45,
  "retirement_age": 65,
  "current_assets": 500000,
  "current_liabilities": 300000,
  "annual_income": 80000,
  "annual_expenses": 50000,
  "income_growth_rate": 3.0,
  "expense_growth_rate": 2.5,
  "investment_return": 6.0,
  "inflation_rate": 2.0
}
```

**Response** (200 OK):
```json
{
  "projections": [
    {
      "year": 2025,
      "age": 45,
      "income": 80000,
      "expenses": 50000,
      "net_worth": 700000,
      "investment_value": 550000
    }
  ],
  "retirement_readiness": 85.5,
  "surplus_at_retirement": 250000
}
```

---

### POST /api/projections/scenario-comparison

**Description**: Compare conservative, moderate, and optimistic scenarios.

**Headers**: `Authorization: Bearer <token>`

**Request Body**: Same as `/calculate` with scenario parameters.

**Response** (200 OK):
```json
{
  "conservative": {
    "retirement_net_worth": 1200000,
    "annual_income": 48000
  },
  "moderate": {
    "retirement_net_worth": 1800000,
    "annual_income": 72000
  },
  "optimistic": {
    "retirement_net_worth": 2600000,
    "annual_income": 104000
  }
}
```

---

### GET /api/projections/retirement-readiness

**Description**: Calculate retirement readiness score.

**Headers**: `Authorization: Bearer <token>`

**Query Parameters**:
- `target_income` (optional): Target retirement income (default: 70% of current)

**Response** (200 OK):
```json
{
  "readiness_score": 78.5,
  "projected_income": 45000,
  "target_income": 56000,
  "income_gap": 11000,
  "recommendations": [
    "Increase pension contributions by £200/month",
    "Review investment allocation"
  ]
}
```

---

## Tax Optimization

### POST /api/tax-optimization/analyze-position

**Description**: Analyze current tax position.

**Headers**: `Authorization: Bearer <token>`

**Request Body**:
```json
{
  "employment_income": 60000,
  "dividend_income": 8000,
  "rental_income": 12000,
  "pension_contributions": 10000,
  "gift_aid_donations": 500
}
```

**Response** (200 OK):
```json
{
  "gross_income": 80000,
  "taxable_income": 69500,
  "income_tax": 13900,
  "national_insurance": 5724,
  "dividend_tax": 525,
  "total_tax": 20149,
  "net_income": 59851,
  "effective_rate": 25.2,
  "marginal_rate": 42
}
```

---

### POST /api/tax-optimization/optimize-pension

**Description**: Get pension contribution optimization.

**Headers**: `Authorization: Bearer <token>`

**Request Body**:
```json
{
  "gross_income": 60000,
  "current_pension_contribution": 5000
}
```

**Response** (200 OK):
```json
{
  "current_contribution": 5000,
  "recommended_contribution": 12000,
  "additional_contribution": 7000,
  "tax_saved": 2800,
  "net_cost": 4200,
  "aa_remaining": 48000
}
```

---

### POST /api/tax-optimization/optimize-salary-dividend

**Description**: Optimize salary/dividend split for directors.

**Headers**: `Authorization: Bearer <token>`

**Request Body**:
```json
{
  "company_profits": 80000,
  "target_income": 60000
}
```

**Response** (200 OK):
```json
{
  "recommended_salary": 12570,
  "recommended_dividends": 47430,
  "total_take_home": 60000,
  "income_tax": 3281,
  "national_insurance": 0,
  "dividend_tax": 3149,
  "total_tax": 6430,
  "corporation_tax": 6100,
  "overall_tax_efficiency": 89.2
}
```

---

### POST /api/tax-optimization/comprehensive-report

**Description**: Get comprehensive tax optimization report.

**Headers**: `Authorization: Bearer <token>`

**Request Body**: Complete financial profile.

**Response** (200 OK):
```json
{
  "current_tax": 20149,
  "optimized_tax": 15200,
  "potential_savings": 4949,
  "recommendations": [
    {
      "priority": "high",
      "category": "pension",
      "action": "Increase pension contributions to £12,000",
      "saving": 2800
    }
  ]
}
```

---

## Portfolio Rebalancing

### POST /api/rebalancing/analyze-current-allocation

**Description**: Analyze current portfolio allocation.

**Headers**: `Authorization: Bearer <token>`

**Request Body**:
```json
{
  "holdings": [
    {
      "asset": "UK Equity",
      "value": 80000,
      "target_percentage": 40
    },
    {
      "asset": "Global Equity",
      "value": 60000,
      "target_percentage": 30
    }
  ]
}
```

**Response** (200 OK):
```json
{
  "total_value": 200000,
  "current_allocation": {
    "UK Equity": 40.0,
    "Global Equity": 30.0
  },
  "drift_analysis": {
    "UK Equity": 0.0,
    "Global Equity": 0.0
  },
  "rebalancing_needed": false
}
```

---

### POST /api/rebalancing/calculate-drift

**Description**: Calculate portfolio drift from target allocation.

**Headers**: `Authorization: Bearer <token>`

**Request Body**: Same as `/analyze-current-allocation`.

**Response** (200 OK):
```json
{
  "total_drift": 8.5,
  "asset_drifts": {
    "UK Equity": 5.2,
    "Global Equity": -3.3
  },
  "rebalancing_recommended": true
}
```

---

### POST /api/rebalancing/generate-plan

**Description**: Generate tax-efficient rebalancing plan.

**Headers**: `Authorization: Bearer <token>`

**Request Body**:
```json
{
  "holdings": [...],
  "accounts": [
    {"type": "ISA", "value": 100000},
    {"type": "GIA", "value": 100000}
  ],
  "cgt_allowance_used": 0,
  "tolerance_band": 5.0
}
```

**Response** (200 OK):
```json
{
  "transactions": [
    {
      "action": "sell",
      "asset": "UK Equity",
      "amount": 10000,
      "account": "ISA",
      "cgt_impact": 0
    },
    {
      "action": "buy",
      "asset": "Global Equity",
      "amount": 10000,
      "account": "ISA"
    }
  ],
  "total_cgt": 0,
  "estimated_costs": 50,
  "net_benefit": 2000
}
```

---

### GET /api/rebalancing/tax-efficient-strategies

**Description**: Get UK tax-efficient rebalancing strategies.

**Headers**: `Authorization: Bearer <token>`

**Response** (200 OK):
```json
{
  "strategies": [
    {
      "name": "ISA Priority",
      "description": "Rebalance within ISA first to avoid CGT",
      "tax_saving": "Up to £600/year"
    },
    {
      "name": "Tax Loss Harvesting",
      "description": "Sell losses in GIA to offset gains",
      "tax_saving": "Variable"
    }
  ]
}
```

---

## Export

### GET /api/export/iht-pdf

**Description**: Export IHT calculation as PDF.

**Headers**: `Authorization: Bearer <token>`

**Response** (200 OK): PDF file download.

---

### GET /api/export/iht-excel

**Description**: Export IHT data to Excel.

**Headers**: `Authorization: Bearer <token>`

**Response** (200 OK): Excel file download.

---

### GET /api/export/financial-statements-csv

**Description**: Export financial statements as CSV.

**Headers**: `Authorization: Bearer <token>`

**Query Parameters**:
- `statement_type` (required): balance_sheet, profit_loss, or cash_flow
- `start_date` (optional): Filter from date
- `end_date` (optional): Filter to date

**Response** (200 OK): CSV file download.

---

### POST /api/export/import-csv

**Description**: Import data from CSV file.

**Headers**: `Authorization: Bearer <token>`

**Request Body** (multipart/form-data):
- `file`: CSV file
- `import_type`: Type of data (transactions, gifts, assets, etc.)

**Response** (201 Created):
```json
{
  "imported": 150,
  "updated": 25,
  "errors": []
}
```

---

## Error Handling

### Standard Error Response

All API errors return JSON in this format:

```json
{
  "detail": "Error message",
  "error_code": "ERROR_CODE",
  "status_code": 400
}
```

### Common HTTP Status Codes

- **200 OK**: Request succeeded
- **201 Created**: Resource created
- **400 Bad Request**: Invalid request data
- **401 Unauthorized**: Missing or invalid authentication
- **403 Forbidden**: Authenticated but not authorized
- **404 Not Found**: Resource not found
- **422 Unprocessable Entity**: Validation error
- **500 Internal Server Error**: Server error

### Error Codes

- `INVALID_CREDENTIALS`: Username/password incorrect
- `TOKEN_EXPIRED`: JWT token expired
- `INSUFFICIENT_PERMISSIONS`: Not authorized for this action
- `VALIDATION_ERROR`: Request validation failed
- `RESOURCE_NOT_FOUND`: Requested resource doesn't exist
- `DUPLICATE_RESOURCE`: Resource already exists
- `CALCULATION_ERROR`: Error in financial calculation
- `DATABASE_ERROR`: Database operation failed

---

## Rate Limits

### Current Limits
- **Authentication endpoints**: 10 requests per minute
- **Standard endpoints**: 100 requests per minute
- **Simulation endpoints**: 10 requests per minute (computationally expensive)
- **Export endpoints**: 20 requests per minute

### Rate Limit Headers

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1696089600
```

### Exceeded Rate Limit Response

**Status**: 429 Too Many Requests

```json
{
  "detail": "Rate limit exceeded",
  "retry_after": 60
}
```

---

## Versioning

Current API version: **v1.0.0**

API versioning is handled via URL path:
- Current: `/api/...`
- Future: `/api/v2/...`

Breaking changes will be introduced in new versions while maintaining backward compatibility for at least 6 months.

---

## Support

- **API Issues**: https://github.com/yourrepo/issues
- **Email**: support@example.com
- **Documentation**: http://localhost:8000/docs

---

## Changelog

### v1.0.0 (2025-09-30)
- Initial API release
- All core endpoints implemented
- UK IHT calculator with enhanced features
- UK pension planning with complete HMRC rules
- Financial projections and tax optimization
- Portfolio analytics and rebalancing

---

*Last Updated: 2025-09-30*