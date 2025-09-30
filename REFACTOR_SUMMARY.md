# Goal-Based Refactor - Executive Summary

## What We're Doing

Transforming the Financial Planning application from a **feature-based** structure to a **goal-based modular** architecture organized around 5 financial planning objectives.

## The 5 Core Modules

### 1. 🛡️ Protection
**Goal:** Secure your family's financial future
- Life insurance, critical illness, income protection
- Products moved from: `/products/protection`
- New location: `/protection/*`

### 2. 💰 Savings
**Goal:** Build emergency funds and short-term savings
- Bank accounts, cash ISAs, savings goals
- Products moved from: `/bank-accounts`, savings from products
- New location: `/savings/*`

### 3. 📈 Investment
**Goal:** Grow wealth for medium to long-term objectives
- Investment portfolio, analytics, rebalancing
- Products moved from: `/products/investments`, `/portfolio-analytics`, `/portfolio-rebalancing`
- New location: `/investment/*`

### 4. 🏖️ Retirement
**Goal:** Plan for a comfortable retirement
- Pensions, retirement planning, projections, Monte Carlo
- Products moved from: `/products/pensions`, `/retirement-planning-uk`, `/financial-projections`, `/monte-carlo`
- New location: `/retirement/*`

### 5. 🏛️ Inheritance Tax Planning
**Goal:** Preserve wealth for future generations
- IHT calculator, compliance, gift tracking, trusts
- Features moved from: `/iht-calculator-complete`, `/iht-compliance`, etc.
- New location: `/iht-planning/*`

## What Gets Removed

### Navigation Items (Header)
- ❌ Products
- ❌ Analytics
- ❌ Banking (standalone)
- ❌ UK Pension (standalone)
- ❌ Tax Optimisation (standalone)
- ❌ Estate Planning (dropdown)

### Pages to Deprecate
- `ProductsOverview.tsx` → Functionality distributed across modules
- `PortfolioAnalytics.tsx` → Moved to Investment module
- `PortfolioRebalancing.tsx` → Moved to Investment module
- `BankAccounts.tsx` → Refactored into Savings module
- Old IHT pages → Consolidated into IHT Planning module

## What Gets Added

### New Navigation (Header)
- ✅ Dashboard (refactored to show module overview)
- ✅ Protection
- ✅ Savings
- ✅ Investment
- ✅ Retirement
- ✅ IHT Planning
- ✅ AI Assistant (unchanged)
- ✅ Learning Centre (unchanged)
- ✅ Settings (unchanged)

### New Page Structure (35 new pages)
```
Dashboard (refactored)
├── Protection/
│   ├── Dashboard
│   ├── Products
│   ├── Analytics
│   └── Needs Analysis
├── Savings/
│   ├── Dashboard
│   ├── Accounts
│   ├── Goals
│   └── Analytics
├── Investment/
│   ├── Dashboard
│   ├── Portfolio
│   ├── Analytics
│   ├── Rebalancing
│   └── Goals
├── Retirement/
│   ├── Dashboard
│   ├── Pensions
│   ├── Planning
│   ├── Projections
│   └── Monte Carlo
└── IHT Planning/
    ├── Dashboard
    ├── Calculator
    ├── Compliance
    ├── Scenarios
    ├── Gifts
    └── Trusts
```

## User Experience Changes

### Before: Feature-Based Navigation
```
User thinks: "I need to check my bank accounts"
→ Clicks "Banking"
→ Sees bank accounts

User thinks: "I want to see my pensions"
→ Clicks "Products" → "Pensions"
→ Sees pensions
```

### After: Goal-Based Navigation
```
User thinks: "I want to work on my emergency fund"
→ Clicks "Savings"
→ Sees Savings Dashboard with emergency fund status, accounts, goals

User thinks: "I need to plan for retirement"
→ Clicks "Retirement"
→ Sees Retirement Dashboard with pension pot, projections, planning tools
```

## Main Dashboard Transformation

### Before
- Narrative sections with overall financial position
- Multiple scattered action buttons
- No clear structure

### After
- **5 Module Overview Cards** (2 per row on desktop)
- Each card shows:
  - Module icon and name
  - Headline metric (e.g., "Total Protection: £500k")
  - 2-3 supporting metrics
  - Status indicator (on track / attention needed)
  - "View Details" button → module dashboard
- Narrative introduction explaining the goal-based approach
- Clear visual hierarchy

### Example Module Card
```
┌─────────────────────────────────────────┐
│ 📈 Investment                           │
│                                         │
│ Portfolio Value: £245,000               │
│                                         │
│ • YTD Return: +8.2%                     │
│ • Asset Allocation: Balanced            │
│ • Next Rebalance: 30 days               │
│                                         │
│ Status: ✅ On Track                     │
│                                         │
│ [View Investment Dashboard →]           │
└─────────────────────────────────────────┘
```

## Technical Changes

### Backend
- **New Structure:** `/api/modules/{module_name}/`
- **5 New Module Routers:** protection, savings, investment, retirement, iht
- **New Database Tables:**
  - `module_goals` - User goals per module
  - `module_metrics` - Module dashboard metrics cache
- **Database Changes:**
  - Add `module` field to `products` table
- **New Service:** `module_aggregator.py` - Aggregates data for main dashboard

### Frontend
- **New Component Structure:** `components/modules/{module_name}/`
- **New Page Structure:** `pages/modules/{module_name}/`
- **New Services:** `services/modules/{module_name}.ts`
- **22 Existing Pages** → **35 New Module Pages** (+ main dashboard)
- **Shared Components:** Module cards, metrics, headers, goal trackers

### Navigation
- Header and MobileNav completely refactored
- Breadcrumbs updated for module hierarchy
- Old routes redirect to new module routes

## Implementation Phases

### Phase 1: Planning & Setup (2-3 days)
✅ Create goalplan.md and goaltasks.md
- Database migrations
- Shared components
- **You are here**

### Phase 2: Backend Module Infrastructure (5-7 days)
- Create 5 module API routers
- Migrate existing logic to modules
- Create module aggregator service
- Update main app

### Phase 3: Frontend Module Dashboards (7-10 days)
- Build 5 module dashboards
- Build module sub-pages (products, analytics, etc.)
- Create module-specific components
- Migrate existing page logic

### Phase 4: Main Dashboard & Services (2-3 days)
- Refactor main dashboard to show module cards
- Create service layer for modules
- Update TypeScript interfaces

### Phase 5: Navigation & Routing (3-5 days)
- Update Header and MobileNav
- Update App.tsx routing
- Implement redirects from old routes
- Update breadcrumbs

### Phase 6: Deprecation & Cleanup (2-3 days)
- Mark old pages as deprecated
- Migrate product data
- Remove old components and pages
- Clean up dependencies

### Phase 7: Testing & Documentation (3-5 days)
- Write comprehensive tests (backend, frontend, E2E)
- Update API documentation
- Update user guides
- Create migration guide

**Total Timeline:** 24-36 days

## Migration Strategy

### Parallel Development
- New module structure built alongside existing features
- Old routes continue to work during migration
- Gradual feature migration module by module
- Deprecation notices on old pages
- Final cleanup after migration complete

### Data Migration
- Add `module` field to existing products
- Populate `module` based on `product_type`:
  - `protection` → `protection`
  - `savings` → `savings`
  - `investment` → `investment`
  - `pension` → `retirement`
- No data loss or downtime

### User Impact
- **During Migration:** Users see deprecation notices but all features work
- **After Migration:** Cleaner, more intuitive navigation
- **Migration Guide:** In-app tooltips and documentation

## Success Criteria

### User Experience
✅ Reduced cognitive load (5 clear modules vs. 10+ navigation items)
✅ Faster task completion (fewer clicks)
✅ Clearer financial goal alignment
✅ Improved feature discoverability

### Technical Quality
✅ Reduced code duplication
✅ Clear separation of concerns
✅ Improved test coverage (>90% backend, >80% frontend)
✅ Better maintainability

### Performance
✅ Main dashboard loads in <1s
✅ Module dashboards load in <800ms
✅ Parallel data fetching optimized

## What's NOT Included (Future Phase)

### AI Integration
The refactor deliberately excludes AI integration to focus on getting the structure right. AI features will be added in a future phase:
- Module-contextualized advice
- Onboarding assistance
- Goal recommendations
- Automated analysis
- Risk alerts

This allows us to:
1. Establish solid module boundaries
2. Get user flows correct
3. Validate the goal-based approach
4. Build AI features with full context

## Next Steps

1. **Review and Approve** goalplan.md and goaltasks.md
2. **Start Phase 2:** Backend module infrastructure
3. **Iterative Development:** Complete each module sequentially
4. **Regular Check-ins:** Review progress and adjust as needed
5. **User Testing:** Validate each module before moving to next

## Questions to Answer Before Starting

1. ✅ Do the 5 modules align with user mental models?
2. ✅ Is the module hierarchy clear and logical?
3. ✅ Are we comfortable with removing Products/Analytics navigation?
4. ✅ Is the timeline realistic for your team?
5. ✅ Are there any concerns about the migration approach?

## Key Documents

- **goalplan.md** - Comprehensive architectural plan (detailed)
- **goaltasks.md** - 78 implementation tasks with dependencies
- **REFACTOR_SUMMARY.md** - This document (quick overview)

---

**Ready to begin?** Start with Phase 2: Backend Module Infrastructure (Tasks 6-27)