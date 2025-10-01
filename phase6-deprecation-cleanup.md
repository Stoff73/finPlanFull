## Phase 6: Deprecation & Cleanup (7 tasks)

**Estimated Time:** 2-3 days

### Task 64: Mark Old Pages as Deprecated 🚧 SIMPLE

**Status:** ✅ Completed | **Dependencies:** Tasks 56-63

**Actions:**

- [x] Add deprecation banner to `frontend/src/pages/ProductsOverview.tsx`
- [x] Add deprecation banner to `frontend/src/pages/PortfolioAnalytics.tsx`
- [x] Add deprecation banner to `frontend/src/pages/PortfolioRebalancing.tsx`
- [x] Add deprecation banner to `frontend/src/pages/BankAccounts.tsx`
- [x] Banners should redirect users to new module pages
- [x] Test banners display correctly
- [x] Commit changes

**Files Modified:**

- `frontend/src/components/common/DeprecationBanner.tsx` (new)
- All 4 old page files updated with banners

---

### Task 65: Archive Old Components 📦 SIMPLE

**Status:** ✅ Completed (SKIPPED) | **Dependencies:** Task 64

**Actions:**

- [x] No old components found to archive
- [x] Pension components still in use (PensionDashboardWidget, SchemeCard, etc.)
- [x] Task skipped as not applicable

**Files Modified:**

- None

---

### Task 66: Remove Old API Endpoints 🗑️ MEDIUM

**Status:** ✅ Completed (DEFERRED) | **Dependencies:** Task 61

**Actions:**

- [x] Deferred to future release - old endpoints still in use
- [x] Will add deprecation warnings in later phase
- [x] Module endpoints taking priority

**Files Modified:**

- None (deferred)

---

### Task 67: Update Database Products 🗄️ MEDIUM

**Status:** ✅ Completed | **Dependencies:** Task 3

**Actions:**

- [x] Create `backend/scripts/migrate_products_to_modules.py`
- [x] Write migration script with module mapping
- [x] Add automatic column creation if missing
- [x] Add data validation checks
- [x] Add database backup functionality (SQLite)
- [x] Implement dry-run mode for testing
- [x] Add migration summary and reporting
- [x] Test script successfully
- [x] Commit script

**Files Created:**

- `backend/scripts/migrate_products_to_modules.py` (313 lines)

**Features:**
- Auto-creates `module` column if not exists
- Validates data before and after migration
- Supports dry-run mode (`--dry-run`)
- Creates automatic database backups
- Detailed progress reporting

---

### Task 68: Remove Deprecated Frontend Pages 🧹 SIMPLE

**Status:** ✅ Completed | **Dependencies:** Tasks 61, 67

**Actions:**

- [x] Delete `frontend/src/pages/ProductsOverview.tsx`
- [x] Delete `frontend/src/pages/PortfolioAnalytics.tsx` (logic moved to Investment)
- [x] Delete `frontend/src/pages/PortfolioRebalancing.tsx` (logic moved to Investment)
- [x] Delete `frontend/src/pages/BankAccounts.tsx` (logic moved to Savings)
- [x] Keep old IHT pages temporarily as reference
- [x] Remove imports from `App.tsx`
- [x] Replace `/products` route with redirect to `/retirement`
- [x] Test build succeeds
- [x] Test no broken links
- [x] Commit changes

**Files Deleted:**

- `frontend/src/pages/ProductsOverview.tsx` (333 lines)
- `frontend/src/pages/PortfolioAnalytics.tsx` (592 lines)
- `frontend/src/pages/PortfolioRebalancing.tsx` (533 lines)
- `frontend/src/pages/BankAccounts.tsx` (1067 lines)

**Total:** 2,525 lines removed

---

### Task 69: Remove Deprecated Backend Endpoints 🧹 MEDIUM

**Status:** ✅ Completed (DEFERRED) | **Dependencies:** Task 66

**Actions:**

- [x] Deferred to future release (after sunset period)
- [x] Old endpoints still needed for backward compatibility
- [x] Will implement in Phase 7 after monitoring usage

**Files Modified:**

- None (deferred)

---

### Task 70: Clean Up Dependencies 🧹 SIMPLE

**Status:** ✅ Completed (MINIMAL CHANGES) | **Dependencies:** Tasks 68, 69

**Actions:**

- [x] Review frontend dependencies - all still in use
- [x] Review backend dependencies - all still in use
- [x] No unused packages found after page removal
- [x] Build sizes reduced due to code removal (611kb vs 615kb)
- [x] Task complete with no changes needed

**Files Modified:**

- None (no unused dependencies found)

---

