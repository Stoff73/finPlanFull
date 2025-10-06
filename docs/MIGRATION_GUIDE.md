# Migration Guide: Goal-Based Modules

**Version 2.0 - Goal-Based Module Structure**

Last Updated: 2025-10-01

---

## Overview

Version 2.0 introduces a **goal-based module structure** that replaces the old product-centric approach. This guide helps you transition smoothly to the new structure.

**What Changed?**
- Financial planning now organized around 5 life goals (Protection, Savings, Investment, Retirement, IHT Planning)
- New module-specific dashboards with focused insights
- Consistent navigation and user experience across modules
- Deprecated old product pages in favor of module pages

**What Stayed the Same?**
- All your existing data is preserved
- Authentication and account settings unchanged
- Financial statements, tax optimization, and reports still available
- Learning Centre and documentation access

---

## Navigation Changes

### Old Structure (v1.x)
```
Main Dashboard
├── Products Overview
├── Pensions (all pensions in one page)
├── Investments (all investments in one page)
├── Protection (all policies in one page)
├── IHT Calculator
└── Settings
```

### New Structure (v2.0)
```
Main Dashboard (shows 5 module cards)
├── Protection Module
│   ├── Dashboard
│   ├── Portfolio (manage policies)
│   ├── Analytics
│   └── Needs Analysis
├── Savings Module
│   ├── Dashboard
│   ├── Accounts
│   ├── Goals
│   └── Analytics
├── Investment Module
│   ├── Dashboard
│   ├── Portfolio
│   ├── Analytics
│   └── Rebalancing
├── Retirement Module
│   ├── Dashboard
│   ├── Pensions
│   ├── Projections
│   └── Monte Carlo
├── IHT Planning Module
│   ├── Dashboard
│   ├── Calculator
│   ├── Gifts
│   └── Trusts
└── Settings
```

---

## Route Mapping: Where Did Everything Go?

### Main Dashboard
**Old**: `/dashboard` (basic metrics)
**New**: `/dashboard` (**improved with module cards and narrative storytelling**)

### Protection / Insurance

| Old Route | New Route | Notes |
|-----------|-----------|-------|
| `/protection` | `/modules/protection/portfolio` | Manage all policies |
| N/A | `/modules/protection/dashboard` | **NEW**: Overview with coverage analysis |
| N/A | `/modules/protection/analytics` | **NEW**: Coverage analytics |
| N/A | `/modules/protection/needs-analysis` | **NEW**: Calculate coverage needs |

### Savings

| Old Route | New Route | Notes |
|-----------|-----------|-------|
| `/bank-accounts` | `/modules/savings/accounts` | Manage savings accounts |
| N/A | `/modules/savings/dashboard` | **NEW**: Emergency fund tracking |
| N/A | `/modules/savings/goals` | **NEW**: Set and track goals |
| N/A | `/modules/savings/analytics` | **NEW**: Savings trends |

### Investments

| Old Route | New Route | Notes |
|-----------|-----------|-------|
| `/investments` | `/modules/investment/portfolio` | Manage investments |
| `/portfolio-analytics` | `/modules/investment/analytics` | Performance analytics |
| `/portfolio-rebalancing` | `/modules/investment/rebalancing` | Rebalancing tool |
| N/A | `/modules/investment/dashboard` | **NEW**: Portfolio overview |

### Retirement / Pensions

| Old Route | New Route | Notes |
|-----------|-----------|-------|
| `/pensions` | `/modules/retirement/pensions` | Manage pensions |
| `/retirement-planning` | `/modules/retirement/projections` | Retirement projections |
| `/monte-carlo` | `/modules/retirement/monte-carlo` | Monte Carlo simulation |
| N/A | `/modules/retirement/dashboard` | **NEW**: Retirement readiness |
| `/retirement-planning-uk` | `/retirement-planning-uk` | **Unchanged**: UK pension features |

### IHT Planning

| Old Route | New Route | Notes |
|-----------|-----------|-------|
| `/iht-calculator` | `/modules/iht/calculator` | IHT calculator |
| `/iht-calculator-enhanced` | `/modules/iht/dashboard` | Enhanced IHT features |
| `/iht-calculator-complete` | `/modules/iht/dashboard` | Complete IHT suite |
| N/A | `/modules/iht/gifts` | **NEW**: Manage gifts (7-year rule) |
| N/A | `/modules/iht/trusts` | **NEW**: Manage trusts |
| `/iht-compliance` | `/iht-compliance` | **Unchanged**: IHT400 compliance |

### Unchanged Pages

| Route | Status | Notes |
|-------|--------|-------|
| `/financial-statements` | ✅ Unchanged | Balance sheet, P&L, cash flow |
| `/financial-projections` | ✅ Unchanged | Multi-year projections |
| `/tax-optimization` | ✅ Unchanged | Tax planning |
| `/chat` | ✅ Unchanged | AI assistant |
| `/learning-centre` | ✅ Unchanged | Documentation browser |
| `/settings` | ✅ Unchanged | User preferences |

---

## API Endpoint Changes

### Old API Structure
```
/api/products/pensions
/api/products/investments
/api/products/protection
/api/iht/calculate
```

### New API Structure
```
/api/modules/protection/dashboard
/api/modules/protection/products
/api/modules/savings/dashboard
/api/modules/savings/accounts
/api/modules/investment/dashboard
/api/modules/investment/portfolio
/api/modules/retirement/dashboard
/api/modules/retirement/pensions
/api/modules/iht/dashboard
/api/modules/iht/calculator
```

**All modules now have consistent endpoints**:
- `/dashboard` - Comprehensive module dashboard
- `/summary` - Quick summary for main dashboard
- CRUD endpoints for module entities
- `/analytics` - Module-specific analytics

**Old endpoints are deprecated but still functional** for backward compatibility.

---

## Data Migration

**Good News**: Your data is automatically migrated!

### What Happened to Your Data?

1. **Products Table Enhancement**:
   - All products now have a `module` field
   - `module` values: `protection`, `savings`, `investment`, `retirement`, `iht`
   - Old products automatically assigned to correct modules

2. **Data Preserved**:
   - All your pensions → `module='retirement'`
   - All your investments → `module='investment'`
   - All your protection policies → `module='protection'`
   - Bank accounts → `module='savings'`
   - IHT data → `module='iht'`

3. **No Data Loss**:
   - All historical data preserved
   - All relationships intact
   - All calculations still work

### Verifying Your Data

After updating, verify your data appears correctly:

1. **Check Main Dashboard**: See 5 module cards with your data
2. **Check Each Module**: Navigate to each module dashboard
3. **Check Legacy Pages**: Old pages still show deprecation banners

**If you see any issues**, please contact support.

---

## Features You'll Love

### 1. Focused Dashboards
Each module has its own dashboard showing only relevant information:
- **Protection**: Coverage adequacy, premium efficiency
- **Savings**: Emergency fund status, months of expenses
- **Investment**: Gain/loss, asset allocation
- **Retirement**: Retirement readiness, projected income
- **IHT**: Estate value, IHT liability

### 2. Consistent Experience
All modules follow the same pattern:
- Dashboard → Overview with key metrics
- Portfolio/Accounts/Pensions → Manage your products
- Analytics → Detailed insights
- Module-specific tools (Needs Analysis, Goals, Rebalancing, etc.)

### 3. Narrative Storytelling
The new dashboard uses conversational language:
- "You're worth £325,000 after debts"
- "You have 8.3 months of expenses saved - excellent!"
- "Your investments are performing well with a 25% gain"

### 4. Better Navigation
- Module cards on main dashboard show status at a glance
- Breadcrumb navigation shows where you are
- Clear "Back to Dashboard" links

---

## Common Questions

### Q: Where did "Products Overview" go?
**A**: Replaced by module-specific dashboards. Each module (Protection, Savings, Investment, Retirement) now has its own focused dashboard.

### Q: Can I still access old pages?
**A**: Yes, old pages show deprecation banners but remain functional during transition period. They will be removed in a future version.

### Q: Will my bookmarks still work?
**A**: Old bookmarks redirect to new pages automatically. Update your bookmarks to new routes for best experience.

### Q: Do I need to re-enter my data?
**A**: No! All your data is automatically migrated. Just navigate to the new module dashboards to see it.

### Q: How do I add a new pension/investment/policy?
**A**: Navigate to the relevant module (e.g., Retirement Module → Pensions → Add Pension).

### Q: Where is the "Products" menu?
**A**: Replaced by "Modules" in the navigation. Click any module card on the main dashboard to access module pages.

### Q: What happened to Monte Carlo simulation?
**A**: Moved to **Retirement Module → Monte Carlo** (same functionality, better location).

### Q: Where are my IHT calculations?
**A**: All IHT features now in **IHT Planning Module**. Your saved profiles are preserved.

### Q: Can I export reports like before?
**A**: Yes, export functionality is unchanged. Access via Settings → Data & Reports.

---

## Troubleshooting

### Issue: I can't find my data

**Solution**:
1. Check the correct module dashboard
2. Verify products aren't archived (check status filter)
3. Try refreshing the page (Cmd/Ctrl + R)
4. Clear browser cache if needed

### Issue: Dashboard looks different

**Solution**:
This is expected! The new dashboard uses narrative storytelling. Your data is the same, just presented differently.

### Issue: Old bookmarks don't work

**Solution**:
Most old routes redirect automatically. If not, use the navigation menu to find the new location (see Route Mapping table above).

### Issue: Module cards show wrong data

**Solution**:
1. Refresh the page
2. Check that you're logged in
3. Verify data exists in module-specific pages
4. Contact support if issue persists

### Issue: Deprecation banners are annoying

**Solution**:
Update your bookmarks to new routes. Deprecation banners will be removed in future versions.

---

## Getting Help

**Documentation**:
- User Guide: `/learning-centre` → "Goal-Based Modules" section
- API Documentation: `/learning-centre` → "API Documentation"
- Video Tutorials: `/learning-centre` → "Video Tutorials"

**Support**:
- Report issues: GitHub Issues
- Questions: Learning Centre FAQ

**Feedback**:
We'd love to hear what you think! Please share feedback through the app or GitHub.

---

## Timeline

**Now (v2.0)**:
- ✅ Goal-based modules live
- ✅ Old pages marked deprecated but functional
- ✅ Automatic data migration complete
- ✅ Documentation updated

**Next (v2.1) - Q1 2026**:
- Remove deprecation banners
- Old routes permanently redirect
- Enhanced module features

**Future (v3.0) - Q2 2026**:
- Complete removal of legacy pages
- New module features (Goals, AI insights, etc.)
- Mobile app with module structure

---

**Thank you for using our Financial Planning Application!**

The goal-based module structure makes financial planning clearer, more focused, and easier to understand. We hope you love it as much as we enjoyed building it.

*Questions? Visit the Learning Centre or contact support.*
