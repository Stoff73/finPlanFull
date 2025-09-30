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

