# Goal-Based Financial Planning Application - Architectural Plan

## Executive Summary

This document outlines the transformation of the Financial Planning application from a feature-based architecture to a goal-based modular architecture. The refactor organizes the application around 5 core financial planning modules, each representing a distinct financial goal with its own dashboard, products, analytics, and planning tools.

## Vision

**Current State:** Feature-scattered application with navigation organized by functionality (Products, Analytics, Banking, etc.)

**Target State:** Goal-centric application where users think in terms of financial objectives (Protection, Savings, Investment, Retirement, IHT Planning)

## Core Modules

### 1. Protection Module
**Goal:** Secure your family's financial future against life's uncertainties

**Responsibilities:**
- Life insurance management
- Critical illness cover
- Income protection
- Protection needs analysis
- Coverage gap analysis
- Beneficiary management
- Claims tracking

**Products:**
- Life insurance policies
- Critical illness cover
- Income protection plans
- Family income benefit
- Keyman insurance (business)

**Analytics:**
- Coverage adequacy vs. needs
- Premium efficiency
- Protection timeline
- Claims history
- Beneficiary allocation

### 2. Savings Module
**Goal:** Build emergency funds and short-term savings

**Responsibilities:**
- Bank account management (from existing BankAccounts)
- Cash savings tracking
- ISA management (Cash ISAs)
- Emergency fund monitoring
- Savings goals
- Transaction history
- Interest tracking

**Products:**
- Current accounts
- Savings accounts
- Cash ISAs
- Notice accounts
- Fixed-rate bonds

**Analytics:**
- Savings rate trends
- Interest earned analysis
- Emergency fund adequacy (3-6 months expenses)
- Account balance trends
- Savings goal progress

### 3. Investment Module
**Goal:** Grow wealth for medium to long-term objectives

**Responsibilities:**
- Investment portfolio management
- Asset allocation
- Portfolio analytics (from existing PortfolioAnalytics)
- Rebalancing tools (from existing PortfolioRebalancing)
- Performance tracking
- Risk analysis
- Investment goals

**Products:**
- Stocks & Shares ISAs
- General Investment Accounts (GIA)
- Bonds
- Funds (OEIC, Unit Trusts)
- ETFs
- Individual stocks

**Analytics:**
- Portfolio performance (YTD, 1yr, 3yr, 5yr)
- Asset allocation breakdown
- Risk metrics (volatility, Sharpe ratio)
- Dividend income
- Rebalancing recommendations
- Tax efficiency (CGT, dividend allowances)

### 4. Retirement Module
**Goal:** Plan for a comfortable retirement

**Responsibilities:**
- Pension portfolio management
- Retirement planning (from RetirementPlanningUK)
- Annual Allowance tracking
- MPAA monitoring
- Retirement projections (from FinancialProjections)
- Retirement income modeling
- Monte Carlo simulations (from MonteCarloSimulation)
- State pension estimation

**Products:**
- Personal pensions
- Workplace pensions
- SIPPs
- Final salary pensions (DB)
- Annuities
- Drawdown plans

**Analytics:**
- Pension pot projection
- Retirement income forecast
- Annual Allowance usage (with taper)
- Lifetime Allowance tracking (LSDBA)
- Retirement shortfall/surplus
- Contribution efficiency
- Tax relief analysis

### 5. Inheritance Tax Planning Module
**Goal:** Preserve wealth for future generations

**Responsibilities:**
- Estate valuation
- IHT liability calculation (from IHTCalculator suite)
- Gift tracking (7-year rule)
- Trust management
- IHT compliance (from IHTCompliance)
- Estate planning scenarios
- Will alignment

**Products:**
- Estate assets (property, investments, etc.)
- Trusts (discretionary, bare, interest in possession)
- Life insurance (for IHT mitigation)
- Gifts (PETs, CLTs)

**Analytics:**
- IHT liability forecast
- Nil-rate band utilization
- Residence nil-rate band
- Taper relief tracking
- Gift timeline (7-year visualization)
- Estate planning scenario comparison
- IHT efficiency recommendations

## Architecture Changes

### Frontend Structure

#### New Page Hierarchy
```
/
├── /dashboard                          # Main dashboard (module overview)
├── /protection
│   ├── index (dashboard)               # Protection module dashboard
│   ├── /products                       # Protection products list/management
│   ├── /analytics                      # Protection analytics
│   └── /needs-analysis                 # Protection needs calculator
├── /savings
│   ├── index (dashboard)               # Savings module dashboard
│   ├── /accounts                       # Bank/savings accounts (from BankAccounts)
│   ├── /goals                          # Savings goals tracking
│   └── /analytics                      # Savings analytics
├── /investment
│   ├── index (dashboard)               # Investment module dashboard
│   ├── /portfolio                      # Portfolio management
│   ├── /analytics                      # Portfolio analytics (from PortfolioAnalytics)
│   ├── /rebalancing                    # Rebalancing tools (from PortfolioRebalancing)
│   └── /goals                          # Investment goals
├── /retirement
│   ├── index (dashboard)               # Retirement module dashboard
│   ├── /pensions                       # Pension products (from Pensions)
│   ├── /planning                       # Retirement planning (from RetirementPlanningUK)
│   ├── /projections                    # Projections (from FinancialProjections)
│   └── /monte-carlo                    # Monte Carlo simulations
├── /iht-planning
│   ├── index (dashboard)               # IHT module dashboard
│   ├── /calculator                     # IHT calculator (from IHTCalculatorComplete)
│   ├── /compliance                     # Compliance (from IHTCompliance)
│   ├── /scenarios                      # Planning scenarios
│   ├── /gifts                          # Gift tracking
│   └── /trusts                         # Trust management
├── /chat                               # AI Assistant (unchanged)
├── /learning-centre                    # Learning Centre (unchanged)
└── /settings                           # Settings (unchanged)
```

#### Component Structure
```
frontend/src/
├── pages/
│   ├── Dashboard.tsx                   # Main dashboard (refactored)
│   ├── modules/
│   │   ├── protection/
│   │   │   ├── ProtectionDashboard.tsx
│   │   │   ├── ProtectionProducts.tsx
│   │   │   ├── ProtectionAnalytics.tsx
│   │   │   └── NeedsAnalysis.tsx
│   │   ├── savings/
│   │   │   ├── SavingsDashboard.tsx
│   │   │   ├── SavingsAccounts.tsx
│   │   │   ├── SavingsGoals.tsx
│   │   │   └── SavingsAnalytics.tsx
│   │   ├── investment/
│   │   │   ├── InvestmentDashboard.tsx
│   │   │   ├── InvestmentPortfolio.tsx
│   │   │   ├── InvestmentAnalytics.tsx
│   │   │   ├── InvestmentRebalancing.tsx
│   │   │   └── InvestmentGoals.tsx
│   │   ├── retirement/
│   │   │   ├── RetirementDashboard.tsx
│   │   │   ├── RetirementPensions.tsx
│   │   │   ├── RetirementPlanning.tsx
│   │   │   ├── RetirementProjections.tsx
│   │   │   └── RetirementMonteCarlo.tsx
│   │   └── iht/
│   │       ├── IHTPlanningDashboard.tsx
│   │       ├── IHTCalculator.tsx
│   │       ├── IHTCompliance.tsx
│   │       ├── IHTScenarios.tsx
│   │       ├── IHTGifts.tsx
│   │       └── IHTTrusts.tsx
│   ├── Chat.tsx
│   ├── LearningCentre.tsx
│   ├── Settings.tsx
│   └── Login.tsx
├── components/
│   ├── modules/
│   │   ├── common/
│   │   │   ├── ModuleDashboardCard.tsx
│   │   │   ├── ModuleHeader.tsx
│   │   │   ├── ModuleMetricCard.tsx
│   │   │   ├── ModuleProductCard.tsx
│   │   │   ├── ModuleAnalyticsChart.tsx
│   │   │   └── ModuleGoalTracker.tsx
│   │   ├── protection/
│   │   │   ├── ProtectionNeedsWidget.tsx
│   │   │   ├── CoverageGapChart.tsx
│   │   │   └── ProtectionProductForm.tsx
│   │   ├── savings/
│   │   │   ├── EmergencyFundWidget.tsx
│   │   │   ├── SavingsGoalWidget.tsx
│   │   │   ├── AccountBalanceChart.tsx
│   │   │   └── TransactionList.tsx
│   │   ├── investment/
│   │   │   ├── AssetAllocationChart.tsx
│   │   │   ├── PerformanceChart.tsx
│   │   │   ├── RebalancingTable.tsx
│   │   │   └── InvestmentProductForm.tsx
│   │   ├── retirement/
│   │   │   ├── PensionProjectionChart.tsx
│   │   │   ├── AnnualAllowanceWidget.tsx
│   │   │   ├── RetirementIncomeChart.tsx
│   │   │   └── MonteCarloChart.tsx
│   │   └── iht/
│   │       ├── IHTLiabilityCard.tsx
│   │       ├── GiftTimelineChart.tsx
│   │       ├── TrustManagerWidget.tsx
│   │       └── IHTScenarioComparison.tsx
│   ├── common/
│   ├── layout/
│   └── ...
├── services/
│   ├── modules/
│   │   ├── protection.ts
│   │   ├── savings.ts
│   │   ├── investment.ts
│   │   ├── retirement.ts
│   │   └── iht.ts
│   ├── auth.ts
│   ├── docs.ts
│   └── ...
└── ...
```

### Backend Structure

#### New API Router Organization
```
backend/app/
├── api/
│   ├── modules/
│   │   ├── __init__.py
│   │   ├── protection/
│   │   │   ├── __init__.py
│   │   │   ├── protection.py           # Main protection router
│   │   │   ├── products.py             # Protection products CRUD
│   │   │   ├── analytics.py            # Protection analytics
│   │   │   └── needs_analysis.py       # Needs analysis calculator
│   │   ├── savings/
│   │   │   ├── __init__.py
│   │   │   ├── savings.py              # Main savings router
│   │   │   ├── accounts.py             # Bank accounts (from banking)
│   │   │   ├── goals.py                # Savings goals
│   │   │   └── analytics.py            # Savings analytics
│   │   ├── investment/
│   │   │   ├── __init__.py
│   │   │   ├── investment.py           # Main investment router
│   │   │   ├── portfolio.py            # Portfolio management
│   │   │   ├── analytics.py            # Portfolio analytics
│   │   │   ├── rebalancing.py          # Rebalancing (from existing)
│   │   │   └── goals.py                # Investment goals
│   │   ├── retirement/
│   │   │   ├── __init__.py
│   │   │   ├── retirement.py           # Main retirement router
│   │   │   ├── pensions.py             # Pension products
│   │   │   ├── planning.py             # Retirement planning (from pension_uk)
│   │   │   ├── projections.py          # Projections (from existing)
│   │   │   └── monte_carlo.py          # Monte Carlo (from simulations)
│   │   └── iht/
│   │       ├── __init__.py
│   │       ├── iht.py                  # Main IHT router
│   │       ├── calculator.py           # IHT calculator (from iht_refactored)
│   │       ├── compliance.py           # IHT compliance
│   │       ├── scenarios.py            # Planning scenarios
│   │       ├── gifts.py                # Gift tracking
│   │       └── trusts.py               # Trust management
│   ├── auth/
│   ├── chat.py
│   ├── docs.py
│   ├── export.py
│   └── ...
├── models/
│   ├── user.py
│   ├── product.py                      # Enhanced with module field
│   ├── module_goal.py                  # NEW: User goals per module
│   ├── module_metric.py                # NEW: Module dashboard metrics
│   ├── financial.py
│   ├── iht.py
│   ├── pension.py
│   ├── chat.py
│   └── docs_metadata.py
├── services/
│   ├── module_aggregator.py            # NEW: Module dashboard data aggregation
│   └── ...
└── ...
```

#### Database Schema Changes

##### New Tables

**module_goals**
```sql
CREATE TABLE module_goals (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    module VARCHAR(50) NOT NULL,          -- protection, savings, investment, retirement, iht
    goal_type VARCHAR(100) NOT NULL,      -- e.g., "emergency_fund", "retirement_income"
    target_amount NUMERIC(15, 2),
    target_date DATE,
    current_amount NUMERIC(15, 2),
    status VARCHAR(50) DEFAULT 'active',  -- active, achieved, paused
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP
);
```

**module_metrics**
```sql
CREATE TABLE module_metrics (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    module VARCHAR(50) NOT NULL,
    metric_type VARCHAR(100) NOT NULL,    -- e.g., "total_coverage", "emergency_fund_months"
    metric_value NUMERIC(15, 2),
    metric_metadata JSONB,                -- Additional context data
    calculated_at TIMESTAMP DEFAULT NOW()
);
```

##### Modified Tables

**products** (add module field)
```sql
ALTER TABLE products ADD COLUMN module VARCHAR(50);
-- Values: protection, savings, investment, retirement
-- IHT assets tracked separately in existing iht tables

UPDATE products SET module = 'protection' WHERE product_type = 'protection';
UPDATE products SET module = 'savings' WHERE product_type = 'savings';
UPDATE products SET module = 'investment' WHERE product_type = 'investment';
UPDATE products SET module = 'retirement' WHERE product_type = 'pension';
```

### Navigation Changes

#### Header Navigation (Desktop)
**Remove:**
- Products
- Analytics
- Banking (as standalone)
- Protection (as standalone)
- UK Pension (as standalone)
- Tax Optimisation (as standalone)
- Portfolio Analytics
- Estate Planning dropdown

**Add:**
- **Modules** dropdown:
  - Protection
  - Savings
  - Investment
  - Retirement
  - IHT Planning

**Keep:**
- Dashboard
- AI Assistant
- Learning Centre
- Settings

#### MobileNav
Same structure as Header but optimized for mobile display.

### Main Dashboard Refactor

#### Current Dashboard
- Narrative sections showing overall financial position
- Static data
- Multiple action buttons

#### New Dashboard
**Module Overview Cards (5 cards)**

Each card shows:
- Module icon and name
- Key headline metric (e.g., "Total Protection: £500k")
- 2-3 supporting metrics
- Status indicator (on track, attention needed, good)
- "View Details" button → navigates to module dashboard

**Example - Protection Module Card:**
```
┌─────────────────────────────────────────────┐
│ 🛡️  Protection                              │
│                                             │
│ Total Coverage: £500,000                    │
│                                             │
│ • 3 active policies                         │
│ • Coverage gap: £150k (needs attention)     │
│ • Next premium: £145/mo (15 days)           │
│                                             │
│ Status: ⚠️ Attention Needed                 │
│                                             │
│ [View Protection Dashboard →]               │
└─────────────────────────────────────────────┘
```

**Layout:**
- 2 cards per row on desktop
- 1 card per row on mobile
- Narrative introduction at top
- "Getting Started" section at bottom (for new users)

### Module Dashboard Pattern

Each module dashboard follows a consistent pattern:

#### Structure
1. **Module Header**
   - Module name and icon
   - Breadcrumb: Dashboard → Module Name
   - Primary action button (e.g., "Add Product", "Run Calculator")

2. **Key Metrics Section**
   - 3-4 large metric cards
   - Narrative explanation
   - Comparison to goals/benchmarks

3. **Products/Accounts Section**
   - List/grid of products in this module
   - Quick actions (edit, view details, archive)
   - "Add New" button

4. **Analytics Section**
   - Charts and visualizations
   - Performance trends
   - Risk analysis (where applicable)

5. **Goals/Planning Section**
   - Current goals for this module
   - Progress tracking
   - Recommendations

6. **Quick Actions**
   - Module-specific tools
   - Common tasks
   - Link to specialized calculators

## Data Flow

### Main Dashboard Data Flow
```
User → Main Dashboard
         ↓
      Fetch module metrics (parallel requests)
         ↓
      /api/modules/protection/dashboard
      /api/modules/savings/dashboard
      /api/modules/investment/dashboard
      /api/modules/retirement/dashboard
      /api/modules/iht/dashboard
         ↓
      Aggregate and display module cards
```

### Module Dashboard Data Flow
```
User → Module Dashboard
         ↓
      Fetch module data
         ↓
      /api/modules/{module}/dashboard (full data)
         ↓
      Display:
      - Key metrics
      - Products list
      - Analytics charts
      - Goals
```

### Drill-Down Data Flow
```
User → Module Dashboard → Product Details
                        → Analytics View
                        → Planning Tools
                        → Goals Management
```

## Migration Strategy

### Phase Approach
1. **Backend First:** Create new module API structure alongside existing APIs
2. **Parallel Development:** New module pages work alongside old pages
3. **Gradual Migration:** Migrate features module by module
4. **Deprecation:** Remove old pages once module is complete
5. **Cleanup:** Remove deprecated APIs and code

### Feature Migration Mapping

#### Protection Module
**Migrate from:**
- `/products/protection` → `/protection/products`
- Protection product creation/editing logic
- (New) Protection analytics
- (New) Needs analysis

#### Savings Module
**Migrate from:**
- `/bank-accounts` → `/savings/accounts`
- Banking API endpoints → Savings API
- Account creation/transaction logic
- (New) Savings goals
- (New) Savings analytics

#### Investment Module
**Migrate from:**
- `/products/investments` → `/investment/portfolio`
- `/portfolio-analytics` → `/investment/analytics`
- `/portfolio-rebalancing` → `/investment/rebalancing`
- Investment product logic
- Analytics charts and calculations
- Rebalancing algorithms

#### Retirement Module
**Migrate from:**
- `/products/pensions` → `/retirement/pensions`
- `/retirement-planning-uk` → `/retirement/planning`
- `/financial-projections` → `/retirement/projections`
- `/monte-carlo` → `/retirement/monte-carlo`
- Pension API endpoints
- Annual Allowance logic
- MPAA tracking
- Projection calculations
- Monte Carlo simulations

#### IHT Planning Module
**Migrate from:**
- `/iht-calculator-complete` → `/iht-planning/calculator`
- `/iht-compliance` → `/iht-planning/compliance`
- IHT calculation logic
- Gift tracking
- Trust management
- Compliance tools

## User Experience Improvements

### Cognitive Load Reduction
- **Before:** 10+ navigation items, unclear relationships
- **After:** 5 clear modules aligned with financial goals

### Progressive Disclosure
- **Level 1:** Main dashboard shows module overview
- **Level 2:** Module dashboard shows detailed metrics and products
- **Level 3:** Drill down into specific products, tools, or calculators

### Contextual Help
- Module-specific help content
- AI assistant can provide module-contextualized advice
- Learning Centre articles tagged by module

### Goal-Oriented Actions
- Clear call-to-actions per module
- Goal progress visible throughout
- Recommendations tied to specific modules

## Technical Considerations

### Performance
- Lazy load module dashboards
- Cache module metrics (Redis in future)
- Paginate product lists within modules
- Optimize parallel data fetching for main dashboard

### Testing Strategy
- Unit tests for new API endpoints
- Integration tests for module data aggregation
- E2E tests for module navigation flows
- Visual regression tests for new dashboards

### Backward Compatibility
- Keep old API endpoints during migration
- Add deprecation warnings
- Provide migration guide for any external consumers

### Future AI Integration Points
- Module-contextualized AI advice
- Goal recommendation engine
- Product suggestions per module
- Risk analysis and alerts
- Automated planning scenarios

## Success Metrics

### User Engagement
- Time to complete module setup
- Module dashboard usage frequency
- Feature discovery rate (users finding tools within modules)

### Code Quality
- Reduced code duplication
- Clear separation of concerns
- Improved test coverage
- Reduced cyclomatic complexity

### User Satisfaction
- Improved navigation intuitiveness
- Reduced clicks to complete common tasks
- Clearer understanding of financial position per goal

## Timeline Estimate

- **Phase 1 (Planning):** 2-3 days (current phase)
- **Phase 2 (Backend):** 5-7 days
- **Phase 3 (Frontend Dashboards):** 7-10 days
- **Phase 4 (Feature Migration):** 10-15 days
- **Phase 5 (Navigation & Routing):** 3-5 days
- **Phase 6 (Testing & Documentation):** 3-5 days

**Total:** 30-45 days of development effort

## Risks and Mitigations

### Risk 1: User Confusion During Transition
**Mitigation:**
- Provide in-app migration guide
- Show tooltips explaining new structure
- Maintain old routes with redirects

### Risk 2: Data Migration Complexity
**Mitigation:**
- Thorough testing of migration scripts
- Backup data before migration
- Rollback plan

### Risk 3: Breaking Changes to Existing Integrations
**Mitigation:**
- Maintain old API endpoints
- Version new APIs (v2)
- Provide deprecation timeline

### Risk 4: Scope Creep
**Mitigation:**
- Strict adherence to module boundaries
- Defer AI integration to future phase
- Focus on core functionality first

## Next Steps

1. Review and approve this architectural plan
2. Proceed to detailed task breakdown in goaltasks.md
3. Begin Phase 2 (Backend restructuring)
4. Iterative development with regular check-ins
5. User acceptance testing after each module migration

---

**Document Version:** 1.0
**Last Updated:** 2025-09-30
**Author:** Development Team
**Status:** Awaiting Approval