# Architecture Documentation

**Financial Planning Application - System Architecture**

Version 1.0.0 | Last Updated: 2025-09-30

---

## Table of Contents

1. [High-Level Architecture](#high-level-architecture)
2. [System Components](#system-components)
3. [Data Flow Diagrams](#data-flow-diagrams)
4. [Database Architecture](#database-architecture)
5. [API Architecture](#api-architecture)
6. [Frontend Architecture](#frontend-architecture)
7. [Security Architecture](#security-architecture)
8. [Deployment Architecture](#deployment-architecture)
9. [Technology Stack](#technology-stack)
10. [Design Patterns](#design-patterns)

---

## High-Level Architecture

### Three-Tier Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         PRESENTATION TIER                            │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │                     React Frontend (SPA)                       │  │
│  │  - TypeScript + Styled Components                             │  │
│  │  - React Router (Client-side routing)                         │  │
│  │  - Context API (State management)                             │  │
│  │  - Recharts (Data visualization)                              │  │
│  │                                                                │  │
│  │  Pages:                        Components:                    │  │
│  │  • Dashboard                   • Button, Card, Input          │  │
│  │  • IHT Calculator              • Header, Navigation           │  │
│  │  • Pension Planning            • Charts, Tables               │  │
│  │  • Financial Statements        • Forms, Modals                │  │
│  │  • Tax Optimization            • Widgets, Cards               │  │
│  │  • Portfolio Analytics                                        │  │
│  └───────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                                    ↓ ↑
                          HTTP/HTTPS REST API
                          JSON Request/Response
                                    ↓ ↑
┌─────────────────────────────────────────────────────────────────────┐
│                          APPLICATION TIER                            │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │                     FastAPI Backend (Python)                   │  │
│  │                                                                │  │
│  │  API Layer (app/api/):                                        │  │
│  │  ┌─────────────────────────────────────────────────────────┐ │  │
│  │  │ • auth.py          - Authentication & JWT               │ │  │
│  │  │ • iht.py           - IHT calculator                     │ │  │
│  │  │ • iht_refactored.py - Enhanced IHT                      │ │  │
│  │  │ • financial.py     - Financial statements               │ │  │
│  │  │ • products.py      - Product management                 │ │  │
│  │  │ • pension/         - UK pension planning                │ │  │
│  │  │ • projections.py   - Financial projections              │ │  │
│  │  │ • tax_optimization.py - Tax planning                    │ │  │
│  │  │ • rebalancing.py   - Portfolio rebalancing              │ │  │
│  │  │ • simulations.py   - Monte Carlo simulations            │ │  │
│  │  │ • chat.py          - AI chat assistant                  │ │  │
│  │  │ • export.py        - Data export                        │ │  │
│  │  └─────────────────────────────────────────────────────────┘ │  │
│  │                                                                │  │
│  │  Service Layer (app/services/):                               │  │
│  │  ┌─────────────────────────────────────────────────────────┐ │  │
│  │  │ • iht_calculator.py      - IHT calculations            │ │  │
│  │  │ • monte_carlo.py         - Simulation engine           │ │  │
│  │  │ • tax_optimizer.py       - Tax optimization logic      │ │  │
│  │  │ • portfolio_rebalancer.py - Rebalancing algorithms     │ │  │
│  │  │ • projection_engine.py   - Financial projections       │ │  │
│  │  └─────────────────────────────────────────────────────────┘ │  │
│  │                                                                │  │
│  │  Model Layer (app/models/):                                   │  │
│  │  ┌─────────────────────────────────────────────────────────┐ │  │
│  │  │ SQLAlchemy ORM Models:                                  │ │  │
│  │  │ • user.py          • iht.py           • pension.py      │ │  │
│  │  │ • financial.py     • products.py      • chat.py         │ │  │
│  │  │ • bank_account.py                                       │ │  │
│  │  └─────────────────────────────────────────────────────────┘ │  │
│  └───────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                                    ↓ ↑
                           SQL Queries/Results
                                    ↓ ↑
┌─────────────────────────────────────────────────────────────────────┐
│                            DATA TIER                                 │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │                    SQLite Database                             │  │
│  │                                                                │  │
│  │  Tables:                                                       │  │
│  │  • users                  • enhanced_pensions                 │  │
│  │  • iht_profiles           • pension_input_periods             │  │
│  │  • gifts                  • carry_forward                     │  │
│  │  • trusts                 • products                          │  │
│  │  • assets                 • balance_sheets                    │  │
│  │  • balance_sheets         • profit_loss_statements            │  │
│  │  • profit_loss            • cash_flow_statements              │  │
│  │  • bank_accounts          • transactions                      │  │
│  │  • chat_messages          • chat_sessions                     │  │
│  │                                                                │  │
│  │  (Production: PostgreSQL recommended)                         │  │
│  └───────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## System Components

### Frontend Components (React)

```
frontend/src/
│
├── components/
│   ├── common/                    # Shared UI Components
│   │   ├── Button.tsx             # Reusable button with variants
│   │   ├── Card.tsx               # Container with styling
│   │   ├── Input.tsx              # Form input with validation
│   │   ├── LoadingSpinner.tsx     # Loading states
│   │   ├── Breadcrumb.tsx         # Navigation breadcrumbs
│   │   └── ThemeToggle.tsx        # Dark/light mode toggle
│   │
│   ├── layout/                    # Layout Components
│   │   ├── Header.tsx             # Main navigation header
│   │   ├── MobileNav.tsx          # Mobile hamburger menu
│   │   ├── Container.tsx          # Responsive container
│   │   └── Grid.tsx               # Grid system (Row/Col)
│   │
│   ├── iht/                       # IHT-Specific Components
│   │   ├── GiftTimelineVisualization.tsx
│   │   ├── EstatePlanningScenarios.tsx
│   │   ├── GiftHistoryManager.tsx
│   │   ├── TrustManager.tsx
│   │   ├── ExemptionTracker.tsx
│   │   ├── ValuationTools.tsx
│   │   ├── IHTCompliance.tsx
│   │   ├── MultipleMarriageTracker.tsx
│   │   ├── DownsizingAddition.tsx
│   │   ├── GiftWithReservationTracker.tsx
│   │   └── IHTDashboardWidget.tsx
│   │
│   └── pension/                   # Pension Components
│       ├── AnnualAllowanceGauge.tsx
│       ├── TaxReliefCalculator.tsx
│       ├── SchemeCard.tsx
│       └── PensionDashboardWidget.tsx
│
├── pages/                         # Page-Level Components
│   ├── Dashboard.tsx              # Main dashboard
│   ├── Login.tsx / Register.tsx   # Authentication
│   ├── IHT*.tsx                   # IHT pages
│   ├── RetirementPlanningUK.tsx   # Pension planning
│   ├── FinancialStatements.tsx    # Financial data
│   ├── TaxOptimization.tsx        # Tax planning
│   ├── PortfolioRebalancing.tsx   # Rebalancing
│   └── Chat.tsx                   # AI assistant
│
├── context/                       # Global State
│   ├── AuthContext.tsx            # Authentication state
│   └── ThemeContext.tsx           # Theme state (dark/light)
│
├── services/                      # API Services
│   └── auth.ts                    # API communication
│
└── styles/                        # Styling
    ├── theme.ts                   # Design tokens
    ├── GlobalStyles.ts            # Global CSS
    └── responsive.ts              # Breakpoints
```

### Backend Components (FastAPI)

```
backend/app/
│
├── api/                           # API Endpoints
│   ├── auth/
│   │   ├── auth.py                # Login, register, JWT
│   │   └── models.py              # Pydantic schemas
│   │
│   ├── iht.py                     # Basic IHT endpoints
│   ├── iht_refactored.py          # Enhanced IHT endpoints
│   ├── financial.py               # Financial statements
│   ├── products.py                # Product management
│   │
│   ├── pension/                   # Pension endpoints
│   │   ├── pension_uk.py          # AA, taper, MPAA, tax relief
│   │   ├── pension_schemes.py     # Multi-scheme management
│   │   └── pension_optimization.py # Optimization & projections
│   │
│   ├── simulations.py             # Monte Carlo
│   ├── projections.py             # Financial projections
│   ├── tax_optimization.py        # Tax planning
│   ├── rebalancing.py             # Portfolio rebalancing
│   ├── chat.py                    # AI chat
│   └── export.py                  # PDF/Excel/CSV export
│
├── models/                        # Database Models (SQLAlchemy)
│   ├── user.py                    # User authentication
│   ├── iht.py                     # IHT profiles, gifts, trusts
│   ├── pension.py                 # Pension schemes, AA tracking
│   ├── financial.py               # Balance sheets, P&L
│   ├── products.py                # Products, investments
│   ├── bank_account.py            # Accounts, transactions
│   └── chat.py                    # Chat messages, sessions
│
├── services/                      # Business Logic
│   ├── iht_calculator.py          # IHT calculations
│   ├── monte_carlo.py             # Simulation engine
│   ├── tax_optimizer.py           # UK tax optimization
│   ├── portfolio_rebalancer.py    # Rebalancing algorithms
│   └── projection_engine.py       # Multi-year projections
│
├── main.py                        # FastAPI app entry point
├── config.py                      # Configuration
└── database.py                    # Database connection
```

---

## Data Flow Diagrams

### User Authentication Flow

```
┌──────────┐                 ┌──────────┐                 ┌──────────┐
│  Client  │                 │   API    │                 │ Database │
│ (React)  │                 │ (FastAPI)│                 │ (SQLite) │
└────┬─────┘                 └────┬─────┘                 └────┬─────┘
     │                            │                            │
     │ 1. POST /api/auth/token    │                            │
     │    {username, password}    │                            │
     │───────────────────────────>│                            │
     │                            │                            │
     │                            │ 2. Query user by username  │
     │                            │───────────────────────────>│
     │                            │                            │
     │                            │ 3. Return user record      │
     │                            │<───────────────────────────│
     │                            │                            │
     │                            │ 4. Verify password hash    │
     │                            │    (bcrypt compare)        │
     │                            │                            │
     │                            │ 5. Generate JWT token      │
     │                            │    (python-jose)           │
     │                            │                            │
     │ 6. Return access token     │                            │
     │<───────────────────────────│                            │
     │                            │                            │
     │ 7. Store token in          │                            │
     │    localStorage            │                            │
     │                            │                            │
     │ 8. GET /api/auth/me        │                            │
     │    Header: Bearer <token>  │                            │
     │───────────────────────────>│                            │
     │                            │                            │
     │                            │ 9. Verify JWT signature    │
     │                            │                            │
     │                            │ 10. Query user by ID       │
     │                            │────────────────────────────>│
     │                            │                            │
     │                            │ 11. Return user data       │
     │                            │<────────────────────────────│
     │                            │                            │
     │ 12. Return user profile    │                            │
     │<───────────────────────────│                            │
     │                            │                            │
     │ 13. Navigate to Dashboard  │                            │
     │                            │                            │
```

### IHT Calculation Flow

```
┌──────────┐         ┌──────────┐         ┌──────────┐         ┌──────────┐
│  Client  │         │   API    │         │ Service  │         │ Database │
└────┬─────┘         └────┬─────┘         └────┬─────┘         └────┬─────┘
     │                    │                    │                    │
     │ 1. User inputs     │                    │                    │
     │    estate data     │                    │                    │
     │                    │                    │                    │
     │ 2. POST /api/iht   │                    │                    │
     │    /calculate      │                    │                    │
     │───────────────────>│                    │                    │
     │                    │                    │                    │
     │                    │ 3. Validate input  │                    │
     │                    │    (Pydantic)      │                    │
     │                    │                    │                    │
     │                    │ 4. Call calculator │                    │
     │                    │────────────────────>│                    │
     │                    │                    │                    │
     │                    │                    │ 5. Get user gifts  │
     │                    │                    │ from last 7 years  │
     │                    │                    │───────────────────>│
     │                    │                    │                    │
     │                    │                    │ 6. Return gifts    │
     │                    │                    │<───────────────────│
     │                    │                    │                    │
     │                    │                    │ 7. Calculate NRB   │
     │                    │                    │    (£325k + TNRB)  │
     │                    │                    │                    │
     │                    │                    │ 8. Calculate RNRB  │
     │                    │                    │    (£175k - taper) │
     │                    │                    │                    │
     │                    │                    │ 9. Apply reliefs   │
     │                    │                    │    (BR, APR, etc.) │
     │                    │                    │                    │
     │                    │                    │10. Calculate tax   │
     │                    │                    │    at 40% or 36%   │
     │                    │                    │                    │
     │                    │                    │11. Calculate gift  │
     │                    │                    │    tax with taper  │
     │                    │                    │                    │
     │                    │12. Return results  │                    │
     │                    │<────────────────────│                    │
     │                    │                    │                    │
     │13. Return JSON     │                    │                    │
     │<───────────────────│                    │                    │
     │                    │                    │                    │
     │14. Display charts  │                    │                    │
     │    and breakdown   │                    │                    │
     │                    │                    │                    │
     │15. Option to save  │                    │                    │
     │    POST /save      │                    │                    │
     │───────────────────>│                    │                    │
     │                    │                    │                    │
     │                    │16. Insert profile  │                    │
     │                    │────────────────────────────────────────>│
     │                    │                    │                    │
     │                    │17. Return saved ID │                    │
     │                    │<────────────────────────────────────────│
     │                    │                    │                    │
     │18. Confirm saved   │                    │                    │
     │<───────────────────│                    │                    │
     │                    │                    │                    │
```

### Pension Annual Allowance Flow

```
┌──────────┐         ┌──────────┐         ┌──────────┐         ┌──────────┐
│  Client  │         │   API    │         │ Service  │         │ Database │
└────┬─────┘         └────┬─────┘         └────┬─────┘         └────┬─────┘
     │                    │                    │                    │
     │ 1. User views      │                    │                    │
     │    pension page    │                    │                    │
     │                    │                    │                    │
     │ 2. GET /api/pension│                    │                    │
     │    /schemes/all    │                    │                    │
     │───────────────────>│                    │                    │
     │                    │                    │                    │
     │                    │ 3. Get all schemes │                    │
     │                    │────────────────────────────────────────>│
     │                    │                    │                    │
     │                    │ 4. Return schemes  │                    │
     │                    │<────────────────────────────────────────│
     │                    │                    │                    │
     │ 5. Display schemes │                    │                    │
     │<───────────────────│                    │                    │
     │                    │                    │                    │
     │ 6. User adds       │                    │                    │
     │    contribution    │                    │                    │
     │                    │                    │                    │
     │ 7. POST /api       │                    │                    │
     │    /pension/aa     │                    │                    │
     │    /calculate      │                    │                    │
     │───────────────────>│                    │                    │
     │                    │                    │                    │
     │                    │ 8. Calculate AA    │                    │
     │                    │────────────────────>│                    │
     │                    │                    │                    │
     │                    │                    │ 9. Get income data │
     │                    │                    │───────────────────>│
     │                    │                    │                    │
     │                    │                    │10. Calculate taper │
     │                    │                    │    if income >£260k│
     │                    │                    │                    │
     │                    │                    │11. Get 3-year      │
     │                    │                    │    carry-forward   │
     │                    │                    │───────────────────>│
     │                    │                    │                    │
     │                    │                    │12. Calculate total │
     │                    │                    │    available AA    │
     │                    │                    │                    │
     │                    │                    │13. Check MPAA      │
     │                    │                    │    restrictions    │
     │                    │                    │                    │
     │                    │14. Return AA data  │                    │
     │                    │<────────────────────│                    │
     │                    │                    │                    │
     │15. Display gauge   │                    │                    │
     │    and warnings    │                    │                    │
     │<───────────────────│                    │                    │
     │                    │                    │                    │
```

---

## Database Architecture

### Entity-Relationship Diagram

```
┌─────────────────────┐
│       Users         │
├─────────────────────┤
│ PK: id              │
│     username        │───┐
│     email           │   │
│     hashed_password │   │
│     full_name       │   │
│     risk_tolerance  │   │
│     created_at      │   │
└─────────────────────┘   │
                          │ 1:N
         ┌────────────────┼───────────────────────────────┐
         │                │                               │
         ↓                ↓                               ↓
┌─────────────────┐ ┌─────────────────┐  ┌─────────────────────────┐
│  IHT Profiles   │ │Enhanced Pensions│  │   Balance Sheets        │
├─────────────────┤ ├─────────────────┤  ├─────────────────────────┤
│ PK: id          │ │ PK: id          │  │ PK: id                  │
│ FK: user_id     │ │ FK: user_id     │  │ FK: user_id             │
│     estate_value│ │     name        │  │     as_of_date          │
│     property    │ │     provider    │  │     current_assets      │
│     spouse_nrb  │ │     scheme_type │  │     investments         │
│     charitable  │ │     value       │  │     property            │
│     created_at  │ │     mpaa_flag   │  │     liabilities         │
└────────┬────────┘ │     created_at  │  │     net_worth           │
         │          └─────────────────┘  │     created_at          │
         │ 1:N                           └─────────────────────────┘
         │
         ↓
┌─────────────────┐        ┌─────────────────┐
│      Gifts      │        │     Trusts      │
├─────────────────┤        ├─────────────────┤
│ PK: id          │        │ PK: id          │
│ FK: user_id     │        │ FK: user_id     │
│ FK: profile_id  │        │     type        │
│     amount      │        │     value       │
│     gift_date   │        │     creation    │
│     recipient   │        │     charges     │
│     type (PET)  │        │     created_at  │
│     exemptions  │        └─────────────────┘
│     created_at  │
└─────────────────┘

         ┌────────────────┐
         │  Pension Input │
         │    Periods     │
         ├────────────────┤
         │ PK: id         │
         │ FK: user_id    │
         │ FK: pension_id │
         │     tax_year   │
         │     amount     │
         │     employer   │
         │     member     │
         │     tax_relief │
         │     aa_used    │
         └────────────────┘

┌─────────────────┐        ┌─────────────────┐
│  Bank Accounts  │        │   Products      │
├─────────────────┤        ├─────────────────┤
│ PK: id          │        │ PK: id          │
│ FK: user_id     │        │ FK: user_id     │
│     name        │        │     type        │
│     type        │        │     name        │
│     balance     │        │     provider    │
│     currency    │        │     value       │
│     created_at  │        │     metadata    │
└────────┬────────┘        │     created_at  │
         │ 1:N             └─────────────────┘
         │
         ↓
┌─────────────────┐
│  Transactions   │
├─────────────────┤
│ PK: id          │
│ FK: account_id  │
│     date        │
│     description │
│     amount      │
│     category    │
│     balance     │
│     created_at  │
└─────────────────┘
```

### Database Normalization

**3NF (Third Normal Form)**:
- All tables follow 3NF principles
- No transitive dependencies
- Primary keys uniquely identify records
- Foreign keys maintain referential integrity

**Indexes**:
```sql
-- Primary keys (automatic)
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);

-- Foreign keys for joins
CREATE INDEX idx_gifts_user_id ON gifts(user_id);
CREATE INDEX idx_gifts_profile_id ON gifts(iht_profile_id);
CREATE INDEX idx_pensions_user_id ON enhanced_pensions(user_id);

-- Query optimization
CREATE INDEX idx_gifts_date ON gifts(gift_date);
CREATE INDEX idx_transactions_date ON transactions(date);
CREATE INDEX idx_balance_sheets_date ON balance_sheets(as_of_date);
```

---

## API Architecture

### RESTful API Design

```
Authentication
├── POST   /api/auth/token        Login (returns JWT)
├── POST   /api/auth/register     Register new user
└── GET    /api/auth/me           Get current user

IHT Calculator
├── POST   /api/iht/calculate     Calculate IHT
├── GET    /api/iht/taper-relief/{date}  Get taper relief
├── POST   /api/iht/save-profile  Save IHT profile
└── GET    /api/iht/profile       Get saved profile

IHT Enhanced
├── POST   /api/iht-enhanced/calculate-enhanced
├── POST   /api/iht-enhanced/gift/validate
├── POST   /api/iht-enhanced/trust/ten-year-charge
├── POST   /api/iht-enhanced/trust/exit-charge
├── GET    /api/iht-enhanced/forms/iht400-data
├── GET    /api/iht-enhanced/excepted-estate/check
└── POST   /api/iht-enhanced/quick-succession-relief

Financial Statements
├── GET    /api/financial/balance-sheet/latest
├── GET    /api/financial/balance-sheet
├── POST   /api/financial/balance-sheet
├── PUT    /api/financial/balance-sheet/{id}
├── GET    /api/financial/profit-loss/latest
├── POST   /api/financial/profit-loss
├── GET    /api/financial/cash-flow/latest
├── POST   /api/financial/cash-flow
└── GET    /api/financial/summary

Products
├── GET    /api/products/
├── GET    /api/products/{id}
├── DELETE /api/products/{id}
├── GET    /api/products/pensions/all
├── POST   /api/products/pensions
├── PUT    /api/products/pensions/{id}
├── GET    /api/products/investments/all
├── POST   /api/products/investments
├── GET    /api/products/protection/all
├── POST   /api/products/protection
├── GET    /api/products/portfolio/summary
└── GET    /api/products/retirement/projection

UK Pensions
├── POST   /api/pension/annual-allowance/calculate
├── POST   /api/pension/taper/calculate
├── POST   /api/pension/tax-relief/calculate
├── GET    /api/pension/schemes/all
├── POST   /api/pension/schemes
├── POST   /api/pension/optimization/optimize-contributions
└── POST   /api/pension/projection/monte-carlo

Simulations
├── POST   /api/simulations/portfolio-monte-carlo
└── POST   /api/simulations/iht-scenario

Financial Projections
├── POST   /api/projections/calculate
├── POST   /api/projections/scenario-comparison
└── GET    /api/projections/retirement-readiness

Tax Optimization
├── POST   /api/tax-optimization/analyze-position
├── POST   /api/tax-optimization/optimize-pension
├── POST   /api/tax-optimization/optimize-salary-dividend
└── POST   /api/tax-optimization/comprehensive-report

Portfolio Rebalancing
├── POST   /api/rebalancing/analyze-current-allocation
├── POST   /api/rebalancing/calculate-drift
├── POST   /api/rebalancing/generate-plan
└── GET    /api/rebalancing/tax-efficient-strategies

AI Chat
├── POST   /api/chat/message
└── GET    /api/chat/history

Export
├── GET    /api/export/iht-pdf
├── GET    /api/export/iht-excel
├── GET    /api/export/financial-statements-csv
└── POST   /api/export/import-csv
```

### API Layer Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      FastAPI Router                          │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Route Definition                                      │  │
│  │  - HTTP Method (GET, POST, PUT, DELETE)               │  │
│  │  - URL Path with parameters                           │  │
│  │  - Request/Response models (Pydantic)                 │  │
│  │  - OpenAPI documentation                              │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                   Request Validation                         │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Pydantic Models                                       │  │
│  │  - Type checking                                       │  │
│  │  - Field validation                                    │  │
│  │  - Custom validators                                   │  │
│  │  - Automatic error responses                           │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                   Authentication                             │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  JWT Verification (Depends)                            │  │
│  │  - Extract token from header                           │  │
│  │  - Verify signature                                    │  │
│  │  - Check expiration                                    │  │
│  │  - Load user from database                             │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                   Business Logic                             │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Service Layer                                         │  │
│  │  - IHT calculations                                    │  │
│  │  - Pension calculations                                │  │
│  │  - Tax optimization                                    │  │
│  │  - Portfolio rebalancing                               │  │
│  │  - Financial projections                               │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                   Data Access Layer                          │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  SQLAlchemy ORM                                        │  │
│  │  - Query construction                                  │  │
│  │  - Transaction management                              │  │
│  │  - Relationship loading                                │  │
│  │  - Session management                                  │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                   Response Formatting                        │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Pydantic Response Models                              │  │
│  │  - Serialize to JSON                                   │  │
│  │  - Exclude sensitive fields                            │  │
│  │  - Format dates/numbers                                │  │
│  │  - Add metadata                                        │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## Frontend Architecture

### Component Hierarchy

```
App
├── AuthContext.Provider
│   └── ThemeContext.Provider
│       ├── GlobalStyles
│       └── Router
│           ├── Login
│           ├── Register
│           └── Protected Routes
│               ├── Header
│               │   ├── Logo
│               │   ├── Navigation
│               │   │   ├── Dropdown (Estate Planning)
│               │   │   ├── Dropdown (Investments)
│               │   │   └── Dropdown (Reports)
│               │   ├── ThemeToggle
│               │   └── UserSection
│               │
│               ├── MobileNav (< 768px)
│               │   ├── Hamburger
│               │   └── Drawer
│               │
│               ├── Breadcrumb
│               │
│               ├── Pages
│               │   ├── Dashboard
│               │   │   ├── MetricsGrid
│               │   │   │   ├── MetricCard (Net Worth)
│               │   │   │   ├── MetricCard (Income)
│               │   │   │   ├── MetricCard (Expenses)
│               │   │   │   └── MetricCard (Savings Rate)
│               │   │   ├── IHTDashboardWidget
│               │   │   ├── PensionDashboardWidget
│               │   │   ├── Charts
│               │   │   │   ├── PieChart (Asset Allocation)
│               │   │   │   ├── BarChart (Cash Flow)
│               │   │   │   └── LineChart (Net Worth Trend)
│               │   │   └── QuickActions
│               │   │       ├── Button (Calculate IHT)
│               │   │       ├── Button (Add Transaction)
│               │   │       └── Button (View Projections)
│               │   │
│               │   ├── IHT Calculator Complete
│               │   │   ├── Tabs
│               │   │   │   ├── Tab (Calculator)
│               │   │   │   ├── Tab (Gift History)
│               │   │   │   ├── Tab (Trusts)
│               │   │   │   ├── Tab (Planning)
│               │   │   │   ├── Tab (Valuation)
│               │   │   │   └── Tab (Compliance)
│               │   │   ├── GiftHistoryManager
│               │   │   ├── TrustManager
│               │   │   ├── EstatePlanningScenarios
│               │   │   ├── ValuationTools
│               │   │   └── IHTCompliance
│               │   │
│               │   ├── Retirement Planning UK
│               │   │   ├── Tabs
│               │   │   │   ├── Tab (Overview)
│               │   │   │   ├── Tab (Annual Allowance)
│               │   │   │   ├── Tab (Tax Relief)
│               │   │   │   ├── Tab (Schemes)
│               │   │   │   ├── Tab (Projections)
│               │   │   │   └── Tab (Optimization)
│               │   │   ├── AnnualAllowanceGauge
│               │   │   ├── TaxReliefCalculator
│               │   │   └── SchemeCard (multiple)
│               │   │
│               │   ├── Financial Statements
│               │   │   ├── Tabs
│               │   │   │   ├── Tab (Balance Sheet)
│               │   │   │   ├── Tab (P&L)
│               │   │   │   └── Tab (Cash Flow)
│               │   │   └── Forms + Charts
│               │   │
│               │   ├── Tax Optimization
│               │   │   ├── Tabs
│               │   │   │   ├── Tab (Overview)
│               │   │   │   ├── Tab (Pension)
│               │   │   │   ├── Tab (Salary/Dividend)
│               │   │   │   ├── Tab (ISA)
│               │   │   │   └── Tab (Report)
│               │   │   └── Charts + Recommendations
│               │   │
│               │   ├── Portfolio Rebalancing
│               │   │   ├── Current Allocation
│               │   │   ├── Drift Analysis
│               │   │   ├── Rebalancing Plan
│               │   │   └── Tax Impact
│               │   │
│               │   ├── Financial Projections
│               │   │   ├── Input Form
│               │   │   ├── Scenario Comparison
│               │   │   ├── Charts
│               │   │   └── Retirement Readiness
│               │   │
│               │   └── Chat
│               │       ├── MessageList
│               │       ├── MessageInput
│               │       └── Suggestions
│               │
│               └── ErrorBoundary
│
└── Common Components
    ├── Button
    ├── Card
    ├── Input
    ├── LoadingSpinner
    └── ThemeToggle
```

### State Management

```
┌─────────────────────────────────────────────────────────┐
│                  Global State (Context)                  │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  AuthContext:                                            │
│  ┌────────────────────────────────────────────────┐    │
│  │ • isAuthenticated: boolean                     │    │
│  │ • user: User | null                            │    │
│  │ • token: string | null                         │    │
│  │ • login: (username, password) => Promise       │    │
│  │ • logout: () => void                           │    │
│  │ • loading: boolean                             │    │
│  └────────────────────────────────────────────────┘    │
│                                                          │
│  ThemeContext:                                           │
│  ┌────────────────────────────────────────────────┐    │
│  │ • theme: 'light' | 'dark'                      │    │
│  │ • toggleTheme: () => void                      │    │
│  │ • themeColors: ThemeColors                     │    │
│  └────────────────────────────────────────────────┘    │
│                                                          │
└─────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────┐
│                 Component Local State                    │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  useState:                                               │
│  • Form inputs (controlled components)                   │
│  • Loading states                                        │
│  • Error messages                                        │
│  • UI state (tabs, modals, etc.)                        │
│                                                          │
│  useEffect:                                              │
│  • Data fetching on mount                               │
│  • Subscription to data changes                         │
│  • Cleanup on unmount                                   │
│                                                          │
│  Custom Hooks:                                           │
│  • useAuth() - Access auth context                      │
│  • useTheme() - Access theme context                    │
│  • useDebounce() - Debounce input                       │
│  • useLocalStorage() - Persist to localStorage          │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## Security Architecture

### Authentication & Authorization Flow

```
┌─────────────────────────────────────────────────────────────┐
│                   Security Layers                            │
└─────────────────────────────────────────────────────────────┘

1. Password Security
   ┌──────────────────────────────────────┐
   │  Input: Plain password               │
   │         ↓                            │
   │  bcrypt.hashpw()                     │
   │  • Cost factor: 12 rounds            │
   │  • Auto-generated salt               │
   │         ↓                            │
   │  Hashed password (stored in DB)      │
   │  Example: $2b$12$...60chars...       │
   └──────────────────────────────────────┘

2. JWT Token Security
   ┌──────────────────────────────────────┐
   │  Header:                             │
   │  {                                   │
   │    "alg": "HS256",                   │
   │    "typ": "JWT"                      │
   │  }                                   │
   │         +                            │
   │  Payload:                            │
   │  {                                   │
   │    "sub": "user_id",                 │
   │    "exp": 1234567890                 │
   │  }                                   │
   │         +                            │
   │  Signature:                          │
   │  HMACSHA256(                         │
   │    base64(header) + "." +            │
   │    base64(payload),                  │
   │    secret_key                        │
   │  )                                   │
   │         ↓                            │
   │  JWT: header.payload.signature       │
   └──────────────────────────────────────┘

3. Request Authorization
   ┌──────────────────────────────────────┐
   │  Client Request                      │
   │  Authorization: Bearer <JWT>         │
   │         ↓                            │
   │  Extract token from header           │
   │         ↓                            │
   │  Verify signature with secret        │
   │         ↓                            │
   │  Check expiration time               │
   │         ↓                            │
   │  Extract user_id from payload        │
   │         ↓                            │
   │  Load user from database             │
   │         ↓                            │
   │  Attach user to request              │
   │         ↓                            │
   │  Execute endpoint logic              │
   └──────────────────────────────────────┘

4. CORS (Cross-Origin Resource Sharing)
   ┌──────────────────────────────────────┐
   │  Allowed Origins:                    │
   │  • http://localhost:3000             │
   │  • https://yourdomain.com            │
   │                                      │
   │  Allowed Methods:                    │
   │  • GET, POST, PUT, DELETE            │
   │                                      │
   │  Allowed Headers:                    │
   │  • Content-Type                      │
   │  • Authorization                     │
   │                                      │
   │  Allow Credentials: true             │
   └──────────────────────────────────────┘

5. Input Validation (Pydantic)
   ┌──────────────────────────────────────┐
   │  Request Body:                       │
   │  {                                   │
   │    "value": -100  ← Invalid          │
   │  }                                   │
   │         ↓                            │
   │  Pydantic Validation:                │
   │  value: float = Field(gt=0)          │
   │         ↓                            │
   │  422 Validation Error                │
   │  {                                   │
   │    "detail": "value must be > 0"     │
   │  }                                   │
   └──────────────────────────────────────┘
```

### Security Best Practices

```
✅ Implemented Security Measures:

1. Authentication:
   • JWT tokens with HS256 algorithm
   • Secure password hashing (bcrypt)
   • Token expiration (30 minutes default)
   • HTTPOnly cookies option available

2. Authorization:
   • Protected routes require valid JWT
   • User-specific data isolation
   • Database query filtering by user_id

3. Data Validation:
   • Pydantic models for all inputs
   • Type checking and field validation
   • SQL injection prevention (ORM)

4. CORS:
   • Configured allowed origins
   • Credentials support
   • Method restrictions

5. HTTPS:
   • Production deployment requires HTTPS
   • Secure cookie flags in production

⚠️ Additional Security Recommendations:

1. Rate Limiting:
   • Implement rate limiting on auth endpoints
   • Prevent brute force attacks
   • Use Redis for distributed rate limiting

2. Refresh Tokens:
   • Implement refresh token rotation
   • Longer-lived refresh tokens
   • Secure storage in httpOnly cookies

3. API Keys:
   • For third-party integrations
   • Rotation policy
   • Scoped permissions

4. Audit Logging:
   • Log all authentication attempts
   • Track sensitive data access
   • Compliance requirements

5. Data Encryption:
   • Encrypt sensitive data at rest
   • Use environment variables for secrets
   • Implement key rotation
```

---

## Deployment Architecture

### Development Environment

```
┌─────────────────────────────────────────────────────────────┐
│                    Developer Machine                         │
│                                                              │
│  ┌─────────────────┐         ┌─────────────────┐           │
│  │   Terminal 1    │         │   Terminal 2    │           │
│  │                 │         │                 │           │
│  │  cd backend     │         │  cd frontend    │           │
│  │  source venv    │         │  npm start      │           │
│  │  uvicorn app    │         │                 │           │
│  │  :8000          │         │  :3000          │           │
│  └─────────────────┘         └─────────────────┘           │
│         ↓                            ↓                      │
│  ┌─────────────────┐         ┌─────────────────┐           │
│  │ Backend Server  │         │ React Dev Server│           │
│  │ localhost:8000  │◄────────┤ localhost:3000  │           │
│  │                 │  API    │                 │           │
│  │ • FastAPI       │ Calls   │ • Hot Reload    │           │
│  │ • Auto Reload   │         │ • Source Maps   │           │
│  │ • SQLite DB     │         │ • Dev Tools     │           │
│  └─────────────────┘         └─────────────────┘           │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Docker Development

```
┌─────────────────────────────────────────────────────────────┐
│                      Docker Compose                          │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  docker-compose.yml                                    │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌─────────────────┐         ┌─────────────────┐           │
│  │   backend       │         │    frontend     │           │
│  │   Container     │         │    Container    │           │
│  │                 │         │                 │           │
│  │  Image:         │         │  Image:         │           │
│  │  finplan-backend│         │  finplan-frontend│          │
│  │                 │         │                 │           │
│  │  Port: 8000     │         │  Port: 80       │           │
│  │                 │         │                 │           │
│  │  Volumes:       │         │  (nginx serves  │           │
│  │  • ./backend    │         │   build/)       │           │
│  │  • db volume    │         │                 │           │
│  └─────────────────┘         └─────────────────┘           │
│         ↓                            ↓                      │
│  ┌─────────────────┐         ┌─────────────────┐           │
│  │  SQLite Volume  │         │  nginx.conf     │           │
│  │  (persistent)   │         │  (reverse proxy)│           │
│  └─────────────────┘         └─────────────────┘           │
│                                                              │
└─────────────────────────────────────────────────────────────┘

Access:
• Frontend: http://localhost:3000
• Backend API: http://localhost:8000
• API Docs: http://localhost:8000/docs
```

### Production Deployment

```
┌─────────────────────────────────────────────────────────────┐
│                         Cloud Provider                       │
│                   (AWS / Azure / GCP / etc.)                │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │                    Load Balancer                       │ │
│  │             (HTTPS Termination)                        │ │
│  └───────────────────┬────────────────────────────────────┘ │
│                      │                                       │
│          ┌───────────┴───────────┐                          │
│          ↓                       ↓                          │
│  ┌──────────────┐        ┌──────────────┐                  │
│  │  Frontend    │        │   Backend    │                  │
│  │  Container   │        │  Containers  │                  │
│  │              │        │  (Multiple)  │                  │
│  │  • nginx     │        │              │                  │
│  │  • Static    │        │  • gunicorn  │                  │
│  │    build/    │        │  • workers   │                  │
│  │              │        │  • uvicorn   │                  │
│  │  Port: 80    │        │              │                  │
│  │              │        │  Port: 8000  │                  │
│  └──────────────┘        └───────┬──────┘                  │
│                                  │                          │
│                                  ↓                          │
│                          ┌──────────────┐                   │
│                          │  PostgreSQL  │                   │
│                          │   Database   │                   │
│                          │              │                   │
│                          │  • Primary   │                   │
│                          │  • Replicas  │                   │
│                          │  • Backups   │                   │
│                          └──────────────┘                   │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │           Additional Services                          │ │
│  │  • Redis (caching, sessions)                          │ │
│  │  • S3/Blob Storage (file uploads)                     │ │
│  │  • CloudWatch/Monitoring                              │ │
│  │  • CloudFront/CDN (static assets)                     │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
└─────────────────────────────────────────────────────────────┘

Access:
• Frontend: https://app.yourdomain.com
• Backend API: https://api.yourdomain.com
• Database: Internal network only
```

---

## Technology Stack

### Backend Stack

```
┌─────────────────────────────────────────┐
│           FastAPI Framework             │
│  • Modern Python web framework          │
│  • Async/await support                  │
│  • Automatic OpenAPI docs               │
│  • High performance (ASGI)              │
└─────────────────────────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────────┐
│          Database Layer                 │
│  • SQLAlchemy (ORM)                     │
│  • SQLite (development)                 │
│  • PostgreSQL (production)              │
│  • Alembic (migrations)                 │
└─────────────────────────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────────┐
│         Authentication                  │
│  • python-jose (JWT)                    │
│  • passlib (password hashing)           │
│  • bcrypt (hashing algorithm)           │
└─────────────────────────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────────┐
│          Data Validation                │
│  • Pydantic (data models)               │
│  • email-validator                      │
└─────────────────────────────────────────┘
```

### Frontend Stack

```
┌─────────────────────────────────────────┐
│            React 19.1.1                 │
│  • Component-based architecture         │
│  • Virtual DOM                          │
│  • Hooks (useState, useEffect, etc.)    │
└─────────────────────────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────────┐
│           TypeScript                    │
│  • Static type checking                 │
│  • IDE autocomplete                     │
│  • Compile-time error detection         │
└─────────────────────────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────────┐
│        Styled Components                │
│  • CSS-in-JS                            │
│  • Theme support                        │
│  • Dynamic styling                      │
└─────────────────────────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────────┐
│           Recharts                      │
│  • Data visualization                   │
│  • Responsive charts                    │
│  • Multiple chart types                 │
└─────────────────────────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────────┐
│         React Router                    │
│  • Client-side routing                  │
│  • Protected routes                     │
│  • URL parameters                       │
└─────────────────────────────────────────┘
```

---

## Design Patterns

### Backend Design Patterns

**1. Repository Pattern**
```python
# Abstraction over database operations
class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: int) -> User:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_username(self, username: str) -> User:
        return self.db.query(User).filter(User.username == username).first()

    def create(self, user_data: dict) -> User:
        user = User(**user_data)
        self.db.add(user)
        self.db.commit()
        return user
```

**2. Service Layer Pattern**
```python
# Business logic separation
class IHTService:
    def __init__(self):
        self.calculator = IHTCalculator()

    def calculate_iht(self, estate_data: dict, user_id: int) -> dict:
        # Fetch user gifts from database
        gifts = self._get_user_gifts(user_id)

        # Perform calculation
        result = self.calculator.calculate(estate_data, gifts)

        # Save result
        self._save_profile(result, user_id)

        return result
```

**3. Dependency Injection**
```python
# FastAPI built-in DI
@router.get("/protected")
async def protected_route(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Dependencies automatically injected
    return {"user": current_user.username}
```

### Frontend Design Patterns

**1. Container/Presentational**
```typescript
// Container (logic)
const DashboardContainer: React.FC = () => {
  const [data, setData] = useState(null);

  useEffect(() => {
    fetchData().then(setData);
  }, []);

  return <DashboardPresentation data={data} />;
};

// Presentational (UI)
const DashboardPresentation: React.FC<{ data: any }> = ({ data }) => {
  return <div>{/* Render data */}</div>;
};
```

**2. Custom Hooks**
```typescript
// Reusable logic
const useIHTCalculator = () => {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const calculate = async (data: IHTInput) => {
    setLoading(true);
    const result = await api.calculateIHT(data);
    setResult(result);
    setLoading(false);
  };

  return { result, loading, calculate };
};
```

**3. Compound Components**
```typescript
// Flexible composition
<Card>
  <Card.Header>
    <Card.Title>Title</Card.Title>
  </Card.Header>
  <Card.Body>
    Content
  </Card.Body>
  <Card.Footer>
    <Button>Action</Button>
  </Card.Footer>
</Card>
```

---

## Performance Considerations

### Backend Optimization

```
1. Database Queries:
   • Use indexes on frequently queried columns
   • Eager loading for relationships (avoid N+1)
   • Query result pagination
   • Connection pooling

2. Caching:
   • Redis for session storage
   • Cache expensive calculations
   • API response caching (with TTL)

3. Async Operations:
   • Use async/await for I/O operations
   • Background tasks for long-running jobs
   • Celery for distributed task queue

4. API Response:
   • Compress responses (gzip)
   • Return only necessary fields
   • Use pagination for lists
```

### Frontend Optimization

```
1. Code Splitting:
   • Route-based code splitting
   • Lazy loading components
   • Dynamic imports

2. Memoization:
   • useMemo for expensive calculations
   • useCallback for function references
   • React.memo for component memoization

3. Bundle Size:
   • Tree shaking (remove unused code)
   • Minification and uglification
   • Optimize images and assets

4. Rendering:
   • Virtualization for long lists
   • Debounce user inputs
   • Throttle scroll events
```

---

## Monitoring & Observability

```
┌─────────────────────────────────────────┐
│           Application Logs              │
│  • Structured logging (JSON)            │
│  • Log levels (DEBUG, INFO, ERROR)      │
│  • Request/response logging             │
└─────────────────────────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────────┐
│          Metrics Collection             │
│  • Request count                        │
│  • Response time                        │
│  • Error rate                           │
│  • Database query time                  │
└─────────────────────────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────────┐
│         Error Tracking                  │
│  • Exception logging                    │
│  • Stack traces                         │
│  • User context                         │
│  • Sentry/Rollbar integration           │
└─────────────────────────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────────┐
│         Health Checks                   │
│  • /health endpoint                     │
│  • Database connectivity                │
│  • External service status              │
└─────────────────────────────────────────┘
```

---

*Last Updated: 2025-09-30*
*Version: 1.0.0*