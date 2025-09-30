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

