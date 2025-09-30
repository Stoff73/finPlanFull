# Goal-Based Application Refactor - Implementation Checklist

## Progress Tracking

**Overall Progress:** 0/78 tasks completed (0%)

- [ ] Phase 1: Planning & Setup (0/5)
- [ ] Phase 2: Backend Module Infrastructure (0/22)
- [ ] Phase 3: Frontend Module Dashboards (0/23)
- [ ] Phase 4: Main Dashboard & Services (0/5)
- [ ] Phase 5: Navigation & Routing (0/8)
- [ ] Phase 6: Deprecation & Cleanup (0/7)
- [ ] Phase 7: Testing & Documentation (0/8)

---

## Phase 1: Planning & Setup (5 tasks)

**Estimated Time:** 2-3 days

### Task 1: Environment Preparation ⚙️ SIMPLE

**Status:** ⬜ Not Started

**Actions:**

- [ ] Create feature branch `refactor/goal-based-modules`
- [ ] Push branch to remote
- [ ] Verify clean build of backend
- [ ] Verify clean build of frontend
- [ ] Create database backup in `backend/backups/`
- [ ] Document backup location and timestamp

**Files Created:**

- Branch: `refactor/goal-based-modules`
- Backup: `backend/backups/pre-refactor-[timestamp].db`

**Testing:** None required

**Acceptance Criteria:**

- ✅ Branch exists and is checked out
- ✅ Backend builds without errors
- ✅ Frontend builds without errors
- ✅ Database backup created and verified

---

### Task 2: Create Database Migration Scripts 🗄️ MEDIUM

**Status:** ⬜ Not Started | **Dependencies:** None

**Actions:**

- [ ] Create new Alembic migration: `alembic revision -m "add_module_support"`
- [ ] Add `module` column to `products` table (VARCHAR(50))
- [ ] Create `module_goals` table with schema:
  - id, user_id, module, goal_type, target_amount, target_date, current_amount, status, notes, created_at, updated_at
- [ ] Create `module_metrics` table with schema:
  - id, user_id, module, metric_type, metric_value, metric_metadata (JSONB), calculated_at
- [ ] Create indexes on `products.module`, `module_goals.user_id`, `module_metrics.user_id`
- [ ] Test migration upgrade: `alembic upgrade head`
- [ ] Test migration downgrade: `alembic downgrade -1`
- [ ] Commit migration file

**Files Created:**

- `backend/alembic/versions/XXX_add_module_support.py`

**Testing:**

- [ ] Migration runs successfully
- [ ] Rollback works correctly
- [ ] Tables created with correct schema
- [ ] Indexes created

**Acceptance Criteria:**

- ✅ Migration file created
- ✅ Upgrade and downgrade both work
- ✅ All tables and columns created correctly

---

### Task 3: Update Product Model 📦 SIMPLE

**Status:** ⬜ Not Started | **Dependencies:** Task 2

**Actions:**

- [ ] Open `backend/app/models/product.py`
- [ ] Add `module = Column(String(50), nullable=True)` after product_type
- [ ] Add comment: `# Module: protection, savings, investment, retirement`
- [ ] Import necessary validation if needed
- [ ] Run existing product tests: `pytest tests/test_products.py -v`
- [ ] Verify tests still pass
- [ ] Commit changes

**Files Modified:**

- `backend/app/models/product.py`

**Testing:**

- [ ] Existing product tests pass
- [ ] Model imports without errors

**Acceptance Criteria:**

- ✅ Module field added to Product model
- ✅ All existing tests pass
- ✅ No import errors

---

### Task 4: Create Module Models 🏗️ MEDIUM

**Status:** ⬜ Not Started | **Dependencies:** Task 2

**Actions:**

- [ ] Create `backend/app/models/module_goal.py`
- [ ] Define ModuleGoal class with all fields from migration
- [ ] Add relationship to User model
- [ ] Add validation for module field (enum or check constraint)
- [ ] Create `backend/app/models/module_metric.py`
- [ ] Define ModuleMetric class with all fields from migration
- [ ] Add relationship to User model
- [ ] Update `backend/app/models/__init__.py` to import new models
- [ ] Update `backend/app/models/user.py` to add relationships:
  - `module_goals = relationship("ModuleGoal", back_populates="user")`
  - `module_metrics = relationship("ModuleMetric", back_populates="user")`
- [ ] Write unit tests for new models
- [ ] Run tests: `pytest tests/test_models.py -v`
- [ ] Commit changes

**Files Created:**

- `backend/app/models/module_goal.py`
- `backend/app/models/module_metric.py`
- `backend/tests/test_module_models.py`

**Files Modified:**

- `backend/app/models/__init__.py`
- `backend/app/models/user.py`

**Testing:**

- [ ] ModuleGoal model creates successfully
- [ ] ModuleMetric model creates successfully
- [ ] Relationships work correctly
- [ ] Validation works

**Acceptance Criteria:**

- ✅ Models created and importable
- ✅ Relationships defined correctly
- ✅ Unit tests pass
- ✅ No database errors

---

### Task 5: Create Shared Module Components 🎨 MEDIUM

**Status:** ⬜ Not Started | **Dependencies:** None

**Actions:**

- [ ] Create directory: `frontend/src/components/modules/common/`
- [ ] Create `ModuleDashboardCard.tsx`:
  - Props: module name, icon, headline metric, supporting metrics, status, onClick
  - Styled-components with theme support
  - Responsive design (mobile, tablet, desktop)
- [ ] Create `ModuleHeader.tsx`:
  - Props: module name, icon, breadcrumb, primaryAction
  - Consistent header for all module pages
- [ ] Create `ModuleMetricCard.tsx`:
  - Props: label, value, change, trend, color
  - Display key metrics with trends
- [ ] Create `ModuleProductCard.tsx`:
  - Props: product data, actions (edit, delete, view)
  - Product display card for lists
- [ ] Create `ModuleGoalTracker.tsx`:
  - Props: goal data, progress percentage
  - Visual goal progress display
- [ ] Create TypeScript interfaces in each component file
- [ ] Test components compile: `npm run build`
- [ ] Commit components

**Files Created:**

- `frontend/src/components/modules/common/ModuleDashboardCard.tsx`
- `frontend/src/components/modules/common/ModuleHeader.tsx`
- `frontend/src/components/modules/common/ModuleMetricCard.tsx`
- `frontend/src/components/modules/common/ModuleProductCard.tsx`
- `frontend/src/components/modules/common/ModuleGoalTracker.tsx`

**Testing:**

- [ ] TypeScript compiles without errors
- [ ] Components render without crashing
- [ ] Responsive design works

**Acceptance Criteria:**

- ✅ All 5 components created
- ✅ TypeScript interfaces defined
- ✅ Build succeeds
- ✅ Components are reusable

---

## Phase 2: Backend Module Infrastructure (22 tasks)

**Estimated Time:** 5-7 days

### Protection Module (Tasks 6-9)

#### Task 6: Create Protection API Router 🛡️ MEDIUM

**Status:** ⬜ Not Started | **Dependencies:** Tasks 3, 4

**Actions:**

- [ ] Create directory: `backend/app/api/modules/protection/`
- [ ] Create `__init__.py` in protection directory
- [ ] Create `protection.py` with APIRouter
- [ ] Implement `GET /api/modules/protection/dashboard` endpoint:
  - Aggregate protection products for user
  - Calculate total coverage
  - Calculate total premiums
  - Get active policies count
  - Return JSON response
- [ ] Implement `GET /api/modules/protection/summary` endpoint:
  - Quick summary for main dashboard card
  - Key metrics only (total coverage, policy count, status)
- [ ] Add authentication dependency to all endpoints
- [ ] Test endpoints manually with Postman/curl
- [ ] Write integration tests
- [ ] Commit changes

**Files Created:**

- `backend/app/api/modules/protection/__init__.py`
- `backend/app/api/modules/protection/protection.py`
- `backend/tests/test_modules_protection.py`

**Testing:**

- [ ] Dashboard endpoint returns correct data
- [ ] Summary endpoint returns correct data
- [ ] Authentication required
- [ ] Error handling works

**Acceptance Criteria:**

- ✅ Router created and working
- ✅ Both endpoints functional
- ✅ Tests pass
- ✅ Documented in code

---

#### Task 7: Create Protection Products Endpoints 📋 MEDIUM

**Status:** ⬜ Not Started | **Dependencies:** Task 6

**Actions:**

- [ ] Create `products.py` in protection directory
- [ ] Implement `GET /api/modules/protection/products`:
  - Query products where module='protection' and user_id=current_user
  - Return list with pagination support
  - Sort by most recent
- [ ] Implement `POST /api/modules/protection/products`:
  - Validate input data
  - Create product with module='protection'
  - Return created product
- [ ] Implement `PUT /api/modules/protection/products/{id}`:
  - Verify ownership
  - Update product
  - Return updated product
- [ ] Implement `DELETE /api/modules/protection/products/{id}`:
  - Verify ownership
  - Soft delete (set status='archived')
  - Return success message
- [ ] Add Pydantic schemas for validation
- [ ] Write integration tests for all CRUD operations
- [ ] Test with different user accounts
- [ ] Commit changes

**Files Created:**

- `backend/app/api/modules/protection/products.py`

**Testing:**

- [ ] GET returns only protection products
- [ ] POST creates product correctly
- [ ] PUT updates correctly
- [ ] DELETE archives product
- [ ] User can only access own products
- [ ] Validation errors caught

**Acceptance Criteria:**

- ✅ All CRUD operations work
- ✅ Products filtered by module
- ✅ Proper authorization
- ✅ Tests pass

---

#### Task 8: Create Protection Analytics Endpoints 📊 COMPLEX

**Status:** ⬜ Not Started | **Dependencies:** Task 6

**Actions:**

- [ ] Create `analytics.py` in protection directory
- [ ] Implement coverage analysis calculation:
  - Total coverage amount
  - Coverage by policy type
  - Coverage adequacy vs. needs (if needs analysis exists)
- [ ] Implement premium efficiency metrics:
  - Total annual premiums
  - Premium per £100k coverage
  - Premium trend over time
- [ ] Implement `GET /api/modules/protection/analytics`:
  - Return all analytics in structured JSON
  - Include charts data (time series, breakdowns)
- [ ] Add caching for expensive calculations (in-memory for now)
- [ ] Write tests for calculation accuracy
- [ ] Performance test (should be <500ms)
- [ ] Commit changes

**Files Created:**

- `backend/app/api/modules/protection/analytics.py`

**Testing:**

- [ ] Coverage calculations accurate
- [ ] Premium calculations accurate
- [ ] Performance acceptable
- [ ] Caching works
- [ ] Tests pass

**Acceptance Criteria:**

- ✅ Analytics endpoint functional
- ✅ Calculations verified accurate
- ✅ Response time <500ms
- ✅ Tests pass

---

#### Task 9: Create Protection Needs Analysis Endpoint 🔍 COMPLEX

**Status:** ⬜ Not Started | **Dependencies:** Task 6

**Actions:**

- [ ] Create `needs_analysis.py` in protection directory
- [ ] Implement needs analysis calculator:
  - Input: income, dependents, debts, existing coverage, expenses
  - Calculate: income replacement needs (10x income rule or custom)
  - Calculate: debt coverage needs
  - Calculate: future expenses (education, etc.)
  - Calculate: total needs
  - Calculate: coverage gap (needs - existing coverage)
- [ ] Implement `POST /api/modules/protection/needs-analysis`:
  - Accept analysis parameters
  - Run calculations
  - Return detailed breakdown
- [ ] Add recommendation engine:
  - Suggest policy types
  - Suggest coverage amounts
- [ ] Write comprehensive tests with various scenarios
- [ ] Document calculation methodology
- [ ] Commit changes

**Files Created:**

- `backend/app/api/modules/protection/needs_analysis.py`

**Testing:**

- [ ] Calculations accurate for various scenarios
- [ ] Edge cases handled
- [ ] Recommendations sensible
- [ ] Tests pass

**Acceptance Criteria:**

- ✅ Calculator works correctly
- ✅ Coverage gap calculated accurately
- ✅ Recommendations provided
- ✅ Tests pass

---

### Savings Module (Tasks 10-13)

#### Task 10: Create Savings API Router 💰 MEDIUM

**Status:** ⬜ Not Started | **Dependencies:** Tasks 3, 4

**Actions:**

- [ ] Create directory: `backend/app/api/modules/savings/`
- [ ] Create `__init__.py` in savings directory
- [ ] Create `savings.py` with APIRouter
- [ ] Implement `GET /api/modules/savings/dashboard`:
  - Aggregate savings accounts
  - Calculate total balance
  - Calculate emergency fund months
  - Calculate savings rate
  - Return JSON response
- [ ] Implement `GET /api/modules/savings/summary`:
  - Quick summary for main dashboard
  - Total balance, emergency fund status, account count
- [ ] Test endpoints
- [ ] Write integration tests
- [ ] Commit changes

**Files Created:**

- `backend/app/api/modules/savings/__init__.py`
- `backend/app/api/modules/savings/savings.py`

**Testing:**

- [ ] Dashboard endpoint works
- [ ] Summary endpoint works
- [ ] Authentication required
- [ ] Tests pass

**Acceptance Criteria:**

- ✅ Router functional
- ✅ Endpoints working
- ✅ Tests pass

---

#### Task 11: Migrate Banking to Savings Module 🏦 MEDIUM

**Status:** ⬜ Not Started | **Dependencies:** Task 10

**Actions:**

- [ ] Review existing `backend/app/api/banking/banking.py`
- [ ] Create `accounts.py` in savings directory
- [ ] Copy and refactor banking endpoints:
  - `GET /api/modules/savings/accounts` (list accounts)
  - `POST /api/modules/savings/accounts` (create account)
  - `PUT /api/modules/savings/accounts/{id}` (update)
  - `DELETE /api/modules/savings/accounts/{id}` (delete)
  - `GET /api/modules/savings/accounts/{id}/transactions` (transactions)
  - `POST /api/modules/savings/accounts/{id}/transactions` (add transaction)
- [ ] Update to use module='savings' filter
- [ ] Keep old banking endpoints temporarily (add deprecation warning)
- [ ] Test all endpoints
- [ ] Write integration tests
- [ ] Commit changes

**Files Created:**

- `backend/app/api/modules/savings/accounts.py`

**Files Modified:**

- `backend/app/api/banking/banking.py` (add deprecation warnings)

**Testing:**

- [ ] All account operations work
- [ ] Transactions work
- [ ] Migration doesn't break existing data
- [ ] Tests pass

**Acceptance Criteria:**

- ✅ All banking features available in savings
- ✅ Accounts filtered correctly
- ✅ Tests pass

---

#### Task 12: Create Savings Goals Endpoints 🎯 MEDIUM

**Status:** ⬜ Not Started | **Dependencies:** Task 10

**Actions:**

- [ ] Create `goals.py` in savings directory
- [ ] Implement `GET /api/modules/savings/goals`:
  - Query module_goals where module='savings'
  - Return active goals
- [ ] Implement `POST /api/modules/savings/goals`:
  - Create savings goal (emergency fund, vacation, etc.)
  - Set target amount and date
  - Return created goal
- [ ] Implement `PUT /api/modules/savings/goals/{id}`:
  - Update goal progress
  - Update target
  - Return updated goal
- [ ] Implement `DELETE /api/modules/savings/goals/{id}`:
  - Mark goal as completed or archived
- [ ] Calculate goal progress percentage
- [ ] Test all endpoints
- [ ] Write tests
- [ ] Commit changes

**Files Created:**

- `backend/app/api/modules/savings/goals.py`

**Testing:**

- [ ] CRUD operations work
- [ ] Progress calculated correctly
- [ ] Tests pass

**Acceptance Criteria:**

- ✅ Goals management functional
- ✅ Progress tracking works
- ✅ Tests pass

---

#### Task 13: Create Savings Analytics Endpoints 📈 MEDIUM

**Status:** ⬜ Not Started | **Dependencies:** Task 10

**Actions:**

- [ ] Create `analytics.py` in savings directory
- [ ] Implement savings rate calculation:
  - Track deposits vs. time
  - Calculate monthly savings rate
  - Calculate trend
- [ ] Implement emergency fund adequacy:
  - Get monthly expenses from user
  - Calculate months of coverage
  - Recommend target (3-6 months)
- [ ] Implement `GET /api/modules/savings/analytics`:
  - Return all analytics
  - Include time series data for charts
- [ ] Add interest earned tracking
- [ ] Test calculations
- [ ] Write tests
- [ ] Commit changes

**Files Created:**

- `backend/app/api/modules/savings/analytics.py`

**Testing:**

- [ ] Savings rate accurate
- [ ] Emergency fund calculation correct
- [ ] Tests pass

**Acceptance Criteria:**

- ✅ Analytics functional
- ✅ Calculations accurate
- ✅ Tests pass

---

### Investment Module (Tasks 14-17)

#### Task 14: Create Investment API Router 📈 MEDIUM

**Status:** ⬜ Not Started | **Dependencies:** Tasks 3, 4

**Actions:**

- [ ] Create directory: `backend/app/api/modules/investment/`
- [ ] Create `__init__.py`
- [ ] Create `investment.py` with APIRouter
- [ ] Implement `GET /api/modules/investment/dashboard`
- [ ] Implement `GET /api/modules/investment/summary`
- [ ] Test endpoints
- [ ] Write tests
- [ ] Commit changes

**Files Created:**

- `backend/app/api/modules/investment/investment.py`

---

#### Task 15: Create Investment Portfolio Endpoints 💼 MEDIUM

**Status:** ⬜ Not Started | **Dependencies:** Task 14

**Actions:**

- [ ] Create `portfolio.py` in investment directory
- [ ] Implement CRUD for investments (GET, POST, PUT, DELETE)
- [ ] Filter by module='investment'
- [ ] Test endpoints
- [ ] Write tests
- [ ] Commit changes

**Files Created:**

- `backend/app/api/modules/investment/portfolio.py`

---

#### Task 16: Migrate Portfolio Analytics 📊 COMPLEX

**Status:** ⬜ Not Started | **Dependencies:** Task 14

**Actions:**

- [ ] Review `backend/app/api/products.py` portfolio analytics
- [ ] Create `analytics.py` in investment directory
- [ ] Copy and refactor analytics logic:
  - Portfolio performance (YTD, 1yr, 3yr, 5yr)
  - Asset allocation breakdown
  - Risk metrics (volatility, Sharpe ratio)
  - Dividend income tracking
- [ ] Update to work with investment module
- [ ] Test all calculations
- [ ] Write comprehensive tests
- [ ] Commit changes

**Files Created:**

- `backend/app/api/modules/investment/analytics.py`

---

#### Task 17: Migrate Rebalancing Logic 🔄 MEDIUM

**Status:** ⬜ Not Started | **Dependencies:** Task 14

**Actions:**

- [ ] Review `backend/app/api/rebalancing.py`
- [ ] Create `rebalancing.py` in investment directory
- [ ] Copy and refactor rebalancing logic
- [ ] Update to work with investment module
- [ ] Test rebalancing calculations
- [ ] Write tests
- [ ] Commit changes

**Files Created:**

- `backend/app/api/modules/investment/rebalancing.py`

---

### Retirement Module (Tasks 18-20)

#### Task 18: Create Retirement API Router 🏖️ MEDIUM

**Status:** ⬜ Not Started | **Dependencies:** Tasks 3, 4

**Actions:**

- [ ] Create directory: `backend/app/api/modules/retirement/`
- [ ] Create `__init__.py`
- [ ] Create `retirement.py` with APIRouter
- [ ] Implement dashboard and summary endpoints
- [ ] Test endpoints
- [ ] Write tests
- [ ] Commit changes

**Files Created:**

- `backend/app/api/modules/retirement/retirement.py`

---

#### Task 19: Migrate Pension Endpoints 🏦 COMPLEX

**Status:** ⬜ Not Started | **Dependencies:** Task 18

**Actions:**

- [ ] Review `backend/app/api/pension/` (3 routers)
- [ ] Create `pensions.py` in retirement directory
- [ ] Create `planning.py` in retirement directory
- [ ] Copy pension CRUD logic
- [ ] Copy AA/MPAA/taper calculations
- [ ] Copy 3-year carry-forward logic
- [ ] Update to use module='retirement'
- [ ] Test all pension features
- [ ] Write tests
- [ ] Commit changes

**Files Created:**

- `backend/app/api/modules/retirement/pensions.py`
- `backend/app/api/modules/retirement/planning.py`

---

#### Task 20: Migrate Projections & Monte Carlo 📊 COMPLEX

**Status:** ⬜ Not Started | **Dependencies:** Task 18

**Actions:**

- [ ] Review `backend/app/api/projections.py`
- [ ] Review `backend/app/api/simulations.py`
- [ ] Create `projections.py` in retirement directory
- [ ] Create `monte_carlo.py` in retirement directory
- [ ] Copy projection logic
- [ ] Copy Monte Carlo simulation logic
- [ ] Update to work with retirement module
- [ ] Test calculations
- [ ] Write tests
- [ ] Commit changes

**Files Created:**

- `backend/app/api/modules/retirement/projections.py`
- `backend/app/api/modules/retirement/monte_carlo.py`

---

### IHT Planning Module (Tasks 21-24)

#### Task 21: Create IHT Planning API Router 🏛️ MEDIUM

**Status:** ⬜ Not Started | **Dependencies:** Tasks 3, 4

**Actions:**

- [ ] Create directory: `backend/app/api/modules/iht/`
- [ ] Create `__init__.py`
- [ ] Create `iht.py` with APIRouter
- [ ] Implement dashboard and summary endpoints
- [ ] Test endpoints
- [ ] Write tests
- [ ] Commit changes

**Files Created:**

- `backend/app/api/modules/iht/iht.py`

---

#### Task 22: Migrate IHT Calculator Logic 💼 COMPLEX

**Status:** ⬜ Not Started | **Dependencies:** Task 21

**Actions:**

- [ ] Review `backend/app/api/iht_refactored.py`
- [ ] Create `calculator.py` in iht directory
- [ ] Copy all IHT calculation logic:
  - Estate valuation
  - Nil-rate bands (standard & residence)
  - Taper relief
  - RNRB tapering
  - Charitable rate
  - BPR/APR
- [ ] Maintain all existing functionality
- [ ] Test with existing IHT test suite (61 tests)
- [ ] Ensure 100% pass rate
- [ ] Commit changes

**Files Created:**

- `backend/app/api/modules/iht/calculator.py`

**Testing:**

- [ ] Run `pytest tests/test_iht_enhanced.py -v`
- [ ] All 61 tests must pass

---

#### Task 23: Create IHT Gifts & Trusts Endpoints 🎁 MEDIUM

**Status:** ⬜ Not Started | **Dependencies:** Task 21

**Actions:**

- [ ] Create `gifts.py` in iht directory
- [ ] Implement gift CRUD endpoints
- [ ] Track 7-year rule
- [ ] Calculate taper relief per gift
- [ ] Create `trusts.py` in iht directory
- [ ] Implement trust CRUD endpoints
- [ ] Track 10-year periodic charges
- [ ] Track exit charges
- [ ] Test endpoints
- [ ] Write tests
- [ ] Commit changes

**Files Created:**

- `backend/app/api/modules/iht/gifts.py`
- `backend/app/api/modules/iht/trusts.py`

---

#### Task 24: Migrate IHT Compliance 📋 MEDIUM

**Status:** ⬜ Not Started | **Dependencies:** Task 21

**Actions:**

- [ ] Review existing IHT compliance endpoints
- [ ] Create `compliance.py` in iht directory
- [ ] Copy IHT400 generation logic
- [ ] Copy compliance checklist logic
- [ ] Copy payment calculation
- [ ] Test compliance tools
- [ ] Write tests
- [ ] Commit changes

**Files Created:**

- `backend/app/api/modules/iht/compliance.py`

---

### Backend Integration (Tasks 25-27)

#### Task 25: Create Module Aggregator Service 🔗 COMPLEX

**Status:** ⬜ Not Started | **Dependencies:** Tasks 6-24

**Actions:**

- [ ] Create `backend/app/services/module_aggregator.py`
- [ ] Implement `get_all_module_summaries(user_id)`:
  - Fetch protection summary
  - Fetch savings summary
  - Fetch investment summary
  - Fetch retirement summary
  - Fetch IHT summary
  - Execute in parallel (asyncio.gather)
- [ ] Add in-memory caching (TTL 5 minutes)
- [ ] Add error handling for individual module failures
- [ ] Test aggregator performance (<1s total)
- [ ] Write tests
- [ ] Commit changes

**Files Created:**

- `backend/app/services/module_aggregator.py`

**Testing:**

- [ ] All modules fetched correctly
- [ ] Parallel execution works
- [ ] Performance <1s
- [ ] Error handling works
- [ ] Caching works

---

#### Task 26: Update Main App with Module Routers 🚀 SIMPLE

**Status:** ⬜ Not Started | **Dependencies:** Tasks 6-24

**Actions:**

- [ ] Open `backend/app/main.py`
- [ ] Import all 5 module routers
- [ ] Mount protection router: `app.include_router(protection_router, prefix="/api/modules/protection", tags=["Protection Module"])`
- [ ] Mount savings router
- [ ] Mount investment router
- [ ] Mount retirement router
- [ ] Mount IHT router
- [ ] Test server starts without errors
- [ ] Check Swagger docs at http://localhost:8000/docs
- [ ] Verify all module endpoints visible
- [ ] Commit changes

**Files Modified:**

- `backend/app/main.py`

**Testing:**

- [ ] Server starts successfully
- [ ] All endpoints accessible
- [ ] Swagger docs complete

---

#### Task 27: Create Main Dashboard API Endpoint 📊 MEDIUM

**Status:** ⬜ Not Started | **Dependencies:** Tasks 25, 26

**Actions:**

- [ ] Create `backend/app/api/dashboard.py`
- [ ] Create APIRouter for dashboard
- [ ] Implement `GET /api/dashboard/overview`:
  - Use module_aggregator service
  - Return data for all 5 modules
  - Format for frontend dashboard cards
- [ ] Add authentication
- [ ] Test endpoint returns all module data
- [ ] Test performance (<1s)
- [ ] Write tests
- [ ] Mount in main.py
- [ ] Commit changes

**Files Created:**

- `backend/app/api/dashboard.py`

**Files Modified:**

- `backend/app/main.py`

**Testing:**

- [ ] Endpoint returns complete data
- [ ] Performance acceptable
- [ ] Tests pass

---

## Phase 3: Frontend Module Dashboards (23 tasks)

**Estimated Time:** 7-10 days

### Protection Module Frontend (Tasks 28-31)

#### Task 28: Create Protection Dashboard Page 🛡️ MEDIUM

**Status:** ⬜ Not Started | **Dependencies:** Tasks 6-9

**Actions:**

- [ ] Create `frontend/src/pages/modules/protection/ProtectionDashboard.tsx`
- [ ] Import ModuleHeader, ModuleMetricCard, ModuleProductCard
- [ ] Fetch data from `/api/modules/protection/dashboard`
- [ ] Display key metrics section:
  - Total coverage
  - Active policies
  - Coverage gap
  - Monthly premiums
- [ ] Display products section (list of policies)
- [ ] Display analytics section (charts)
- [ ] Add "Run Needs Analysis" button
- [ ] Test responsive design
- [ ] Test loading states
- [ ] Test error handling
- [ ] Commit changes

**Files Created:**

- `frontend/src/pages/modules/protection/ProtectionDashboard.tsx`

---

#### Task 29: Create Protection Products Page 📋 MEDIUM

**Status:** ⬜ Not Started | **Dependencies:** Task 7

**Actions:**

- [ ] Create `frontend/src/pages/modules/protection/ProtectionProducts.tsx`
- [ ] Fetch products from `/api/modules/protection/products`
- [ ] Display product list (grid or table)
- [ ] Implement product form modal for add/edit
- [ ] Add delete confirmation modal
- [ ] Test CRUD operations
- [ ] Test validation
- [ ] Commit changes

**Files Created:**

- `frontend/src/pages/modules/protection/ProtectionProducts.tsx`

---

#### Task 30: Create Protection Analytics Page 📊 MEDIUM

**Status:** ⬜ Not Started | **Dependencies:** Task 8

**Actions:**

- [ ] Create `frontend/src/pages/modules/protection/ProtectionAnalytics.tsx`
- [ ] Fetch analytics from `/api/modules/protection/analytics`
- [ ] Create coverage breakdown chart
- [ ] Create premium trend chart
- [ ] Display coverage adequacy metrics
- [ ] Test charts render correctly
- [ ] Commit changes

**Files Created:**

- `frontend/src/pages/modules/protection/ProtectionAnalytics.tsx`

---

#### Task 31: Create Protection Components 🎨 MEDIUM

**Status:** ⬜ Not Started | **Dependencies:** None

**Actions:**

- [ ] Create directory: `frontend/src/components/modules/protection/`
- [ ] Create `CoverageGapChart.tsx`
- [ ] Create `ProtectionNeedsWidget.tsx`
- [ ] Create `ProtectionProductForm.tsx`
- [ ] Test components compile
- [ ] Commit changes

**Files Created:**

- `frontend/src/components/modules/protection/CoverageGapChart.tsx`
- `frontend/src/components/modules/protection/ProtectionNeedsWidget.tsx`
- `frontend/src/components/modules/protection/ProtectionProductForm.tsx`

---

### Savings Module Frontend (Tasks 32-35)

#### Task 32: Create Savings Dashboard Page 💰 MEDIUM

**Status:** ⬜ Not Started | **Dependencies:** Tasks 10-13

**Actions:**

- [ ] Create `frontend/src/pages/modules/savings/SavingsDashboard.tsx`
- [ ] Fetch dashboard data
- [ ] Display emergency fund widget
- [ ] Display savings goals progress
- [ ] Display accounts list
- [ ] Display analytics charts
- [ ] Test responsive design
- [ ] Commit changes

**Files Created:**

- `frontend/src/pages/modules/savings/SavingsDashboard.tsx`

---

#### Task 33: Create Savings Accounts Page 🏦 MEDIUM

**Status:** ⬜ Not Started | **Dependencies:** Task 11

**Actions:**

- [ ] Create `frontend/src/pages/modules/savings/SavingsAccounts.tsx`
- [ ] Review existing `frontend/src/pages/BankAccounts.tsx`
- [ ] Copy and refactor account list logic
- [ ] Copy transaction display logic
- [ ] Update API calls to use `/api/modules/savings/accounts`
- [ ] Test all account operations
- [ ] Test transaction management
- [ ] Commit changes

**Files Created:**

- `frontend/src/pages/modules/savings/SavingsAccounts.tsx`

---

#### Task 34: Create Savings Goals Page 🎯 MEDIUM

**Status:** ⬜ Not Started | **Dependencies:** Task 12

**Actions:**

- [ ] Create `frontend/src/pages/modules/savings/SavingsGoals.tsx`
- [ ] Fetch goals from API
- [ ] Display goals list with progress bars
- [ ] Create goal form modal
- [ ] Update goal progress functionality
- [ ] Test CRUD operations
- [ ] Commit changes

**Files Created:**

- `frontend/src/pages/modules/savings/SavingsGoals.tsx`

---

#### Task 35: Create Savings Components 🎨 MEDIUM

**Status:** ⬜ Not Started | **Dependencies:** None

**Actions:**

- [ ] Create directory: `frontend/src/components/modules/savings/`
- [ ] Create `EmergencyFundWidget.tsx`
- [ ] Create `SavingsGoalWidget.tsx`
- [ ] Create `AccountBalanceChart.tsx`
- [ ] Create `TransactionList.tsx`
- [ ] Test components
- [ ] Commit changes

**Files Created:**

- `frontend/src/components/modules/savings/EmergencyFundWidget.tsx`
- `frontend/src/components/modules/savings/SavingsGoalWidget.tsx`
- `frontend/src/components/modules/savings/AccountBalanceChart.tsx`
- `frontend/src/components/modules/savings/TransactionList.tsx`

---

### Investment Module Frontend (Tasks 36-40)

#### Task 36: Create Investment Dashboard Page 📈 MEDIUM

**Status:** ⬜ Not Started | **Dependencies:** Tasks 14-17

**Actions:**

- [ ] Create `frontend/src/pages/modules/investment/InvestmentDashboard.tsx`
- [ ] Implement dashboard layout
- [ ] Commit changes

**Files Created:**

- `frontend/src/pages/modules/investment/InvestmentDashboard.tsx`

---

#### Task 37: Create Investment Portfolio Page 💼 MEDIUM

**Status:** ⬜ Not Started | **Dependencies:** Task 15

**Actions:**

- [ ] Create `frontend/src/pages/modules/investment/InvestmentPortfolio.tsx`
- [ ] Implement portfolio management
- [ ] Commit changes

**Files Created:**

- `frontend/src/pages/modules/investment/InvestmentPortfolio.tsx`

---

#### Task 38: Create Investment Analytics Page 📊 COMPLEX

**Status:** ⬜ Not Started | **Dependencies:** Task 16

**Actions:**

- [ ] Create `frontend/src/pages/modules/investment/InvestmentAnalytics.tsx`
- [ ] Review `frontend/src/pages/PortfolioAnalytics.tsx`
- [ ] Copy and refactor analytics logic
- [ ] Update API calls
- [ ] Test all charts and metrics
- [ ] Commit changes

**Files Created:**

- `frontend/src/pages/modules/investment/InvestmentAnalytics.tsx`

---

#### Task 39: Create Investment Rebalancing Page 🔄 MEDIUM

**Status:** ⬜ Not Started | **Dependencies:** Task 17

**Actions:**

- [ ] Create `frontend/src/pages/modules/investment/InvestmentRebalancing.tsx`
- [ ] Review `frontend/src/pages/PortfolioRebalancing.tsx`
- [ ] Copy and refactor rebalancing logic
- [ ] Update API calls
- [ ] Test rebalancing functionality
- [ ] Commit changes

**Files Created:**

- `frontend/src/pages/modules/investment/InvestmentRebalancing.tsx`

---

#### Task 40: Create Investment Components 🎨 MEDIUM

**Status:** ⬜ Not Started | **Dependencies:** None

**Actions:**

- [ ] Create directory: `frontend/src/components/modules/investment/`
- [ ] Create `AssetAllocationChart.tsx`
- [ ] Create `PerformanceChart.tsx`
- [ ] Create `RebalancingTable.tsx`
- [ ] Create `InvestmentProductForm.tsx`
- [ ] Test components
- [ ] Commit changes

**Files Created:**

- `frontend/src/components/modules/investment/` (4 components)

---

### Retirement Module Frontend (Tasks 41-45)

#### Task 41: Create Retirement Dashboard Page 🏖️ MEDIUM

**Status:** ⬜ Not Started | **Dependencies:** Tasks 18-20

**Actions:**

- [ ] Create `frontend/src/pages/modules/retirement/RetirementDashboard.tsx`
- [ ] Implement dashboard
- [ ] Commit changes

**Files Created:**

- `frontend/src/pages/modules/retirement/RetirementDashboard.tsx`

---

#### Task 42: Create Retirement Pensions Page 💼 MEDIUM

**Status:** ⬜ Not Started | **Dependencies:** Task 19

**Actions:**

- [ ] Create `frontend/src/pages/modules/retirement/RetirementPensions.tsx`
- [ ] Review `frontend/src/pages/Pensions.tsx`
- [ ] Copy and refactor logic
- [ ] Commit changes

**Files Created:**

- `frontend/src/pages/modules/retirement/RetirementPensions.tsx`

---

#### Task 43: Create Retirement Planning Page 📋 COMPLEX

**Status:** ⬜ Not Started | **Dependencies:** Task 19

**Actions:**

- [ ] Create `frontend/src/pages/modules/retirement/RetirementPlanning.tsx`
- [ ] Review `frontend/src/pages/RetirementPlanningUK.tsx`
- [ ] Copy AA/MPAA/taper logic
- [ ] Update API calls
- [ ] Test all planning features
- [ ] Commit changes

**Files Created:**

- `frontend/src/pages/modules/retirement/RetirementPlanning.tsx`

---

#### Task 44: Create Retirement Projections Page 📊 MEDIUM

**Status:** ⬜ Not Started | **Dependencies:** Task 20

**Actions:**

- [ ] Create `frontend/src/pages/modules/retirement/RetirementProjections.tsx`
- [ ] Review `frontend/src/pages/FinancialProjections.tsx`
- [ ] Copy projection logic
- [ ] Create `frontend/src/pages/modules/retirement/RetirementMonteCarlo.tsx`
- [ ] Review `frontend/src/pages/MonteCarloSimulation.tsx`
- [ ] Copy Monte Carlo logic
- [ ] Test both pages
- [ ] Commit changes

**Files Created:**

- `frontend/src/pages/modules/retirement/RetirementProjections.tsx`
- `frontend/src/pages/modules/retirement/RetirementMonteCarlo.tsx`

---

#### Task 45: Create Retirement Components 🎨 MEDIUM

**Status:** ⬜ Not Started | **Dependencies:** None

**Actions:**

- [ ] Create directory: `frontend/src/components/modules/retirement/`
- [ ] Create `PensionProjectionChart.tsx`
- [ ] Create `AnnualAllowanceWidget.tsx`
- [ ] Create `RetirementIncomeChart.tsx`
- [ ] Create `MonteCarloChart.tsx`
- [ ] Test components
- [ ] Commit changes

**Files Created:**

- `frontend/src/components/modules/retirement/` (4 components)

---

### IHT Planning Module Frontend (Tasks 46-50)

#### Task 46: Create IHT Planning Dashboard Page 🏛️ MEDIUM

**Status:** ⬜ Not Started | **Dependencies:** Tasks 21-24

**Actions:**

- [ ] Create `frontend/src/pages/modules/iht/IHTPlanningDashboard.tsx`
- [ ] Implement dashboard
- [ ] Commit changes

**Files Created:**

- `frontend/src/pages/modules/iht/IHTPlanningDashboard.tsx`

---

#### Task 47: Create IHT Calculator Page 💼 COMPLEX

**Status:** ⬜ Not Started | **Dependencies:** Task 22

**Actions:**

- [ ] Create `frontend/src/pages/modules/iht/IHTCalculator.tsx`
- [ ] Review `frontend/src/pages/IHTCalculatorComplete.tsx`
- [ ] Copy all IHT calculator logic
- [ ] Update API calls to module endpoints
- [ ] Test all IHT calculations
- [ ] Ensure feature parity
- [ ] Commit changes

**Files Created:**

- `frontend/src/pages/modules/iht/IHTCalculator.tsx`

---

#### Task 48: Create IHT Compliance Page 📋 MEDIUM

**Status:** ⬜ Not Started | **Dependencies:** Task 24

**Actions:**

- [ ] Create `frontend/src/pages/modules/iht/IHTCompliance.tsx`
- [ ] Review `frontend/src/pages/IHTCompliance.tsx`
- [ ] Copy compliance logic
- [ ] Update API calls
- [ ] Test compliance tools
- [ ] Commit changes

**Files Created:**

- `frontend/src/pages/modules/iht/IHTCompliance.tsx`

---

#### Task 49: Create IHT Gifts & Trusts Pages 🎁 MEDIUM

**Status:** ⬜ Not Started | **Dependencies:** Task 23

**Actions:**

- [ ] Create `frontend/src/pages/modules/iht/IHTGifts.tsx`
- [ ] Implement gift tracking interface
- [ ] Create 7-year timeline visualization
- [ ] Create `frontend/src/pages/modules/iht/IHTTrusts.tsx`
- [ ] Implement trust management interface
- [ ] Test CRUD operations
- [ ] Commit changes

**Files Created:**

- `frontend/src/pages/modules/iht/IHTGifts.tsx`
- `frontend/src/pages/modules/iht/IHTTrusts.tsx`

---

#### Task 50: Create IHT Components 🎨 MEDIUM

**Status:** ⬜ Not Started | **Dependencies:** None

**Actions:**

- [ ] Create directory: `frontend/src/components/modules/iht/`
- [ ] Create `IHTLiabilityCard.tsx`
- [ ] Create `GiftTimelineChart.tsx`
- [ ] Create `TrustManagerWidget.tsx`
- [ ] Create `IHTScenarioComparison.tsx`
- [ ] Test components
- [ ] Commit changes

**Files Created:**

- `frontend/src/components/modules/iht/` (4 components)

---

## Phase 4: Main Dashboard & Services (5 tasks)

**Estimated Time:** 2-3 days

### Task 51: Refactor Main Dashboard 🏠 COMPLEX

**Status:** ⬜ Not Started | **Dependencies:** Tasks 27, 28-50

**Actions:**

- [ ] Open `frontend/src/pages/Dashboard.tsx`
- [ ] Remove old narrative content
- [ ] Add introduction text explaining goal-based approach
- [ ] Create 5 module overview cards using ModuleDashboardCard:
  - Protection card
  - Savings card
  - Investment card
  - Retirement card
  - IHT Planning card
- [ ] Fetch data from `/api/dashboard/overview`
- [ ] Display loading states
- [ ] Handle errors gracefully
- [ ] Test responsive layout (2 columns desktop, 1 column mobile)
- [ ] Test navigation to module dashboards
- [ ] Add "Getting Started" section for new users
- [ ] Commit changes

**Files Modified:**

- `frontend/src/pages/Dashboard.tsx`

**Testing:**

- [ ] Dashboard loads correctly
- [ ] All 5 module cards display
- [ ] Navigation works
- [ ] Responsive design works
- [ ] Loading states work
- [ ] Error handling works

---

### Task 52: Create Module Service Layer 🔧 MEDIUM

**Status:** ⬜ Not Started | **Dependencies:** Tasks 6-27

**Actions:**

- [ ] Create directory: `frontend/src/services/modules/`
- [ ] Create `protection.ts` with API functions:
  - getDashboard(), getSummary(), getProducts(), createProduct(), etc.
- [ ] Create `savings.ts` with API functions
- [ ] Create `investment.ts` with API functions
- [ ] Create `retirement.ts` with API functions
- [ ] Create `iht.ts` with API functions
- [ ] Create `dashboard.ts` with getOverview() function
- [ ] Add error handling to all functions
- [ ] Add TypeScript return types
- [ ] Test functions
- [ ] Commit changes

**Files Created:**

- `frontend/src/services/modules/protection.ts`
- `frontend/src/services/modules/savings.ts`
- `frontend/src/services/modules/investment.ts`
- `frontend/src/services/modules/retirement.ts`
- `frontend/src/services/modules/iht.ts`
- `frontend/src/services/modules/dashboard.ts`

---

### Task 53: Update TypeScript Interfaces 📝 MEDIUM

**Status:** ⬜ Not Started | **Dependencies:** Task 52

**Actions:**

- [ ] Create `frontend/src/types/modules.ts`
- [ ] Define ModuleSummary interface
- [ ] Define ModuleDashboardData interface
- [ ] Define ModuleGoal interface
- [ ] Define ModuleMetric interface
- [ ] Update Product interface to include module field
- [ ] Export all interfaces
- [ ] Test TypeScript compilation
- [ ] Commit changes

**Files Created:**

- `frontend/src/types/modules.ts`

**Files Modified:**

- `frontend/src/types/product.ts` (if exists)

---

### Task 54: Implement Module Context (Optional) ⚙️ MEDIUM

**Status:** ⬜ Not Started | **Dependencies:** Tasks 51-53

**Actions:**

- [ ] Create `frontend/src/context/ModuleContext.tsx`
- [ ] Define ModuleContext with:
  - currentModule
  - setCurrentModule
  - moduleData
- [ ] Create ModuleProvider component
- [ ] Wrap App with ModuleProvider (if using)
- [ ] Test context works
- [ ] Commit changes

**Files Created:**

- `frontend/src/context/ModuleContext.tsx`

**Note:** This task is optional - evaluate if context is needed or if props are sufficient.

---

### Task 55: Create Module Navigation Helper 🧭 SIMPLE

**Status:** ⬜ Not Started | **Dependencies:** None

**Actions:**

- [ ] Create `frontend/src/utils/moduleNavigation.ts`
- [ ] Define function `getModuleRoute(module: string, subpage?: string): string`
- [ ] Define function `getModuleBreadcrumb(module: string, subpage?: string): string[]`
- [ ] Define module icon mapping
- [ ] Define module color mapping
- [ ] Test functions
- [ ] Commit changes

**Files Created:**

- `frontend/src/utils/moduleNavigation.ts`

---

## Phase 5: Navigation & Routing (8 tasks)

**Estimated Time:** 3-5 days

### Task 56: Update Header Navigation 🧭 MEDIUM

**Status:** ⬜ Not Started | **Dependencies:** Task 51

**Actions:**

- [ ] Open `frontend/src/components/layout/Header.tsx`
- [ ] Remove old navigation items:
  - Banking
  - Products
  - Analytics
  - UK Pension
  - Tax Optimisation
  - Estate Planning dropdown
- [ ] Add new navigation items:
  - Protection
  - Savings
  - Investment
  - Retirement
  - IHT Planning
- [ ] Update links to module routes
- [ ] Test navigation on desktop
- [ ] Test hover states
- [ ] Commit changes

**Files Modified:**

- `frontend/src/components/layout/Header.tsx`

---

### Task 57: Update Mobile Navigation 📱 MEDIUM

**Status:** ⬜ Not Started | **Dependencies:** Task 56

**Actions:**

- [ ] Open `frontend/src/components/layout/MobileNav.tsx`
- [ ] Update to match Header navigation structure
- [ ] Add module icons
- [ ] Test mobile navigation
- [ ] Test touch interactions
- [ ] Commit changes

**Files Modified:**

- `frontend/src/components/layout/MobileNav.tsx`

---

### Task 58: Update App Routing 🚦 COMPLEX

**Status:** ⬜ Not Started | **Dependencies:** Tasks 28-50

**Actions:**

- [ ] Open `frontend/src/App.tsx`
- [ ] Add imports for all new module pages
- [ ] Add routes for all modules:
  - `/protection` → ProtectionDashboard
  - `/protection/products` → ProtectionProducts
  - `/protection/analytics` → ProtectionAnalytics
  - `/protection/needs-analysis` → NeedsAnalysis
  - (Repeat for all 5 modules and their sub-pages)
- [ ] Keep old routes temporarily (mark for deprecation)
- [ ] Test all new routes work
- [ ] Test route transitions
- [ ] Commit changes

**Files Modified:**

- `frontend/src/App.tsx`

**Routes to Add:** (35+ routes)

- [ ] `/protection` (dashboard)
- [ ] `/protection/products`
- [ ] `/protection/analytics`
- [ ] `/protection/needs-analysis`
- [ ] `/savings` (dashboard)
- [ ] `/savings/accounts`
- [ ] `/savings/goals`
- [ ] `/savings/analytics`
- [ ] `/investment` (dashboard)
- [ ] `/investment/portfolio`
- [ ] `/investment/analytics`
- [ ] `/investment/rebalancing`
- [ ] `/investment/goals`
- [ ] `/retirement` (dashboard)
- [ ] `/retirement/pensions`
- [ ] `/retirement/planning`
- [ ] `/retirement/projections`
- [ ] `/retirement/monte-carlo`
- [ ] `/iht-planning` (dashboard)
- [ ] `/iht-planning/calculator`
- [ ] `/iht-planning/compliance`
- [ ] `/iht-planning/scenarios`
- [ ] `/iht-planning/gifts`
- [ ] `/iht-planning/trusts`

---

### Task 59: Update Breadcrumb Component 🍞 MEDIUM

**Status:** ⬜ Not Started | **Dependencies:** Task 58

**Actions:**

- [ ] Open `frontend/src/components/common/Breadcrumb.tsx`
- [ ] Add module-aware breadcrumb logic
- [ ] Display: Dashboard → Module → Page
- [ ] Use module navigation helper
- [ ] Test breadcrumbs on all module pages
- [ ] Commit changes

**Files Modified:**

- `frontend/src/components/common/Breadcrumb.tsx`

---

### Task 60: Create Module Route Guards 🔒 SIMPLE

**Status:** ⬜ Not Started | **Dependencies:** Task 58

**Actions:**

- [ ] Review authentication in `frontend/src/App.tsx`
- [ ] Ensure all module routes require authentication
- [ ] Test unauthenticated users are redirected to login
- [ ] Commit changes

**Files Modified:**

- `frontend/src/App.tsx`

---

### Task 61: Implement Redirects from Old Routes 🔀 MEDIUM

**Status:** ⬜ Not Started | **Dependencies:** Task 58

**Actions:**

- [ ] Add redirect routes in `frontend/src/App.tsx`:
  - `/products/protection` → `/protection/products`
  - `/products/investments` → `/investment/portfolio`
  - `/products/pensions` → `/retirement/pensions`
  - `/bank-accounts` → `/savings/accounts`
  - `/portfolio-analytics` → `/investment/analytics`
  - `/portfolio-rebalancing` → `/investment/rebalancing`
  - `/retirement-planning-uk` → `/retirement/planning`
  - `/financial-projections` → `/retirement/projections`
  - `/monte-carlo` → `/retirement/monte-carlo`
  - `/iht-calculator-complete` → `/iht-planning/calculator`
  - `/iht-compliance` → `/iht-planning/compliance`
- [ ] Test all redirects work
- [ ] Add deprecation notices to old routes
- [ ] Commit changes

**Files Modified:**

- `frontend/src/App.tsx`

**Redirects to Implement:**

- [ ] `/products/protection` → `/protection/products`
- [ ] `/products/investments` → `/investment/portfolio`
- [ ] `/products/pensions` → `/retirement/pensions`
- [ ] `/bank-accounts` → `/savings/accounts`
- [ ] `/portfolio-analytics` → `/investment/analytics`
- [ ] `/portfolio-rebalancing` → `/investment/rebalancing`
- [ ] `/retirement-planning-uk` → `/retirement/planning`
- [ ] `/financial-projections` → `/retirement/projections`
- [ ] `/monte-carlo` → `/retirement/monte-carlo`
- [ ] `/iht-calculator-complete` → `/iht-planning/calculator`
- [ ] `/iht-compliance` → `/iht-planning/compliance`

---

### Task 62: Update Learning Centre Links 📚 SIMPLE

**Status:** ⬜ Not Started | **Dependencies:** None

**Actions:**

- [ ] Review documentation files in `docs/`
- [ ] Update links to reference new module structure
- [ ] Update help content in Learning Centre
- [ ] Update any hardcoded route references
- [ ] Test all documentation links work
- [ ] Commit changes

**Files Modified:**

- `docs/*.md` (as needed)
- `frontend/src/pages/LearningCentre.tsx` (if needed)

---

### Task 63: Update Settings Page Links ⚙️ SIMPLE

**Status:** ⬜ Not Started | **Dependencies:** None

**Actions:**

- [ ] Open `frontend/src/pages/Settings.tsx`
- [ ] Review any module-related links
- [ ] Update if needed
- [ ] Test settings page
- [ ] Commit changes

**Files Modified:**

- `frontend/src/pages/Settings.tsx` (if needed)

---

## Phase 6: Deprecation & Cleanup (7 tasks)

**Estimated Time:** 2-3 days

### Task 64: Mark Old Pages as Deprecated 🚧 SIMPLE

**Status:** ⬜ Not Started | **Dependencies:** Tasks 56-63

**Actions:**

- [ ] Add deprecation banner to `frontend/src/pages/ProductsOverview.tsx`
- [ ] Add deprecation banner to `frontend/src/pages/PortfolioAnalytics.tsx`
- [ ] Add deprecation banner to `frontend/src/pages/PortfolioRebalancing.tsx`
- [ ] Add deprecation banner to `frontend/src/pages/BankAccounts.tsx`
- [ ] Banners should redirect users to new module pages
- [ ] Test banners display correctly
- [ ] Commit changes

**Files Modified:**

- Multiple old page files

---

### Task 65: Archive Old Components 📦 SIMPLE

**Status:** ⬜ Not Started | **Dependencies:** Task 64

**Actions:**

- [ ] Create `frontend/src/components/deprecated/`
- [ ] Move old product-related components to deprecated folder
- [ ] Update any remaining imports (should be minimal)
- [ ] Test build succeeds
- [ ] Commit changes

**Files Modified:**

- Component organization

---

### Task 66: Remove Old API Endpoints 🗑️ MEDIUM

**Status:** ⬜ Not Started | **Dependencies:** Task 61

**Actions:**

- [ ] Add deprecation warnings to old backend endpoints
- [ ] Log warnings when old endpoints are called
- [ ] Document migration path in API docs
- [ ] Set sunset date (e.g., 30 days from now)
- [ ] Test warnings appear in logs
- [ ] Commit changes

**Files Modified:**

- Old API router files

---

### Task 67: Update Database Products 🗄️ MEDIUM

**Status:** ⬜ Not Started | **Dependencies:** Task 3

**Actions:**

- [ ] Create `backend/scripts/migrate_products_to_modules.py`
- [ ] Write migration script:
  - `UPDATE products SET module = 'protection' WHERE product_type = 'protection'`
  - `UPDATE products SET module = 'savings' WHERE product_type IN ('savings', 'cash')`
  - `UPDATE products SET module = 'investment' WHERE product_type = 'investment'`
  - `UPDATE products SET module = 'retirement' WHERE product_type = 'pension'`
- [ ] Add data validation checks
- [ ] Backup database before running
- [ ] Run migration script
- [ ] Verify all products have module assigned
- [ ] Check for any NULL module values
- [ ] Commit script

**Files Created:**

- `backend/scripts/migrate_products_to_modules.py`

---

### Task 68: Remove Deprecated Frontend Pages 🧹 SIMPLE

**Status:** ⬜ Not Started | **Dependencies:** Tasks 61, 67

**Actions:**

- [ ] Delete `frontend/src/pages/ProductsOverview.tsx`
- [ ] Delete `frontend/src/pages/PortfolioAnalytics.tsx` (logic moved to Investment)
- [ ] Delete `frontend/src/pages/PortfolioRebalancing.tsx` (logic moved to Investment)
- [ ] Delete `frontend/src/pages/BankAccounts.tsx` (logic moved to Savings)
- [ ] Keep old IHT pages temporarily as reference
- [ ] Remove imports from `App.tsx`
- [ ] Test build succeeds
- [ ] Test no broken links
- [ ] Commit changes

**Files Deleted:**

- Multiple old page files

---

### Task 69: Remove Deprecated Backend Endpoints 🧹 MEDIUM

**Status:** ⬜ Not Started | **Dependencies:** Task 66

**Actions:**

- [ ] After sunset period (e.g., 30 days), remove old endpoints
- [ ] Comment out old routers in `main.py`
- [ ] Move old router files to `backend/app/api/deprecated/`
- [ ] Test all module endpoints still work
- [ ] Update API documentation
- [ ] Commit changes

**Files Modified:**

- `backend/app/main.py`
- Old API router files moved

---

### Task 70: Clean Up Dependencies 🧹 SIMPLE

**Status:** ⬜ Not Started | **Dependencies:** Tasks 68, 69

**Actions:**

- [ ] Review `frontend/package.json`
- [ ] Check for unused packages: `npm run check-unused` (if you have this script)
- [ ] Remove unused packages
- [ ] Review `backend/requirements.txt`
- [ ] Remove unused packages
- [ ] Test builds still work
- [ ] Commit changes

**Files Modified:**

- `frontend/package.json`
- `backend/requirements.txt`

---

## Phase 7: Testing & Documentation (8 tasks)

**Estimated Time:** 3-5 days

### Task 71: Write Module API Tests 🧪 COMPLEX

**Status:** ⬜ Not Started | **Dependencies:** Tasks 6-27

**Actions:**

- [ ] Create `backend/tests/test_modules_protection.py`
- [ ] Write tests for Protection API (all endpoints)
- [ ] Create `backend/tests/test_modules_savings.py`
- [ ] Write tests for Savings API
- [ ] Create `backend/tests/test_modules_investment.py`
- [ ] Write tests for Investment API
- [ ] Create `backend/tests/test_modules_retirement.py`
- [ ] Write tests for Retirement API
- [ ] Create `backend/tests/test_modules_iht.py`
- [ ] Write tests for IHT API
- [ ] Target: 100% endpoint coverage
- [ ] Run all tests: `pytest backend/tests/test_modules_*.py -v`
- [ ] Check coverage: `pytest --cov=app backend/tests/test_modules_*.py`
- [ ] Commit tests

**Files Created:**

- 5 new test files

**Testing Goals:**

- [ ] All endpoints tested
- [ ] Coverage >90%
- [ ] All tests pass

---

### Task 72: Write Frontend Component Tests 🧪 MEDIUM

**Status:** ⬜ Not Started | **Dependencies:** Tasks 28-50

**Actions:**

- [ ] Create test files for module components
- [ ] Test Protection components
- [ ] Test Savings components
- [ ] Test Investment components
- [ ] Test Retirement components
- [ ] Test IHT components
- [ ] Test shared module components
- [ ] Run tests: `npm test`
- [ ] Check coverage: `npm test -- --coverage`
- [ ] Commit tests

**Files Created:**

- `frontend/src/components/modules/**/__tests__/`

**Testing Goals:**

- [ ] All components tested
- [ ] Coverage >80%
- [ ] All tests pass

---

### Task 73: Write E2E Tests 🧪 COMPLEX

**Status:** ⬜ Not Started | **Dependencies:** Tasks 56-63

**Actions:**

- [ ] Set up E2E testing framework (Playwright/Cypress if not already)
- [ ] Write test: Main dashboard → Module dashboard navigation
- [ ] Write test: Module CRUD operations (create, edit, delete product)
- [ ] Write test: Analytics views load correctly
- [ ] Write test: Forms validation works
- [ ] Write test: Mobile navigation
- [ ] Run E2E tests
- [ ] All tests must pass
- [ ] Commit tests

**Files Created:**

- `e2e/modules.spec.ts` (or similar)

**Test Scenarios:**

- [ ] Dashboard to module navigation
- [ ] Product CRUD in each module
- [ ] Analytics page loads
- [ ] Form validation
- [ ] Mobile responsive

---

### Task 74: Update API Documentation 📚 MEDIUM

**Status:** ⬜ Not Started | **Dependencies:** Task 26

**Actions:**

- [ ] Open `docs/API_DOCUMENTATION.md`
- [ ] Document all new module endpoints
- [ ] Add request/response examples
- [ ] Document data models (ModuleGoal, ModuleMetric)
- [ ] Add usage examples
- [ ] Update Swagger inline documentation
- [ ] Test Swagger UI at http://localhost:8000/docs
- [ ] Verify all endpoints documented
- [ ] Commit changes

**Files Modified:**

- `docs/API_DOCUMENTATION.md`
- Backend router files (docstrings)

---

### Task 75: Update User Guide 📖 MEDIUM

**Status:** ⬜ Not Started | **Dependencies:** Task 51

**Actions:**

- [ ] Open `docs/USER_GUIDE.md`
- [ ] Add section on goal-based modules
- [ ] Document each of the 5 modules
- [ ] Add screenshots of new dashboards
- [ ] Update navigation guide
- [ ] Add "Getting Started" section
- [ ] Add FAQ for module structure
- [ ] Review and update entire guide
- [ ] Commit changes

**Files Modified:**

- `docs/USER_GUIDE.md`

---

### Task 76: Update Developer Documentation 📝 MEDIUM

**Status:** ⬜ Not Started | **Dependencies:** Tasks 1-70

**Actions:**

- [ ] Open `CLAUDE.md`
- [ ] Update architecture diagrams
- [ ] Document new module structure
- [ ] Update file organization sections
- [ ] Update API endpoints section
- [ ] Update contribution guidelines
- [ ] Open `README.md`
- [ ] Update project description
- [ ] Update routes section
- [ ] Update architecture overview
- [ ] Update screenshots
- [ ] Open `docs/DEVELOPER_DOCUMENTATION.md`
- [ ] Update with module details
- [ ] Open `docs/ARCHITECTURE.md`
- [ ] Update architecture diagrams
- [ ] Commit all changes

**Files Modified:**

- `CLAUDE.md`
- `README.md`
- `docs/DEVELOPER_DOCUMENTATION.md`
- `docs/ARCHITECTURE.md`

---

### Task 77: Create Migration Guide 📋 MEDIUM

**Status:** ⬜ Not Started | **Dependencies:** Task 76

**Actions:**

- [ ] Create `docs/MIGRATION_GUIDE.md`
- [ ] Document what changed (old → new structure)
- [ ] Create navigation comparison table
- [ ] Map old routes to new routes
- [ ] Add FAQ section
- [ ] Add "Where did X go?" section
- [ ] Add troubleshooting tips
- [ ] Commit guide

**Files Created:**

- `docs/MIGRATION_GUIDE.md`

---

### Task 78: Update Video Tutorials 🎥 MEDIUM

**Status:** ⬜ Not Started | **Dependencies:** Task 75

**Actions:**

- [ ] Open `docs/VIDEO_TUTORIALS.md`
- [ ] Update existing tutorial references
- [ ] Script new module overview tutorial
- [ ] Script module-specific tutorials (5 tutorials, one per module)
- [ ] Mark old tutorials as deprecated
- [ ] Link to new tutorials
- [ ] Update learning centre to reference new videos
- [ ] Commit changes

**Files Modified:**

- `docs/VIDEO_TUTORIALS.md`

---

## Completion Checklist

### Before Declaring Complete

- [ ] All 78 tasks completed
- [ ] Backend builds without errors
- [ ] Frontend builds without errors
- [ ] All tests passing (backend + frontend + E2E)
- [ ] No TypeScript errors
- [ ] No console errors in browser
- [ ] Documentation updated
- [ ] Migration guide created
- [ ] Old routes redirect correctly
- [ ] All module dashboards functional
- [ ] All CRUD operations work
- [ ] Performance acceptable (<1s dashboard load)
- [ ] Mobile responsive design verified
- [ ] Dark mode works throughout

### Post-Launch Monitoring

- [ ] Monitor user feedback
- [ ] Track analytics on module usage
- [ ] Monitor API performance
- [ ] Watch for error reports
- [ ] Prepare for AI integration phase (future)

---

## Notes

- **Estimated Total Time:** 24-36 development days
- **Complexity Distribution:**
  - Simple: 15 tasks
  - Medium: 45 tasks
  - Complex: 18 tasks
- **Critical Path:** Tasks 2 → 3 → 6-27 → 51 → 56-58 → 67
- **High Risk Tasks:** 22 (IHT calculator), 43 (Retirement planning), 51 (Main dashboard), 67 (Data migration)

**Last Updated:** 2025-09-30
**Status:** Ready for Implementation