# Financial Planning Application

A comprehensive financial planning application with **goal-based modules** that organize your financial life around 5 key life goals: Protection, Savings, Investment, Retirement, and IHT Planning.

**Version 2.0** introduces a goal-based approach that makes financial planning clearer, more focused, and easier to understand.

## ✨ Key Features

### Goal-Based Modules (v2.0) 🆕
The application organizes all financial planning around **5 life goals**:

1. **Protection Module** - Ensure adequate coverage against life's risks
   - Life insurance, critical illness, income protection
   - Coverage needs analysis calculator
   - Gap analysis and premium tracking

2. **Savings Module** - Build and maintain emergency funds
   - Emergency fund tracking (months of expenses)
   - Savings goals with progress tracking
   - Multiple savings account management

3. **Investment Module** - Grow your wealth through investments
   - Portfolio tracking and performance analysis
   - Asset allocation and rebalancing tools
   - Gain/loss tracking with benchmarking

4. **Retirement Module** - Plan for a comfortable retirement
   - Pension scheme management
   - Retirement income projections
   - Annual Allowance tracking with taper
   - Monte Carlo simulations

5. **IHT Planning Module** - Minimize inheritance tax liability
   - IHT calculator with scenario comparison
   - Gift tracking (7-year rule with taper relief)
   - Trust management
   - Estate planning strategies

Each module has:
- **Dashboard** - Overview with key metrics and status
- **Management** - CRUD operations for module products
- **Analytics** - Detailed insights and charts
- **Specialized Tools** - Module-specific calculators and features

### UK Inheritance Tax Calculator (Complete)
- **Real-time IHT calculations** with 2024/25 UK tax rates
- **7-Year Gift Timeline** - Interactive visualization with taper relief
- **Estate Planning Scenarios** - Compare and optimize multiple strategies
- **Gift History Management** - Full CRUD with exemption tracking
- **Trust Management Suite** - 10-year periodic and exit charge calculators
- **Exemption Tracker** - Optimize use of all IHT exemptions
- **Valuation Tools** - Professional asset valuation suite
- **IHT Compliance Dashboard** - IHT400 preparation and deadline tracking
- **61 comprehensive tests** with 100% pass rate covering complete UK tax law

### UK Pension Planning System (Complete)
- Annual Allowance tracking with taper calculations (£200k-£360k income)
- Money Purchase Annual Allowance (MPAA) monitoring
- 3-year carry-forward calculations with proper ordering
- Tax relief optimization (20%, 40%, 45% rates + Scotland)
- Auto-enrolment compliance checking
- Salary sacrifice vs relief at source comparison
- Multi-scheme aggregation and management
- Monte Carlo retirement projections
- Lifetime allowances (LSA £268,275, LSDBA £1,073,100)

### Financial Management
- **Financial Statements**: Balance Sheet, Profit & Loss, Cash Flow analysis
- **Product Portfolio**: Pensions, Investments, Protection products
- **Bank Accounts**: Transaction tracking and management
- **AI Chat Assistant**: OpenAI-powered financial advice
- **Data Export**: PDF reports and Excel/CSV export

### Advanced Analytics
- **Tax Optimization** - Smart tax planning strategies and recommendations
- **Portfolio Rebalancing** - Automated drift analysis and rebalancing suggestions
- **Financial Projections** - Multi-year scenario modeling and forecasting
- **Monte Carlo Simulations** - Probabilistic retirement outcome analysis

### User Experience
- **Narrative Storytelling Dashboard** - Conversational, educational approach to financial data
- **Learning Centre** - In-app documentation browser with full-text search and video tutorials
- **Mobile Responsive** - Fully responsive design for all screen sizes
- **Dark Mode** - Professional light and dark themes with seamless switching
- **Interactive Charts** - Recharts visualizations for data analysis
- **Progressive Disclosure** - "Tell me more" sections reduce cognitive load
- **Protected Routes** - Secure JWT-based authentication
- **Settings Hub** - Centralized user preferences and account management

## 📚 Documentation

### Design System
- **[Style Guide](./STYLEGUIDE.md)** - Complete design system with narrative storytelling approach
- **[Visual Mockups](./frontend/public/dashboard-mockups.html)** - 5 dashboard layout options
- **[Development Guide](./CLAUDE.md)** - Architectural patterns and development guidelines

### IHT Documentation Suite
- **[User Guide](./docs/IHT_USER_GUIDE.md)** - Complete how-to guide with examples
- **[Calculation Methodology](./docs/IHT_CALCULATION_METHODOLOGY.md)** - Technical specifications
- **[Compliance Checklist](./docs/IHT_COMPLIANCE_CHECKLIST.md)** - HMRC compliance guide
- **[Documentation Index](./docs/README.md)** - Overview and navigation

Perfect for end users, developers, executors, and auditors.

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 16+
- SQLite (included with Python)

### One-Command Setup

```bash
# Start both backend and frontend
./start.sh
```

This will:
1. Start backend API on http://localhost:8000
2. Start frontend on http://localhost:3000
3. Open API documentation at http://localhost:8000/docs

### Manual Setup

<details>
<summary>Click to expand manual setup instructions</summary>

#### Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create database with seed data
python seed_data.py

# Run server
uvicorn app.main:app --reload --port 8000
```

#### Frontend Setup

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

</details>

## 🔑 Test Credentials

### Demo User (with full seed data)
- **Username**: `demouser` or **Email**: `demo@example.com`
- **Password**: `demo123`

### Test User (basic account)
- **Username**: `testuser` or **Email**: `test@example.com`
- **Password**: `testpass123`

## 📍 Application Routes

### Main Routes
- `/dashboard` - Goal-based modules dashboard with narrative storytelling
- `/login` - User login
- `/register` - User registration
- `/settings` - User preferences, theme, and account management
- `/learning-centre` - In-app documentation and tutorials

### Goal-Based Module Routes (v2.0) 🆕

#### Protection Module
- `/modules/protection/dashboard` - Protection overview and status
- `/modules/protection/portfolio` - Manage protection policies
- `/modules/protection/analytics` - Coverage analytics
- `/modules/protection/needs-analysis` - Calculate coverage needs

#### Savings Module
- `/modules/savings/dashboard` - Savings overview and emergency fund status
- `/modules/savings/accounts` - Manage savings accounts
- `/modules/savings/goals` - Set and track savings goals
- `/modules/savings/analytics` - Savings trends and analytics

#### Investment Module
- `/modules/investment/dashboard` - Investment portfolio overview
- `/modules/investment/portfolio` - Manage investments
- `/modules/investment/analytics` - Performance analytics
- `/modules/investment/rebalancing` - Portfolio rebalancing tool

#### Retirement Module
- `/modules/retirement/dashboard` - Retirement readiness overview
- `/modules/retirement/pensions` - Manage pension schemes
- `/modules/retirement/projections` - Retirement income projections
- `/modules/retirement/monte-carlo` - Monte Carlo simulations

#### IHT Planning Module
- `/modules/iht/dashboard` - IHT planning overview
- `/modules/iht/calculator` - IHT calculator with scenarios
- `/modules/iht/gifts` - Gift tracking (7-year rule)
- `/modules/iht/trusts` - Trust management

### Legacy Routes (Deprecated - Will Redirect) ⚠️
- `/iht-calculator` → redirects to `/modules/iht/calculator`
- `/iht-calculator-enhanced` → redirects to `/modules/iht/dashboard`
- `/iht-calculator-complete` → redirects to `/modules/iht/dashboard`
- `/iht-compliance` - IHT400 compliance (unchanged)
- `/retirement-planning-uk` - UK pension features (unchanged)
- `/financial-statements` - Balance Sheet, P&L, Cash Flow (unchanged)
- `/financial-projections` - Multi-year projections (unchanged)
- `/tax-optimization` - Tax strategies (unchanged)
- `/products` → Use module-specific routes instead
- `/pensions` → redirects to `/modules/retirement/pensions`
- `/investments` → redirects to `/modules/investment/portfolio`
- `/protection` → redirects to `/modules/protection/portfolio`
- `/bank-accounts` → redirects to `/modules/savings/accounts`
- `/portfolio-analytics` → redirects to `/modules/investment/analytics`
- `/portfolio-rebalancing` → redirects to `/modules/investment/rebalancing`
- `/monte-carlo` → redirects to `/modules/retirement/monte-carlo`

### Other Features
- `/chat` - AI-powered financial assistant

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - ORM for database management
- **PostgreSQL/SQLite** - Database options
- **JWT** - Secure authentication
- **OpenAI API** - AI chat integration

### Frontend
- **React 19** - UI framework
- **TypeScript** - Type-safe JavaScript
- **Styled Components** - CSS-in-JS styling
- **Recharts** - Data visualization
- **React Router v6** - Client-side routing

## 🧪 Testing

### Run IHT Test Suite (61 Tests - 100% Pass Rate)
```bash
cd backend && source venv/bin/activate
python -m pytest tests/test_iht_enhanced.py -v
```

### Test Categories
- **Taper Relief** (15 tests) - All 7-year taper scenarios
- **RNRB Tapering** (9 tests) - £2M+ estate calculations
- **Edge Cases** (8 tests) - GWR/POAT, Quick Succession Relief
- **Integration** (3 tests) - Multi-year tracking, trust lifecycle
- **Compliance** (3 tests) - Form generation, payment calculations

### Run All Tests
```bash
# Backend tests with coverage
cd backend && pytest --cov=app tests/

# Frontend tests
cd frontend && npm test -- --coverage --watchAll=false

# TypeScript compilation check
cd frontend && npm run build
```

## 🐳 Docker Deployment

```bash
# Build and run with docker-compose
docker-compose up --build

# Or build individual images
docker build -t finplan-backend ./backend
docker build -t finplan-frontend ./frontend
```

## 📊 API Documentation

Interactive API documentation available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔧 Troubleshooting

### Port Already in Use
```bash
# Kill process on port 3000 (frontend)
lsof -i :3000 | grep LISTEN | awk '{print $2}' | xargs kill -9

# Kill process on port 8000 (backend)
lsof -i :8000 | grep LISTEN | awk '{print $2}' | xargs kill -9
```

### Backend Won't Start
- Ensure virtual environment is activated: `source backend/venv/bin/activate`
- Install dependencies: `pip install -r backend/requirements.txt`
- Create database: `python backend/seed_data.py`

### Frontend Compilation Errors
- Clear node_modules: `rm -rf node_modules && npm install`
- Check Node version: `node --version` (should be 16+)
- Clear cache: `npm cache clean --force`

### Login Issues
- Clear browser localStorage (F12 → Application → Local Storage → Clear All)
- Ensure both backend and frontend are running
- Check browser console for errors (F12 → Console)

### Database Issues
- Reset database: `cd backend && python seed_data.py`
- Check `.env` file exists with correct `DATABASE_URL`
- For PostgreSQL, verify connection credentials

## 📦 Project Structure

```
finPlanFull/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── api/         # API endpoints
│   │   │   ├── auth/           # Authentication
│   │   │   ├── modules/        # 🆕 Goal-based module APIs
│   │   │   │   ├── protection/ # Protection module API
│   │   │   │   ├── savings/    # Savings module API
│   │   │   │   ├── investment/ # Investment module API
│   │   │   │   ├── retirement/ # Retirement module API
│   │   │   │   └── iht/        # IHT Planning module API
│   │   │   ├── iht/            # ⚠️ Legacy IHT API (deprecated)
│   │   │   ├── pension/        # UK pension (3 routers)
│   │   │   ├── banking/        # Bank accounts
│   │   │   ├── financial_statements/ # Financial data
│   │   │   ├── products/       # ⚠️ Legacy product API (deprecated)
│   │   │   ├── chat.py         # AI chat
│   │   │   ├── docs.py         # Learning Centre API
│   │   │   ├── export.py       # PDF/Excel export
│   │   │   ├── simulations.py  # Monte Carlo
│   │   │   ├── projections.py  # Financial projections
│   │   │   ├── tax_optimization.py
│   │   │   └── rebalancing.py
│   │   ├── models/      # SQLAlchemy models (10+ models)
│   │   ├── core/        # Configuration & security
│   │   ├── db/          # Database initialization
│   │   └── utils/       # Utility functions
│   ├── tests/           # Test suites (10+ files, 189+ tests)
│   │   ├── test_modules_protection.py  # 18 tests
│   │   ├── test_modules_savings.py     # 17 tests
│   │   ├── test_modules_investment.py  # 13 tests
│   │   ├── test_modules_retirement.py  # 14 tests
│   │   ├── test_modules_iht.py         # 21 tests
│   │   ├── test_iht_enhanced.py        # 61 IHT tests
│   │   ├── test_docs_api.py            # 34 docs tests
│   │   └── test_pension.py             # 12 pension tests
│   └── seed_data.py     # Database seeding
├── frontend/            # React 19 + TypeScript
│   └── src/
│       ├── components/  # React components
│       │   ├── common/       # 11 reusable components
│       │   ├── modules/      # 🆕 Goal-based module components
│       │   ├── docs/         # 5 Learning Centre components
│       │   ├── iht/          # 12 IHT components
│       │   ├── pension/      # 6 pension components
│       │   └── layout/       # Header, navigation
│       ├── pages/       # 45+ page components
│       │   ├── modules/      # 🆕 Module pages (20 pages)
│       │   │   ├── protection/   # 4 Protection pages
│       │   │   ├── savings/      # 4 Savings pages
│       │   │   ├── investment/   # 4 Investment pages
│       │   │   ├── retirement/   # 4 Retirement pages
│       │   │   └── iht/          # 4 IHT Planning pages
│       │   └── ...          # Other pages (dashboard, settings, etc.)
│       ├── services/    # API client services (3 files)
│       ├── styles/      # Theme system (light/dark)
│       ├── types/       # TypeScript definitions
│       └── context/     # React contexts (theme, auth)
├── docs/                # 10 comprehensive documentation files
│   ├── IHT_USER_GUIDE.md
│   ├── IHT_CALCULATION_METHODOLOGY.md
│   ├── IHT_COMPLIANCE_CHECKLIST.md
│   ├── USER_GUIDE.md                    # 🆕 v2.0 with modules
│   ├── API_DOCUMENTATION.md             # 🆕 v2.0 with modules
│   ├── MIGRATION_GUIDE.md               # 🆕 v1.x → v2.0 guide
│   ├── ARCHITECTURE.md
│   ├── DEVELOPER_DOCUMENTATION.md
│   ├── VIDEO_TUTORIALS.md               # 🆕 v2.0 with modules
│   └── README.md
├── .github/workflows/   # CI/CD with GitHub Actions
├── docker-compose.yml   # Docker configuration
├── CLAUDE.md           # Developer guide (v2.0 updated)
├── STYLEGUIDE.md       # Design system documentation
├── README.md           # This file (v2.0)
└── start.sh            # Quick start script
```

## 🎯 Development Workflow

For developers working on this project, see [CLAUDE.md](./CLAUDE.md) for:
- Architecture overview
- Development commands
- Testing requirements
- Common gotchas
- API endpoints
- Troubleshooting guide

## 🚧 Roadmap

### Completed ✅
- [x] **Goal-Based Modules (v2.0)** - 5 life goal modules with 20 pages
- [x] **Module API Layer** - Consistent endpoints across all modules
- [x] **Module Testing Suite** - 83 comprehensive API tests
- [x] **Migration Documentation** - Complete v1.x → v2.0 guide
- [x] UK IHT Calculator Phase 2
- [x] UK Pension Planning System
- [x] Monte Carlo Simulations
- [x] Comprehensive Testing Suite (189+ total tests: 83 module + 61 IHT + 34 docs + 11 frontend)
- [x] Learning Centre with Documentation Browser
- [x] Tax Optimization Module
- [x] Portfolio Rebalancing Tools
- [x] Multi-year Financial Projections
- [x] Narrative Storytelling Dashboard
- [x] Settings & Preferences Hub

### In Progress 🚧
- [ ] Frontend Component Tests (Module components)
- [ ] E2E Testing Framework (Playwright/Cypress)
- [ ] Legacy route deprecation cleanup (v2.1)

### Planned 📋
- [ ] Multi-currency support
- [ ] Advanced AI-powered insights per module
- [ ] Open Banking integration
- [ ] Mobile app (React Native) with module structure
- [ ] Multi-language support (i18n)
- [ ] Real-time market data integration
- [ ] Goal progress tracking and notifications

## 📅 Latest Updates

### 2025-10-01 - Goal-Based Modules Launch (v2.0) 🆕
- **5 Life Goal Modules**: Protection, Savings, Investment, Retirement, IHT Planning
- **20 New Module Pages**: 4 pages per module (Dashboard, Management, Analytics, Tools)
- **Module API Layer**: Consistent endpoints across all 5 modules
- **83 New API Tests**: Comprehensive module coverage (Protection: 18, Savings: 17, Investment: 13, Retirement: 14, IHT: 21)
- **Migration Guide**: Complete v1.x → v2.0 transition documentation
- **Updated Documentation**: USER_GUIDE.md, API_DOCUMENTATION.md, VIDEO_TUTORIALS.md
- **Narrative Storytelling**: Dashboard redesigned with conversational approach
- **Automatic Redirects**: Legacy routes redirect to new module structure

### 2025-09-30 - Learning Centre Launch ✅
- In-app documentation browser with 10 comprehensive guides
- Full-text search across all documentation (<100ms response time)
- 8 video tutorial series (34 videos, ~180 minutes of content)
- 34 backend API tests + 11 frontend component tests (100% pass rate)
- Context-aware help system with keyboard shortcuts
- Category-based organization with 9 documentation categories

### 2025-09-30 - Enhanced Features Portfolio ✅
- Tax optimization strategies and recommendations
- Portfolio rebalancing with drift analysis
- Multi-year financial projections
- Settings page with centralized preferences
- Narrative storytelling dashboard with progressive disclosure

### 2025-09-29 - IHT Testing Suite Complete ✅
- 61 comprehensive IHT tests with 100% pass rate
- Complete UK tax law coverage (2024/25 tax year)
- All edge cases: GWR/POAT, Quick Succession Relief, foreign assets
- Full compliance testing: Form generation, payment calculations

### 2025-09-29 - UK Pension Planning Complete ✅
- Annual Allowance with taper calculations
- MPAA management and monitoring
- Complete tax relief calculations
- Multi-scheme pension management

## 🤝 Contributing

This project is under active development. For contribution guidelines, see [CLAUDE.md](./CLAUDE.md).

## 📄 License

This project is proprietary and confidential. All rights reserved.

---

**Quick Links**:
- [API Documentation](http://localhost:8000/docs)
- [Developer Guide](./CLAUDE.md)
- [IHT User Guide](./docs/IHT_USER_GUIDE.md)
- [Testing Framework](./TESTING_FRAMEWORK.md)