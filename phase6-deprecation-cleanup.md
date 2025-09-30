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

