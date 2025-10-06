# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## CRITICAL DEVELOPMENT RULES

**IMPORTANT**: When making changes:
- ONLY modify the specific feature requested
- NEVER alter unrelated modules or functionality
- TEST the application to ensure existing features work
- MAINTAIN backward compatibility
- FOLLOW established architectural patterns

## ARCHITECTURE OVERVIEW

### System Architecture
- **Backend**: FastAPI monolith with modular API routers
- **Frontend**: React SPA with TypeScript and styled-components
- **Database**: SQLite (dev) / PostgreSQL (prod) via SQLAlchemy ORM
- **Authentication**: JWT tokens stored in localStorage on frontend

### Backend Module Organization
```
backend/app/
├── api/              # API route handlers
│   ├── auth/         # Authentication (login, register, token)
│   ├── modules/      # **NEW: Goal-based module APIs**
│   │   ├── protection/   # Protection module (policies, analytics, needs analysis)
│   │   ├── savings/      # Savings module (accounts, goals, analytics)
│   │   ├── investment/   # Investment module (portfolio, analytics, rebalancing)
│   │   ├── retirement/   # Retirement module (pensions, projections, monte-carlo)
│   │   └── iht/          # IHT Planning module (calculator, gifts, trusts)
│   ├── iht/          # **DEPRECATED**: Use /api/modules/iht instead
│   ├── financial_statements/  # Balance sheet, P&L, cash flow
│   ├── products/     # **DEPRECATED**: Use module-specific endpoints
│   ├── pension/      # UK pension-specific (AA, taper, MPAA, optimization, schemes)
│   ├── banking/      # Bank accounts and transactions
│   ├── chat.py       # AI chat integration
│   ├── export.py     # PDF/Excel export
│   ├── simulations.py # Monte Carlo projections
│   ├── projections.py # Multi-year financial projections
│   ├── tax_optimization.py # Tax planning and optimization
│   ├── rebalancing.py # Portfolio rebalancing
│   ├── docs.py       # Learning Centre documentation API
│   ├── iht_refactored.py # Enhanced IHT calculations
│   └── dashboard.py  # Main dashboard aggregation
├── models/           # SQLAlchemy models (user, iht, financial, product, chat, pension, docs_metadata, module_goal, module_metric)
├── core/             # Configuration, security, dependencies
└── db/               # Database initialization
```

**Goal-Based Modules** (NEW in v2.0):
- **Protection**: `/api/modules/protection` - Insurance/protection planning
- **Savings**: `/api/modules/savings` - Cash savings and emergency fund
- **Investment**: `/api/modules/investment` - Investment portfolio management
- **Retirement**: `/api/modules/retirement` - Pension planning
- **IHT Planning**: `/api/modules/iht` - Inheritance tax planning

Each module has consistent endpoints:
- `/dashboard` - Comprehensive dashboard data
- `/summary` - Quick summary for main dashboard card
- CRUD operations for module-specific entities
- `/analytics` - Module-specific analytics

### Frontend Component Hierarchy
```
frontend/src/
├── pages/            # Full page components with data fetching (27+ pages)
│   ├── Dashboard.tsx                # **NEW**: Narrative storytelling main dashboard
│   ├── Settings.tsx                 # User preferences & account settings
│   ├── LearningCentre.tsx          # Documentation browser
│   ├── modules/                     # **NEW**: Goal-based module pages
│   │   ├── protection/
│   │   │   ├── ProtectionDashboard.tsx       # Protection module dashboard
│   │   │   ├── ProtectionPortfolio.tsx       # Manage policies
│   │   │   ├── ProtectionAnalytics.tsx       # Coverage analytics
│   │   │   └── ProtectionNeedsAnalysis.tsx   # Needs calculator
│   │   ├── savings/
│   │   │   ├── SavingsDashboard.tsx          # Savings module dashboard
│   │   │   ├── SavingsAccounts.tsx           # Manage accounts
│   │   │   ├── SavingsGoals.tsx              # Track goals
│   │   │   └── SavingsAnalytics.tsx          # Savings analytics
│   │   ├── investment/
│   │   │   ├── InvestmentDashboard.tsx       # Investment module dashboard
│   │   │   ├── InvestmentPortfolio.tsx       # Manage investments
│   │   │   ├── InvestmentAnalytics.tsx       # Performance analytics
│   │   │   └── InvestmentRebalancing.tsx     # Rebalancing tool
│   │   ├── retirement/
│   │   │   ├── RetirementDashboard.tsx       # Retirement module dashboard
│   │   │   ├── RetirementPensions.tsx        # Manage pensions
│   │   │   ├── RetirementProjections.tsx     # Retirement projections
│   │   │   └── RetirementMonteCarlo.tsx      # Monte Carlo simulation
│   │   └── iht/
│   │       ├── IHTDashboard.tsx              # IHT module dashboard
│   │       ├── IHTCalculator.tsx             # IHT calculator
│   │       ├── IHTGifts.tsx                  # Manage gifts
│   │       └── IHTTrusts.tsx                 # Manage trusts
│   ├── IHTCalculator.tsx           # **DEPRECATED**: Use /modules/iht instead
│   ├── IHTCalculatorEnhanced.tsx   # **DEPRECATED**: Legacy IHT page
│   ├── IHTCalculatorComplete.tsx   # **DEPRECATED**: Legacy IHT page
│   ├── IHTCompliance.tsx           # IHT400 compliance
│   ├── RetirementPlanningUK.tsx    # UK pension planning (advanced features)
│   ├── RetirementPlanning.tsx      # **DEPRECATED**: Use /modules/retirement
│   ├── FinancialStatements.tsx     # Balance sheet, P&L, cash flow
│   ├── FinancialProjections.tsx    # Multi-year projections
│   ├── TaxOptimization.tsx         # Tax planning strategies
│   ├── PortfolioAnalytics.tsx      # **DEPRECATED**: Use /modules/investment/analytics
│   ├── PortfolioRebalancing.tsx    # **DEPRECATED**: Use /modules/investment/rebalancing
│   ├── ProductsOverview.tsx        # **DEPRECATED**: Product summary
│   ├── Pensions.tsx                # **DEPRECATED**: Use /modules/retirement/pensions
│   ├── Investments.tsx             # **DEPRECATED**: Use /modules/investment/portfolio
│   ├── Protection.tsx              # **DEPRECATED**: Use /modules/protection/portfolio
│   ├── BankAccounts.tsx            # Bank account management
│   ├── MonteCarloSimulation.tsx    # **DEPRECATED**: Use /modules/retirement/monte-carlo
│   ├── Chat.tsx                    # AI assistant
│   └── Login.tsx                   # Authentication
├── components/
│   ├── common/       # Reusable UI primitives
│   │   ├── Button, Card, Input, ThemeToggle, LoadingSpinner (traditional)
│   │   ├── Breadcrumb.tsx            # Navigation breadcrumbs
│   │   ├── NarrativeSection.tsx      # Narrative storytelling card container
│   │   ├── CalloutBox.tsx            # Tip/warning/success callouts
│   │   ├── CompactMetricGrid.tsx     # Supporting metric grids
│   │   └── ExpandableSection.tsx     # Progressive disclosure sections
│   ├── layout/       # Header, MobileNav, navigation components
│   ├── iht/          # IHT-specific components (12 components)
│   ├── pension/      # Pension widgets (6 components)
│   ├── docs/         # Documentation browser components (5 components + tests)
│   │   ├── DocSidebar.tsx            # Category navigation
│   │   ├── DocumentViewer.tsx        # Markdown renderer
│   │   ├── SearchBar.tsx             # Documentation search
│   │   ├── VideoTutorialCard.tsx     # Tutorial display
│   │   └── QuickHelpButton.tsx       # Context-aware help
│   ├── ErrorBoundary.tsx # Error handling
│   └── ExportButtons.tsx # PDF/Excel export
├── services/         # API client functions (auth, docs, products)
└── styles/           # Theme system with light/dark mode
```

### Key Architectural Patterns
1. **Protected Routes**: `App.tsx` wraps routes with auth check, redirects to `/login` if not authenticated
2. **API Services**: All API calls go through service layer (`src/services/`)
3. **Theme System**: `ThemeProvider` wraps entire app, provides theme context to all components. Theme toggle located in Settings page.
4. **Routing**: `App.tsx` handles ALL routing logic - do NOT add navigation logic in page components
5. **State Management**: Local state + React Context (auth, theme) - no Redux/Zustand
6. **Settings Page**: Centralized hub for user preferences (theme, account management, data access). Navigation to Financial Statements is through Settings → Data & Reports.
7. **Narrative Storytelling**: UI follows narrative approach per STYLEGUIDE.md - conversational tone, educational content, progressive disclosure (see Design System section below)

## MANDATORY TESTING REQUIREMENTS

### Pre-Completion Checklist (NO SHORTCUTS)

**MUST complete ALL before claiming work is done:**

1. **TypeScript compiles**: `cd frontend && npm run build`
2. **Python imports work**: `cd backend && python -c "from app.main import app; print('✓ Imports work')"`
3. **Backend starts**: `cd backend && uvicorn app.main:app --reload --port 8000`
4. **Frontend starts**: `cd frontend && npm start`
5. **Zero browser console errors**: Open http://localhost:3000, press F12, check Console tab
6. **Features work**: Test ALL modified functionality

**DO NOT mark complete if**:
- ❌ TypeScript compilation fails
- ❌ Python imports fail
- ❌ Console shows ANY errors
- ❌ Features don't work as expected

### Running Tests

#### Backend Tests (106+ tests - 100% pass rate)

```bash
# All backend tests with coverage
cd backend && source venv/bin/activate && pytest --cov=app tests/ -v

# IHT test suite (61 tests)
pytest tests/test_iht_enhanced.py -v

# Run IHT tests by category
pytest tests/test_iht_enhanced.py::TestTaperReliefScenarios -v      # 15 taper relief tests
pytest tests/test_iht_enhanced.py::TestRNRBTaperingCalculations -v  # 9 RNRB tapering tests
pytest tests/test_iht_enhanced.py::TestEdgeCases -v                 # 8 edge cases
pytest tests/test_iht_enhanced.py::TestIntegrationScenarios -v      # 3 integration tests
pytest tests/test_iht_enhanced.py::TestComplianceAndForms -v        # 3 compliance tests

# Documentation API tests (34 tests)
pytest tests/test_docs_api.py -v

# Pension tests (12 tests)
pytest tests/test_pension.py -v

# Other module tests
pytest tests/test_auth.py -v           # Authentication tests
pytest tests/test_iht.py -v            # Basic IHT tests
pytest tests/test_export.py -v         # Export functionality tests
pytest tests/test_integration.py -v    # Integration tests
```

#### Frontend Tests (11+ tests)

```bash
cd frontend

# All frontend tests with coverage
npm test -- --coverage --watchAll=false

# Documentation component tests
npm test -- src/components/docs/__tests__ --watchAll=false

# Run specific test file
npm test -- ComponentName.test.tsx --watchAll=false
```

#### Test Coverage Summary

**Backend (106+ tests)**:
- ✅ **IHT Suite (61 tests)**: Complete UK IHT law (2024/25), taper relief, RNRB tapering, charitable rate, BPR/APR, edge cases (GWR/POAT, Quick Succession Relief, foreign assets)
- ✅ **Documentation API (34 tests)**: File listing, content serving, search, categories, error handling
- ✅ **Pension (12 tests)**: Annual Allowance, MPAA, taper calculations, carry-forward
- ✅ **Auth, Export, Integration**: Authentication, PDF/Excel export, integration scenarios

**Frontend (11+ tests)**:
- ✅ **Documentation Components**: DocSidebar, DocumentViewer, SearchBar, VideoTutorialCard, QuickHelpButton
- ✅ **UI Components**: Narrative components, common components
- ✅ **Integration**: API service tests

**Quality Metrics**:
- 100% test pass rate across all suites
- Comprehensive coverage of business logic
- Edge case testing for complex calculations
- Integration testing for multi-component workflows

## CRITICAL FIXES APPLIED (DO NOT BREAK THESE)

### SQLAlchemy Reserved Words
- `relationship` → `recipient_relationship` (models/iht.py)
- `metadata` → `extra_metadata` (models/product.py)
- Always check for reserved words when creating new models

### React 19 + TypeScript Compatibility
- **Styled-components**: Use transient props prefixed with `$` to prevent DOM warnings
  ```typescript
  // ✅ Correct
  <Button $variant="primary" $fullWidth>Click</Button>

  // ❌ Wrong - causes console warning
  <Button variant="primary" fullWidth>Click</Button>
  ```
- **React-icons**: Import with type assertions for React 19 compatibility
  ```typescript
  import * as Icons from 'react-icons/fi';
  const FiDownload = Icons.FiDownload as React.FC;
  ```
- **Theme typing**: See `frontend/src/types/styled.d.ts` for proper theme TypeScript definitions

### Routing (Critical - Prevents Infinite Redirect Loop)
- **App.tsx handles ALL routing** - compute router with useMemo BEFORE any conditional returns
- **Page components**: Do NOT add navigation logic in pages (e.g., Dashboard.tsx)
- **Login navigation**: Use `window.location.reload()`, NOT `window.location.href = '/dashboard'`
- **React Hooks order**: ALL hooks (useMemo, useState, etc.) MUST come before conditional returns

## DEVELOPMENT COMMANDS

### Quick Start
```bash
# Start both backend and frontend
./start.sh

# Or manually
# Terminal 1 - Backend (http://localhost:8000)
cd backend && source venv/bin/activate && uvicorn app.main:app --reload --port 8000

# Terminal 2 - Frontend (http://localhost:3000)
cd frontend && npm start
```

### Database Management
```bash
# Reset database with seed data (includes demo user)
cd backend && python seed_data.py
```

### Common Development Tasks
```bash
# Kill stuck processes
lsof -i :3000 | grep LISTEN | awk '{print $2}' | xargs kill -9  # Frontend
lsof -i :8000 | grep LISTEN | awk '{print $2}' | xargs kill -9  # Backend

# Check TypeScript types
cd frontend && npm run build

# Check Python imports
cd backend && python -c "from app.main import app"

# Run specific test file
cd backend && pytest tests/test_auth.py -v

# Docker deployment
docker-compose up --build
```

## API ENDPOINTS

### Authentication (`/api/auth`)
- `POST /token` - Login (returns JWT)
- `POST /register` - Register new user
- `GET /me` - Get current user (requires auth)

### **Goal-Based Modules (NEW)** (`/api/modules/`)

All modules follow consistent endpoint patterns:

#### Protection Module (`/api/modules/protection`)
- `GET /dashboard` - Comprehensive protection dashboard
- `GET /summary` - Quick summary for main dashboard
- `GET /products` - List all protection products
- `POST /products` - Create protection product
- `GET /products/{id}` - Get specific product
- `PUT /products/{id}` - Update product
- `DELETE /products/{id}` - Archive product
- `GET /analytics` - Coverage analytics and recommendations
- `POST /needs-analysis` - Calculate protection needs

#### Savings Module (`/api/modules/savings`)
- `GET /dashboard` - Savings dashboard with emergency fund status
- `GET /summary` - Quick summary for main dashboard
- `GET /accounts` - List all savings accounts
- `POST /accounts` - Create savings account
- `GET /accounts/{id}` - Get specific account
- `PUT /accounts/{id}` - Update account
- `DELETE /accounts/{id}` - Archive account
- `GET /analytics` - Savings analytics and trends
- `GET /goals` - List savings goals
- `POST /goals` - Create savings goal

#### Investment Module (`/api/modules/investment`)
- `GET /dashboard` - Investment dashboard with portfolio overview
- `GET /summary` - Quick summary for main dashboard
- `GET /portfolio` - List all investments
- `POST /portfolio` - Add investment
- `GET /portfolio/{id}` - Get specific investment
- `PUT /portfolio/{id}` - Update investment
- `DELETE /portfolio/{id}` - Archive investment
- `GET /analytics` - Performance analytics and risk metrics
- `GET /rebalancing` - Portfolio rebalancing recommendations

#### Retirement Module (`/api/modules/retirement`)
- `GET /dashboard` - Retirement dashboard with pension overview
- `GET /summary` - Quick summary for main dashboard
- `GET /pensions` - List all pensions
- `POST /pensions` - Add pension
- `GET /pensions/{id}` - Get specific pension
- `PUT /pensions/{id}` - Update pension
- `DELETE /pensions/{id}` - Archive pension
- `GET /projections?retirement_age=65` - Retirement projections
- `GET /monte-carlo?simulations=1000` - Monte Carlo simulation

#### IHT Planning Module (`/api/modules/iht`)
- `GET /dashboard` - IHT planning dashboard
- `GET /summary` - Quick summary for main dashboard
- `POST /calculator` - Calculate IHT liability
- `GET /gifts` - List all gifts
- `POST /gifts` - Record gift
- `GET /gifts/{id}` - Get specific gift
- `PUT /gifts/{id}` - Update gift
- `DELETE /gifts/{id}` - Delete gift
- `GET /trusts` - List all trusts
- `POST /trusts` - Create trust

### IHT Calculator (DEPRECATED - Use `/api/modules/iht` instead)
- `POST /calculate` - Calculate IHT with assets, gifts, trusts
- `GET /taper-relief/{gift_date}?amount={amount}` - Taper relief calculation
- `POST /save-profile` - Save IHT profile
- `GET /profile` - Get saved IHT profile
- Enhanced endpoints for advanced IHT features

### Financial Statements (`/api/financial`)
- `GET /balance-sheet/latest` - Most recent balance sheet
- `POST /balance-sheet` - Create balance sheet
- `PUT /balance-sheet/{id}` - Update balance sheet
- `GET /profit-loss/latest` - Most recent P&L
- `POST /profit-loss` - Create P&L
- `GET /cash-flow/latest` - Most recent cash flow
- `GET /summary` - Complete financial summary with metrics

### Products (`/api/products`)
- `GET /pensions/all` - All pension products
- `POST /pensions` - Create pension
- `PUT /pensions/{id}` - Update pension
- `GET /investments/all` - All investments
- `GET /protection/all` - All protection products
- `GET /portfolio/summary` - Portfolio analytics
- `GET /retirement/projection?retirement_age=65` - Retirement projection

### UK Pension (`/api/pension-uk`, `/api/pension-schemes`, `/api/pension-optimization`)
- Comprehensive UK pension API endpoints
- Annual Allowance calculations with taper
- MPAA tracking and monitoring
- 3-year carry-forward calculations
- Pension scheme management
- Tax relief optimization

### Tax & Portfolio Management
- `/api/tax-optimization` - Tax planning strategies and recommendations
- `/api/rebalancing` - Portfolio rebalancing with drift analysis
- `/api/projections` - Multi-year financial projections
- `/api/simulations` - Monte Carlo simulations

### Banking & Export
- `/api/banking` - Bank account and transaction management
- `/api/export` - PDF reports and Excel/CSV export

### AI Chat (`/api/chat`)
- AI-powered financial advice and assistance

### Documentation (`/api/docs`) - ✅ LIVE
- `GET /api/docs/list` - List all available documentation files
- `GET /api/docs/{doc_name}` - Get specific documentation content
- `GET /api/docs/search?q={query}&limit={limit}` - Search across all documentation
- `GET /api/docs/categories` - Get documentation organized by categories
- **Frontend Route**: `/learning-centre` - Full-featured documentation browser with search

**Full API Docs**: http://localhost:8000/docs (Swagger UI)

## TEST CREDENTIALS

- **Demo User** (with seed data): `demouser` / `demo123` or `demo@example.com` / `demo123`
- **Test User** (basic): `testuser` / `testpass123` or `test@example.com` / `testpass123`

## COMMON DEVELOPMENT GOTCHAS

1. **Adding new SQLAlchemy models**: Check for reserved words (`metadata`, `relationship`, `type`, `session`)
2. **API endpoint changes**: Must update BOTH backend route AND frontend service layer
3. **Theme changes**: Update both `styles/theme.ts` AND `types/styled.d.ts`. Theme toggle is in Settings page.
4. **Background processes**: Backend (:8000) and frontend (:3000) must BOTH run
5. **Database resets**: Re-run `python seed_data.py` to reset with fresh data
6. **Login issues**: Clear localStorage in browser DevTools if login doesn't redirect properly
7. **Import errors**: Backend uses absolute imports from `app.*` (e.g., `from app.api.auth.auth import get_current_user`)
8. **Infinite redirects**: Likely caused by navigation logic in page components - remove it, let App.tsx handle routing
9. **Navigation changes**: Top navigation managed in `Header.tsx` (desktop) and `MobileNav.tsx` (mobile). Settings page accessed via main navigation.
10. **Narrative components**: When building new UI, use narrative components (NarrativeSection, CalloutBox, etc.) per STYLEGUIDE.md. Do NOT use emojis or icons.
11. **Content tone**: Always use conversational second-person ("you", "your"), explain the "why", and keep paragraphs short (2-3 sentences)

## PROJECT FEATURES

### Completed ✅
- **UK Inheritance Tax Calculator** (Phase 2) - ✅ **LIVE at `/iht-calculator-complete`**
  - 7-year gift timeline with taper relief visualization
  - Estate planning scenarios with comparison
  - Trust management (10-year periodic and exit charges)
  - IHT400 compliance dashboard at `/iht-compliance`
  - 61 comprehensive tests (100% pass rate)

- **UK Pension Planning System** - ✅ **LIVE at `/retirement-planning-uk`**
  - Annual Allowance with taper calculations (£200k-£360k income)
  - MPAA tracking and monitoring
  - 3-year carry-forward calculations
  - Multi-scheme pension management
  - Tax relief optimization

- **Financial Management Suite**
  - Balance Sheet, P&L, Cash Flow at `/financial-statements`
  - Multi-year financial projections at `/financial-projections`
  - Portfolio analytics at `/portfolio-analytics`
  - Portfolio rebalancing tools at `/portfolio-rebalancing`
  - Tax optimization strategies at `/tax-optimization`
  - Monte Carlo simulations at `/monte-carlo`

- **Product Portfolio Management**
  - Pensions, Investments, Protection products
  - Product overview at `/products`
  - Individual product pages at `/products/{type}`
  - Bank account management at `/bank-accounts`

- **User Experience & Documentation**
  - **Narrative Storytelling Dashboard** at `/dashboard`
    - Conversational, educational approach
    - 4 narrative components (NarrativeSection, CalloutBox, CompactMetricGrid, ExpandableSection)
    - Progressive disclosure patterns
    - No emojis/icons, clean professional design
  - **Learning Centre** at `/learning-centre`
    - 9 comprehensive documentation files
    - Full-text search (<100ms response time)
    - 6 video tutorial series (27 videos, ~160 minutes)
    - Context-aware help with keyboard shortcuts
    - 34 backend API tests + 11 frontend tests (100% pass rate)
  - **Settings Hub** at `/settings`
    - Centralized preferences and account management
    - Theme toggle (light/dark mode)
    - Data access and reports

- **AI & Export Features**
  - AI Chat Assistant at `/chat` (OpenAI integration)
  - PDF/Excel/CSV export capabilities

- **Infrastructure**
  - Mobile responsive design with dark mode
  - Comprehensive test suite (106+ tests, 100% pass rate)
  - CI/CD pipeline with GitHub Actions
  - Docker containerization
  - Protected routes with JWT authentication

### In Progress 🚧
- Documentation polish and updates
- UI/UX refinements for mobile responsiveness
- Performance optimization

### Key UK IHT Features
- Nil-rate bands (£325,000 standard, £175,000 residence)
- 7-year taper relief calculations
- Business/Agricultural property relief
- Gift tracking and management
- Trust management (10-year periodic and exit charges)
- Charitable giving exemptions
- IHT400 compliance dashboard

### Next Implementation Phases
1. Real-time market data integration
2. AI chat refinements (intent classification, advice generation)
3. Multi-currency support
4. Open Banking integration
5. Multi-language support (i18n)
6. Mobile app (React Native)

## SETTINGS PAGE

The Settings page (`/settings`) is a centralized hub for user preferences and account management:

### Structure
```
Settings (/settings)
├── Appearance
│   └── Theme Toggle (light/dark mode)
├── Data & Reports
│   └── Financial Statements (navigates to /financial-statements)
└── Account (Danger Zone)
    └── Sign Out
```

### Key Features
- **Appearance Section**: Theme toggle with live preview
- **Data & Reports Section**: Quick access to financial statements and reports
- **Account Section**: Sign out functionality (styled with danger/error theme)
- **Responsive Design**: Card-based layout adapts to mobile and desktop
- **Navigation**: Accessible from main navigation (both desktop and mobile)

### Design Notes
- Uses consistent `SettingsSection` component for each section
- Each setting has a title, subtitle (description), and control
- Danger zone uses error color border and tinted background
- All navigation uses React Router's `useNavigate` hook

### Location of User Controls
- ❌ Theme toggle is NO LONGER in top navigation
- ❌ Sign out is NO LONGER in top navigation
- ✅ Both are now centralized in Settings page
- ✅ Access Financial Statements through Settings → Data & Reports

## DESIGN SYSTEM

### Overview
The application follows a **Narrative Storytelling** approach as defined in `STYLEGUIDE.md`. This creates an accessible, educational, and empowering user experience.

### Core Design Principles
1. **Storytelling Over Data Display**: Lead with plain-language narratives that explain financial situations
2. **Educational by Default**: Teach users about financial concepts through use
3. **Empowerment Through Understanding**: Help users understand the "why" behind recommendations
4. **Conversational & Human Tone**: Write like a trusted advisor speaking to a friend
5. **Generous White Space & Readability**: Text-focused design with line-height 1.7
6. **Progressive Disclosure**: Start simple, reveal complexity on demand

### Visual Aesthetic
- Clean, professional appearance (no emojis or decorative icons)
- Trust-inspiring white space
- Progressive disclosure patterns
- Card-based layouts with narrative sections
- Subtle animations and transitions (250ms)
- Mobile-first responsive design

### Narrative Components (MUST USE)
When building new pages or features, use these components:

1. **NarrativeSection** - Main container for story sections
   ```tsx
   <NarrativeSection highlight> // Optional border for emphasis
     <NarrativeHeading>Your Financial Position</NarrativeHeading>
     <NarrativeParagraph>You're worth £325,000...</NarrativeParagraph>
   </NarrativeSection>
   ```

2. **CalloutBox** - Tips, warnings, success messages
   ```tsx
   <CalloutBox type="tip"> // Options: tip, warning, success, info
     <strong>Good news: You can reduce this by:</strong>
     <ul><li>Making gifts now (7-year rule)</li></ul>
   </CalloutBox>
   ```

3. **CompactMetricGrid** - Supporting metrics within narratives
   ```tsx
   <CompactMetricGrid columns={4}>
     <CompactMetric value="£325k" label="Net Worth" />
   </CompactMetricGrid>
   ```

4. **ExpandableSection** - Progressive disclosure
   ```tsx
   <ExpandableSection trigger="Tell me more">
     <p>Additional details...</p>
   </ExpandableSection>
   ```

### Content Writing Guidelines

**DO:**
- ✅ "You're worth £325,000 after debts"
- ✅ "That's increased by £7,500 since last month - great progress!"
- ✅ "Good news: You can reduce this by..."
- ✅ Use second-person language ("you", "your")
- ✅ Explain the "why" behind every number
- ✅ Keep paragraphs to 2-3 sentences
- ✅ Frame challenges as opportunities

**DON'T:**
- ❌ "Net Worth: £325,000"
- ❌ "Estate value has increased 2.3%"
- ❌ Use emojis or decorative icons
- ❌ Use financial jargon without explanation
- ❌ Display metrics without context

### Reference Files
- **Complete Style Guide**: `STYLEGUIDE.md`
- **Dashboard Example**: `frontend/src/pages/Dashboard.tsx`
- **Visual Mockups**: `frontend/public/dashboard-mockups.html`

## TROUBLESHOOTING

**Port already in use**:
```bash
lsof -i :3000 | grep LISTEN  # Find PID
kill -9 [PID]                 # Kill process
```

**Backend won't start**:
- Check virtual environment is activated: `source backend/venv/bin/activate`
- Verify dependencies installed: `pip install -r backend/requirements.txt`
- Check database exists: `ls backend/financial_planning.db`

**Frontend TypeScript errors**:
- Ensure theme types are correct in `src/types/styled.d.ts`
- Check transient props use `$` prefix in styled-components
- Verify react-icons imported with type assertions

**Login doesn't redirect**:
- Clear localStorage in browser (F12 → Application → Local Storage → Clear)
- Check both backend and frontend are running
- Verify console has no errors (F12 → Console)

**Database connection issues**:
- Check `.env` file exists in backend/
- Ensure SQLite database created: `python seed_data.py`
- For PostgreSQL: verify connection string in `.env`

**Learning Centre returns 404** (RESOLVED - 2025-09-30):
- This issue has been resolved. The Learning Centre is now accessible at `/learning-centre`
- **If you encounter 404 errors**, check:
  1. Verify `LearningCentre.tsx` exists (not `.disabled`)
  2. Confirm route is uncommented in `App.tsx`
  3. Check for naming conflicts in styled components vs. imported types
  4. Restart frontend server: `cd frontend && npm start`
- **Root cause was**: File was disabled during development due to compilation errors
- **Resolution**: File enabled, route uncommented, naming conflict resolved (`DocCategory` → `CategoryBadge`)

## LEARNING CENTRE

### Overview
The Learning Centre is an in-app documentation browser that provides users with instant access to all guides, tutorials, and help resources.

### Architecture
```
Backend: /api/docs endpoints
├── GET /list - List all documentation files
├── GET /{doc_name} - Serve markdown content
├── GET /search?q={query} - Full-text search
└── GET /categories - Organized documentation tree

Frontend: React components
├── pages/LearningCentre.tsx - Main page
├── components/docs/
│   ├── DocumentViewer.tsx - Markdown renderer
│   ├── DocSidebar.tsx - Category navigation
│   ├── SearchBar.tsx - Documentation search
│   ├── VideoTutorialCard.tsx - Tutorial display
│   └── QuickHelpButton.tsx - Context-aware help
└── services/docs.ts - API client
```

### Key Files
**Backend**:
- `backend/app/api/docs.py` - Documentation API router
- `backend/app/utils/doc_search.py` - Search implementation
- `backend/app/models/docs_metadata.py` - Documentation metadata

**Frontend**:
- `frontend/src/pages/LearningCentre.tsx` - Main page
- `frontend/src/components/docs/*` - Doc components
- `frontend/src/services/docs.ts` - API service
- `frontend/src/utils/markdown.ts` - Markdown utilities

**Documentation Source**:
- `docs/` - All markdown documentation files (9 files)

### Adding New Documentation
1. Add markdown file to `/docs` folder
2. Update `docs_metadata.py` with metadata (title, category, tags, related)
3. Documentation automatically available in Learning Centre
4. Search index updates automatically on server restart

### Context-Aware Help Mapping
```typescript
// Map routes to relevant documentation
{
  '/dashboard': ['USER_GUIDE.md#dashboard-overview'],
  '/iht-calculator': ['IHT_USER_GUIDE.md', 'IHT_CALCULATION_METHODOLOGY.md'],
  '/pensions': ['USER_GUIDE.md#pension-planning'],
  '/financial-statements': ['USER_GUIDE.md#financial-statements'],
  '/tax-optimization': ['USER_GUIDE.md#tax-optimization'],
  '/settings': ['USER_GUIDE.md#settings']
}
```

Press **?** (question mark) on any page to trigger context-aware help.

### Documentation Categories
```
📘 Getting Started - New user guides and setup
💰 IHT Planning - Inheritance tax guides and compliance
🏦 Pension Planning - UK pension features and calculations
📊 Financial Management - Balance sheets, P&L, cash flow
🎯 Tax Optimization - Tax planning and optimization guides
👨‍💻 Developer Resources - API, architecture, development guides
📋 Compliance - HMRC forms, checklists, compliance tools
🎥 Video Tutorials - 27 video scripts across 6 series (~160 minutes)
❓ Help & Support - FAQ, troubleshooting, contact support
```

### Search Implementation
- Full-text search across all markdown files
- Search ranking by relevance (headings weighted higher)
- Excerpt generation with highlighted search terms
- Debounced search (300ms delay)
- Backend caching for performance (<100ms response)

### Dependencies
**Frontend** (add to package.json):
```json
{
  "react-markdown": "^9.0.1",
  "remark-gfm": "^4.0.0",
  "react-syntax-highlighter": "^15.5.0",
  "@types/react-syntax-highlighter": "^15.5.11"
}
```

**Backend**: No additional dependencies needed (uses Python standard library)

### Maintenance
- Review documentation after each major feature release
- Update VIDEO_TUTORIALS.md when creating new tutorials
- Refresh FAQ quarterly based on user questions
- Update screenshots annually or when UI changes significantly
- Maintain tax year references (currently 2024/25)
- Verify all links and cross-references quarterly

### Development Guidelines
- **Follow existing patterns**: Match app theme and component style
- **Accessibility**: WCAG 2.1 Level AA compliance required
- **Mobile-first**: Responsive design for all screen sizes
- **Dark mode**: Full theme support required
- **Performance**: Page load <2s, search <100ms
- **Testing**: 100% backend tests, 80%+ frontend tests

### Implementation Status
See `docs_tasks.md` for detailed implementation plan and task tracking.

## CI/CD PIPELINE

GitHub Actions workflow (`.github/workflows/ci.yml`) runs on push/PR:
- Backend tests (unit + integration)
- Frontend tests (TypeScript compilation + unit tests)
- Linting (Python: black/flake8, TypeScript: ESLint)
- Security scans (safety for Python, npm audit)
- Docker image builds (on main branch)

## REMEMBER

- **Working code > Fast code** - TEST EVERYTHING before marking complete
- **One feature at a time** - Don't change unrelated code
- **Follow patterns** - Architecture is established, follow it
- **Test credentials exist** - Use demo user for testing with seed data
- **Documentation is up-to-date** - Update this file when patterns change