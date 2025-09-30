## Refactored Feature Analysis by Category

### 0. Technology Stack (Refactored)

**Frontend:**

* React (Static hosting via Netlify/Vercel or any static-compatible host)
* Recharts (2.15.3), html2canvas, jsPDF

**Backend:**

* FastAPI (Python 3.9+)

  * Lightweight, async-ready REST framework
  * Replaces previous Node.js/Express API
  * Compatible with OpenAI integration, PDF generation, and financial calculations
  * Hosted via supported Python environment on your existing provider (no Django needed)

**Database:**

* PostgreSQL or SQLite (based on hosting support)
* SQLAlchemy ORM (Python-native)

**Authentication:**

* JWT-based user sessions
* Secure token handling

**Other Tools:**

* Bcrypt for password hashing
* Pydantic for validation
* Alembic for migrations

---

### 1. Core Financial Data Management

**Data Extraction Service**

* Intelligent parsing of user messages to extract:

  * Income sources and amounts
  * Expense categories and values
  * Financial goals with targets
  * Risk tolerance assessment
  * Asset and debt information
* Real-time processing on message updates
* Data persistence with database and localStorage backups

**Inheritance Tax (IHT) Planning Data Integration**

* Track estate valuation, liabilities, nil-rate band, and residence nil-rate band (RNRB)
* Input historical gifts, trust assignments, and apply taper relief
* Calculate IHT liabilities and simulate future estate growth
* Store beneficiary and will data for inheritance distribution

**Personal Financial Statements Management**

* Generate personal Balance Sheet, Profit & Loss (P&L), Income Statement, and Cash Flow Statement
* Automatically compile data from income, expenses, assets, and liabilities
* Provide real-time updates and downloadable reports
* Visualize personal financial health and trends

---

### 2. AI-Powered Chat Interface

* Context-aware financial chat with OpenAI API
* Real-time typing and message status
* Custom intents for:

  * IHT exposure questions
  * Financial statement insights ("What’s my current cash flow?")
  * Strategy suggestions ("How can I improve my P&L?")

---

### 3. Advanced Dashboard System

* Specialized dashboards for:

  * Retirement
  * Investment
  * Savings
  * Protection
  * Comprehensive Planning
  * **Estate & IHT Planning** (NEW)
  * **Personal Financial Statements Overview** (NEW)

**Dynamic Metrics**

* Real-time IHT calculation (effective rate, taxable estate, tax due)
* Real-time Cash Flow, Net Income, and Equity calculations
* Progress toward financial health improvement goals

---

### 4. Product Detail Management

**Expanded Product Types**

* Pension (workplace, SIPP)
* Investment (ISA, GIA)
* Savings (instant access, fixed term, **personal bank accounts**) (UPDATED)
* Protection (life, CI)
* **Estate Planning Tools** (NEW: Life insurance for IHT, Trusts, Will trackers)

**Detailed Analytics**

* Performance tracking for IHT coverage products
* Real-time metrics for financial statement components

**Document Management**

* Attach estate plans, wills, trust deeds
* PDF downloads of estate snapshot, tax forecasts, and personal financial statements

---

### 5. Data Visualization & Analytics

* Recharts 2.15.3 for interactive estate and financial statement charts
* IHT Forecast timelines
* Cash flow visualizations and net income trends

---

### 6. Document Processing & Export

* jsPDF 2.5.1 for IHT and personal financial reports
* html2canvas for snapshot exports
* Export options for financial statements and estate plans

---

### 7. Advanced Routing & Navigation

* Product-specific routes for IHT Tools and Financial Statements
* Protected modules under authentication layer
* Breadcrumbs for Estate → Trusts → Gifts, and Finance → P&L → Cash Flow, etc.

---

### Database Schema & Data Models (Updated)

**New Core Entities**

* `IHTProfile`: estateValue, liabilities, bandsUsed, taxDue
* `Gift`: amount, date, relation, taperRelief
* `Trust`: type, value, assignedBeneficiaries
* `FinancialStatement`: type (P&L, Balance Sheet, Cash Flow), period, values
* `Will`: beneficiaries, distributionRules
* `PersonalBankAccount` (moved under Savings): accountType, balance, transactionList

**Updated Relationships**

* Users → IHTProfile (one-to-one)
* Users → FinancialStatements (one-to-many)
* Users → PersonalBankAccounts (one-to-many)
* IHTProfile → Assets, Gifts, Trusts, Will

---

### Security & Data Protection

* Add estate-specific access controls for sensitive family planning data
* Encryption of will, trust, and financial statement information

---

### Planned Features (Phase 3 Additions)

* Monte Carlo for IHT scenario projections
* Real-time Open Banking feed for personal bank accounts
* Legal doc integrations (e.g. upload will and auto-parse)

---

This refactor integrates legacy systems with new high-value estate and financial tracking functionality, powered by a modern Python FastAPI backend and static React frontend — fully compatible with your current hosting setup.
