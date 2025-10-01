## Phase 5: Navigation & Routing (8 tasks)

**Estimated Time:** 3-5 days
**Status:** ✅ COMPLETED

### Task 56: Update Header Navigation 🧭 MEDIUM

**Status:** ✅ COMPLETED | **Dependencies:** Task 51

**Actions:**

- [x] Open `frontend/src/components/layout/Header.tsx`
- [x] Remove old navigation items:
  - Banking
  - Products
  - Analytics
  - UK Pension
  - Tax Optimisation
  - Estate Planning dropdown
- [x] Add new navigation items:
  - Protection
  - Savings
  - Investment
  - Retirement
  - IHT Planning
- [x] Update links to module routes
- [x] Test navigation on desktop
- [x] Test hover states
- [x] Commit changes

**Files Modified:**

- `frontend/src/components/layout/Header.tsx`

---

### Task 57: Update Mobile Navigation 📱 MEDIUM

**Status:** ✅ COMPLETED | **Dependencies:** Task 56

**Actions:**

- [x] Open `frontend/src/components/layout/MobileNav.tsx`
- [x] Update to match Header navigation structure
- [x] Add module icons
- [x] Test mobile navigation
- [x] Test touch interactions
- [x] Commit changes

**Files Modified:**

- `frontend/src/components/layout/MobileNav.tsx`

---

### Task 58: Update App Routing 🚦 COMPLEX

**Status:** ✅ COMPLETED | **Dependencies:** Tasks 28-50

**Actions:**

- [x] Open `frontend/src/App.tsx`
- [x] Add imports for all new module pages
- [x] Add routes for all modules:
  - `/protection` → ProtectionDashboard
  - `/protection/products` → ProtectionProducts
  - `/protection/analytics` → ProtectionAnalytics
  - `/protection/needs-analysis` → NeedsAnalysis
  - (Repeat for all 5 modules and their sub-pages)
- [x] Keep old routes temporarily (mark for deprecation)
- [x] Test all new routes work
- [x] Test route transitions
- [x] Commit changes

**Files Modified:**

- `frontend/src/App.tsx`

**Routes to Add:** (35+ routes)

- [x] `/protection` (dashboard)
- [x] `/protection/products`
- [x] `/protection/analytics`
- [x] `/protection/needs-analysis`
- [x] `/savings` (dashboard)
- [x] `/savings/accounts`
- [x] `/savings/goals`
- [x] `/savings/analytics`
- [x] `/investment` (dashboard)
- [x] `/investment/portfolio`
- [x] `/investment/analytics`
- [x] `/investment/rebalancing`
- [x] `/investment/goals`
- [x] `/retirement` (dashboard)
- [x] `/retirement/pensions`
- [x] `/retirement/planning`
- [x] `/retirement/projections`
- [x] `/retirement/monte-carlo`
- [x] `/iht-planning` (dashboard)
- [x] `/iht-planning/calculator`
- [x] `/iht-planning/compliance`
- [x] `/iht-planning/scenarios`
- [x] `/iht-planning/gifts`
- [x] `/iht-planning/trusts`

---

### Task 59: Update Breadcrumb Component 🍞 MEDIUM

**Status:** ✅ COMPLETED | **Dependencies:** Task 58

**Actions:**

- [x] Open `frontend/src/components/common/Breadcrumb.tsx`
- [x] Add module-aware breadcrumb logic
- [x] Display: Dashboard → Module → Page
- [x] Use module navigation helper
- [x] Test breadcrumbs on all module pages
- [x] Commit changes

**Files Modified:**

- `frontend/src/components/common/Breadcrumb.tsx`

---

### Task 60: Create Module Route Guards 🔒 SIMPLE

**Status:** ✅ COMPLETED | **Dependencies:** Task 58

**Actions:**

- [x] Review authentication in `frontend/src/App.tsx`
- [x] Ensure all module routes require authentication
- [x] Test unauthenticated users are redirected to login
- [x] Commit changes

**Files Modified:**

- `frontend/src/App.tsx`

---

### Task 61: Implement Redirects from Old Routes 🔀 MEDIUM

**Status:** ✅ COMPLETED | **Dependencies:** Task 58

**Actions:**

- [x] Add redirect routes in `frontend/src/App.tsx`:
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
- [x] Test all redirects work
- [x] Add deprecation notices to old routes
- [x] Commit changes

**Files Modified:**

- `frontend/src/App.tsx`

**Redirects to Implement:**

- [x] `/products/protection` → `/protection/products`
- [x] `/products/investments` → `/investment/portfolio`
- [x] `/products/pensions` → `/retirement/pensions`
- [x] `/bank-accounts` → `/savings/accounts`
- [x] `/portfolio-analytics` → `/investment/analytics`
- [x] `/portfolio-rebalancing` → `/investment/rebalancing`
- [x] `/retirement-planning-uk` → `/retirement/planning`
- [x] `/financial-projections` → `/retirement/projections`
- [x] `/monte-carlo` → `/retirement/monte-carlo`
- [x] `/iht-calculator-complete` → `/iht-planning/calculator`
- [x] `/iht-compliance` → `/iht-planning/compliance`

---

### Task 62: Update Learning Centre Links 📚 SIMPLE

**Status:** ✅ COMPLETED | **Dependencies:** None

**Actions:**

- [x] Review documentation files in `docs/`
- [x] Update links to reference new module structure
- [x] Update help content in Learning Centre
- [x] Update any hardcoded route references
- [x] Test all documentation links work
- [x] Commit changes

**Notes:** No hardcoded route references found in documentation. All routes use relative paths or are handled by redirects.

**Files Modified:**

- `docs/*.md` (as needed)
- `frontend/src/pages/LearningCentre.tsx` (if needed)

---

### Task 63: Update Settings Page Links ⚙️ SIMPLE

**Status:** ✅ COMPLETED | **Dependencies:** None

**Actions:**

- [x] Open `frontend/src/pages/Settings.tsx`
- [x] Review any module-related links
- [x] Update if needed
- [x] Test settings page
- [x] Commit changes

**Notes:** No changes needed. Settings page only links to `/financial-statements` which is a valid legacy route.

**Files Modified:**

- `frontend/src/pages/Settings.tsx` (if needed)

---

