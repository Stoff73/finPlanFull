# Financial Planning Application

A comprehensive financial planning application featuring UK Inheritance Tax calculations, pension planning, financial statements management, and AI-powered financial advice.

## ✨ Key Features

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
- `/dashboard` - Narrative storytelling dashboard with financial metrics
- `/login` - User login
- `/register` - User registration
- `/settings` - User preferences, theme, and account management

### IHT Calculator
- `/iht-calculator` - Basic IHT Calculator
- `/iht-calculator-enhanced` - Enhanced IHT calculator with advanced features
- `/iht-calculator-complete` - Complete IHT suite with all Phase 2 tools
- `/iht-compliance` - IHT400 preparation and compliance dashboard

### Financial Planning
- `/financial-statements` - Balance Sheet, P&L, Cash Flow
- `/retirement-planning` - General retirement planning
- `/retirement-planning-uk` - UK pension planning (AA/taper/MPAA)
- `/portfolio-analytics` - Portfolio analysis and insights
- `/portfolio-rebalancing` - Portfolio rebalancing tools
- `/financial-projections` - Multi-year financial projections
- `/tax-optimization` - Tax optimization strategies

### Products & Accounts
- `/products` - Product overview
- `/products/pensions` - Pension management
- `/products/investments` - Investment tracking
- `/products/protection` - Protection products
- `/bank-accounts` - Bank account management

### Advanced Features
- `/chat` - AI-powered financial assistant
- `/monte-carlo` - Monte Carlo simulations
- `/learning-centre` - In-app documentation and tutorials

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
│   │   ├── api/         # API endpoints (14 routers)
│   │   │   ├── auth/           # Authentication
│   │   │   ├── iht/            # IHT calculations
│   │   │   ├── pension/        # UK pension (3 routers)
│   │   │   ├── banking/        # Bank accounts
│   │   │   ├── financial_statements/ # Financial data
│   │   │   ├── products/       # Product management
│   │   │   ├── chat.py         # AI chat
│   │   │   ├── docs.py         # Learning Centre API
│   │   │   ├── export.py       # PDF/Excel export
│   │   │   ├── simulations.py  # Monte Carlo
│   │   │   ├── projections.py  # Financial projections
│   │   │   ├── tax_optimization.py
│   │   │   └── rebalancing.py
│   │   ├── models/      # SQLAlchemy models (10 models)
│   │   ├── core/        # Configuration & security
│   │   ├── db/          # Database initialization
│   │   └── utils/       # Utility functions
│   ├── tests/           # Test suites (9 files, 106+ tests)
│   └── seed_data.py     # Database seeding
├── frontend/            # React 19 + TypeScript
│   └── src/
│       ├── components/  # React components
│       │   ├── common/       # 11 reusable components
│       │   ├── docs/         # 5 Learning Centre components
│       │   ├── iht/          # 12 IHT components
│       │   ├── pension/      # 6 pension components
│       │   └── layout/       # Header, navigation
│       ├── pages/       # 22 page components
│       ├── services/    # API client services (3 files)
│       ├── styles/      # Theme system (light/dark)
│       ├── types/       # TypeScript definitions
│       └── context/     # React contexts (theme, auth)
├── docs/                # 9 comprehensive documentation files
│   ├── IHT_USER_GUIDE.md
│   ├── IHT_CALCULATION_METHODOLOGY.md
│   ├── IHT_COMPLIANCE_CHECKLIST.md
│   ├── USER_GUIDE.md
│   ├── API_DOCUMENTATION.md
│   ├── ARCHITECTURE.md
│   ├── DEVELOPER_DOCUMENTATION.md
│   ├── VIDEO_TUTORIALS.md
│   └── README.md
├── .github/workflows/   # CI/CD with GitHub Actions
├── docker-compose.yml   # Docker configuration
├── CLAUDE.md           # Developer guide (comprehensive)
├── STYLEGUIDE.md       # Design system documentation
├── README.md           # This file
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
- [x] UK IHT Calculator Phase 2
- [x] UK Pension Planning System
- [x] Monte Carlo Simulations
- [x] Comprehensive Testing Suite (61 IHT tests, 34 docs tests, 11 frontend tests)
- [x] Learning Centre with Documentation Browser
- [x] Tax Optimization Module
- [x] Portfolio Rebalancing Tools
- [x] Multi-year Financial Projections
- [x] Narrative Storytelling Dashboard
- [x] Settings & Preferences Hub

### In Progress 🚧
- [ ] Frontend integration refinements
- [ ] Documentation polish and updates

### Planned 📋
- [ ] Multi-currency support
- [ ] Advanced AI-powered tax optimization
- [ ] Open Banking integration
- [ ] Mobile app (React Native)
- [ ] Multi-language support (i18n)
- [ ] Real-time market data integration

## 📅 Latest Updates

### 2025-09-30 - Learning Centre Launch ✅
- In-app documentation browser with 9 comprehensive guides
- Full-text search across all documentation (<100ms response time)
- 6 video tutorial series (27 videos, ~160 minutes of content)
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

### 2025-09-29 - IHT Calculator Phase 2 Complete ✅
- 7 new advanced IHT components
- 2 new pages (Complete Suite + Compliance Dashboard)
- Enhanced visualizations and optimization tools
- Full TypeScript support

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