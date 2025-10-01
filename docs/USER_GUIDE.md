# Financial Planning Application - User Guide

**Complete Guide to Using Your Financial Planning Platform**

Version 1.0.0 | Last Updated: 2025-09-30

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Dashboard Overview](#dashboard-overview)
3. **[Goal-Based Modules (NEW)](#goal-based-modules)**
   - [Protection Module](#protection-module)
   - [Savings Module](#savings-module)
   - [Investment Module](#investment-module)
   - [Retirement Module](#retirement-module)
   - [IHT Planning Module](#iht-planning-module)
4. [IHT Calculator](#iht-calculator)
5. [Pension Planning](#pension-planning)
6. [Financial Statements](#financial-statements)
7. [Portfolio Management](#portfolio-management)
8. [Tax Optimization](#tax-optimization)
9. [Financial Projections](#financial-projections)
10. [AI Chat Assistant](#ai-chat-assistant)
11. [Export & Reports](#export--reports)
12. [Tips & Best Practices](#tips--best-practices)
13. [Troubleshooting](#troubleshooting)

---

## Getting Started

### Creating Your Account

1. Navigate to http://localhost:3000
2. Click **"Sign Up"** or **"Register"**
3. Fill in your details:
   - Username (required)
   - Email address (required)
   - Password (minimum 8 characters)
   - Full name
   - Risk tolerance (Conservative, Moderate, Aggressive)
4. Click **"Create Account"**
5. You'll be automatically logged in

### Logging In

1. Go to http://localhost:3000
2. Enter your **username or email**
3. Enter your **password**
4. Click **"Login"**

**Demo Credentials** (for testing):
- Username: `demouser` or Email: `demo@example.com`
- Password: `demo123`

### First Steps After Login

1. **Update Your Profile**: Complete your personal information
2. **Add Financial Data**: Input your assets, liabilities, and income
3. **Set Goals**: Define your retirement and financial goals
4. **Explore Features**: Navigate through the dashboard

---

## Dashboard Overview

The dashboard is your financial command center, showing real-time insights and quick actions.

### Key Metrics

**Net Worth**
- Total assets minus total liabilities
- Updated in real-time as you add/edit data
- Click to view detailed breakdown

**Monthly Income**
- Average monthly income from all sources
- Includes salary, dividends, rental income
- Click to view income breakdown

**Monthly Expenses**
- Average monthly expenditure
- Categorized by type (housing, food, transport, etc.)
- Click to view expense breakdown

**Savings Rate**
- Percentage of income saved/invested
- Formula: (Income - Expenses) / Income × 100
- Target: 20%+ for healthy finances

### Quick Actions

- **Calculate IHT**: Open Inheritance Tax calculator
- **View Pensions**: Review pension schemes
- **Add Transaction**: Log income/expense
- **Financial Projection**: View long-term forecasts

### Widgets

**IHT Dashboard Widget**
- Real-time IHT liability
- Status indicators (Good/Warning/Alert)
- Gift warnings and key dates
- Quick access to IHT tools

**Pension Dashboard Widget**
- Total pension value across all schemes
- Annual Allowance usage
- Tax relief claimed this year
- Retirement readiness score

---

## Goal-Based Modules

**NEW in Version 2.0**: Your financial planning is now organized around five key life goals. Each module provides a focused dashboard, actionable insights, and easy management of your financial products.

### Why Goal-Based Modules?

Traditional financial planning can feel overwhelming. Goal-based modules simplify your financial life by organizing everything around what matters most:

- **Protection**: Safeguarding your family and income
- **Savings**: Building emergency funds and short-term goals
- **Investment**: Growing wealth for the long term
- **Retirement**: Planning for financial independence
- **IHT Planning**: Protecting your legacy and reducing tax

### Accessing Modules

From the main dashboard, you'll see five module cards showing your status in each area. Click any card to open that module's dedicated dashboard.

**Main Dashboard → Module Dashboard → Detailed Views**

---

## Protection Module

**Goal**: Ensure your family is financially protected if something happens to you.

### What is Protection?

Protection (or insurance) replaces lost income, covers debts, or provides a lump sum to your family. The Protection Module helps you:

- Track all your life insurance, critical illness, and income protection policies
- Calculate how much coverage you actually need
- Identify gaps in your protection
- Optimize premium costs

### Getting Started

1. **Navigate to Protection Module**
   - From main dashboard, click **"Protection"** card
   - Or use navigation: **Modules > Protection**

2. **Add Your First Policy**
   - Click **"Add Policy"**
   - Select policy type:
     - **Life Insurance**: Pays out on death
     - **Critical Illness**: Pays out on serious illness diagnosis
     - **Income Protection**: Replaces salary if unable to work
     - **Family Income Benefit**: Regular payments to family
   - Enter policy details:
     - Policy name (e.g., "Term Life Insurance")
     - Provider (e.g., "Example Life Co")
     - Coverage amount (e.g., £500,000)
     - Monthly premium (e.g., £50)
     - Start date and end date (if term policy)
     - Beneficiaries
   - Click **"Save Policy"**

3. **Review Your Coverage**
   - **Total Coverage**: Sum of all your policies
   - **Monthly Premiums**: What you're paying across all policies
   - **Coverage by Type**: Breakdown (life, critical illness, income)
   - **Coverage Adequacy**: Are you adequately covered?

### Understanding Your Protection Dashboard

**Key Metrics**:
- **Total Coverage**: £750,000 across 2 policies
- **Monthly Premiums**: £125/month total
- **Coverage Status**: Adequate / Attention Needed / Insufficient

**Status Indicators**:
- **Green (Adequate)**: You have good coverage for your situation
- **Amber (Attention Needed)**: Some gaps in coverage
- **Red (Insufficient)**: Significant protection gap

### Protection Needs Analysis

**What You Need**:
The app calculates recommended coverage based on:
1. **Income Replacement**: 10x annual income if you have dependents
2. **Debt Coverage**: Outstanding mortgage and loans
3. **Future Expenses**: Education costs, final expenses
4. **Emergency Fund**: 6 months of household expenses

**Running Needs Analysis**:
1. Click **"Needs Analysis"**
2. Enter your financial situation:
   - Annual income
   - Number of dependents
   - Outstanding debts (mortgage, loans)
   - Existing savings
   - Monthly household expenses
   - Spouse's income (if applicable)
3. Review recommendations:
   - **Coverage Gap**: How much more you need
   - **Estimated Cost**: Monthly premium estimate
   - **Recommendations**: Specific actions to take

**Example Output**:
```
Your Protection Gap: £306,000
Recommended Actions:
1. Add £300k term life insurance (est. £30/month)
2. Consider critical illness cover (£50/month for £150k)
3. Review income protection needs
```

### Managing Policies

**Edit a Policy**:
1. Click policy card
2. Click **"Edit"**
3. Update details (value, premium, dates)
4. Click **"Save Changes"**

**Archive a Policy** (when policy ends):
1. Click policy card
2. Click **"Archive"**
3. Confirm archival
4. Policy moves to "Archived" tab

**Premium Efficiency**:
- See **"Premium per £100k Coverage"**
- Compare your cost vs. typical rates
- Consider shopping around if premiums are high

### Tips & Best Practices

✅ **Review Annually**: Life changes (marriage, children, house purchase) = protection needs change

✅ **Life Events Trigger**: Review protection after:
- Getting married
- Having children
- Buying a house
- Changing jobs (may lose employer coverage)
- Paying off mortgage

✅ **Term vs Whole of Life**:
- **Term Insurance**: Cheaper, covers specific period (e.g., until mortgage paid off)
- **Whole of Life**: More expensive, covers entire life

✅ **Don't Forget Critical Illness**: 1 in 2 people will get cancer, heart disease, or stroke in their lifetime

---

## Savings Module

**Goal**: Build emergency funds and save for short-term goals.

### What is Savings?

The Savings Module helps you:
- Track all your cash savings accounts (savings accounts, ISAs, current accounts)
- Monitor your emergency fund status
- Set and track savings goals
- Maximize interest earnings

### Getting Started

1. **Navigate to Savings Module**
   - From main dashboard, click **"Savings"** card
   - Or use navigation: **Modules > Savings**

2. **Add Your First Savings Account**
   - Click **"Add Account"**
   - Select account type:
     - **Savings Account**: Standard savings
     - **ISA**: Cash ISA (tax-free)
     - **Current Account**: Checking account with balance
     - **Easy Access**: Instant access savings
     - **Fixed Term**: Locked for fixed period
   - Enter account details:
     - Account name (e.g., "Emergency Fund")
     - Provider (e.g., "Example Bank")
     - Current balance (e.g., £15,000)
     - Interest rate (e.g., 2.5%)
     - Account number (last 4 digits for reference)
   - Click **"Save Account"**

3. **Review Your Savings**
   - **Total Balance**: All your cash savings
   - **Emergency Fund**: Months of expenses covered
   - **Interest Analysis**: Average interest rate earned
   - **Accounts by Type**: ISA, savings, current accounts

### Understanding Your Savings Dashboard

**Key Metrics**:
- **Total Balance**: £25,000 across 2 accounts
- **Emergency Fund**: 8.3 months of expenses
- **Average Interest Rate**: 2.75%

**Emergency Fund Status**:
- **6+ months**: Excellent - you're well protected
- **3-6 months**: Adequate - aim for 6 months for optimal security
- **1-3 months**: Needs improvement - keep building
- **<1 month**: Insufficient - prioritize emergency fund

### Setting Savings Goals

**Create a Goal**:
1. Click **"Goals"** tab
2. Click **"Add Goal"**
3. Enter goal details:
   - Goal name (e.g., "Emergency Fund", "Holiday Fund", "House Deposit")
   - Target amount (e.g., £18,000 for 6-month emergency fund)
   - Target date (e.g., December 2025)
   - Monthly contribution (e.g., £500)
4. Click **"Save Goal"**

**Track Progress**:
- **Progress Bar**: Visual progress toward goal
- **Months Remaining**: Time until target date
- **On Track Indicator**: Green if on track, amber if behind

**Example**:
```
Emergency Fund Goal
Target: £18,000 by Dec 2025
Current: £15,000 (83% complete)
Monthly Contribution: £500
Status: On Track ✓
```

### Savings Analytics

**Balance Trends**:
- See how your savings have grown over time
- Month-by-month balance chart
- Identify savings rate patterns

**Interest Analysis**:
- Total interest earned this year
- Average interest rate across accounts
- Recommendations for higher-yield accounts

**Savings Rate**:
- Percentage of income you're saving
- Target: 20%+ for healthy finances
- See trends over time

### Tips & Best Practices

✅ **Emergency Fund First**: Prioritize 3-6 months of expenses before investing

✅ **High-Yield Accounts**: Shop around for best interest rates (currently 4-5% available)

✅ **Use ISAs Wisely**: £20,000 annual allowance (2024/25) - tax-free interest

✅ **Automate Savings**: Set up standing orders on payday

✅ **Separate Goals**: Use different accounts for different goals (emergency, holiday, house)

---

## Investment Module

**Goal**: Grow wealth for long-term financial goals.

### What is Investment?

The Investment Module helps you:
- Track stocks, bonds, ETFs, mutual funds, and other investments
- Monitor portfolio performance (gain/loss)
- Analyze asset allocation and diversification
- Rebalance your portfolio

### Getting Started

1. **Navigate to Investment Module**
   - From main dashboard, click **"Investment"** card
   - Or use navigation: **Modules > Investment**

2. **Add Your First Investment**
   - Click **"Add Investment"**
   - Select investment type:
     - **Stocks**: Individual company shares
     - **Bonds**: Government or corporate bonds
     - **ETF**: Exchange-Traded Fund
     - **Mutual Fund**: Actively managed fund
     - **REIT**: Real Estate Investment Trust
     - **Crypto**: Cryptocurrency
     - **Commodity**: Gold, silver, oil, etc.
     - **Cash**: Money market funds
   - Enter investment details:
     - Name (e.g., "FTSE 100 Index Fund")
     - Provider/broker (e.g., "Example Broker")
     - Current value (e.g., £15,000)
     - Total contributions (what you've put in: £12,000)
     - Number of units (e.g., 100)
     - Purchase price per unit (e.g., £120)
     - Annual dividend (optional, e.g., £300)
   - Click **"Save Investment"**

3. **Review Your Portfolio**
   - **Total Value**: Current market value
   - **Gain/Loss**: How much you're up or down
   - **Asset Allocation**: Breakdown by asset class
   - **Holdings**: Individual investments

### Understanding Your Investment Dashboard

**Key Metrics**:
- **Total Value**: £40,000
- **Total Contributions**: £32,000
- **Gain/Loss**: £8,000 (+25%)
- **Annual Dividend Income**: £1,200

**Asset Allocation**:
```
Equities (Stocks/ETFs): 75% (£30,000)
Bonds: 15% (£6,000)
Cash: 10% (£4,000)
```

**Status Indicators**:
- **Growing**: Portfolio value increasing
- **Stable**: Minimal changes
- **Attention Needed**: Significant losses or imbalance
- **Negative**: Portfolio underwater

### Investment Analytics

**Performance Metrics**:
- **Total Return**: £8,000 gain (+25%)
- **Annualized Return**: Average yearly return
- **Dividend Yield**: Income as % of portfolio value

**Risk Metrics**:
- **Portfolio Risk Score**: Low / Medium / High
- Based on asset mix and volatility
- **Diversification Score**: How spread out your investments are
- Target: 70%+ for good diversification

**Income Analysis**:
- **Annual Dividend Income**: £1,200
- **Monthly Income**: £100
- **Dividend Yield**: 3.0%

### Portfolio Rebalancing

**What is Rebalancing?**
Over time, your portfolio drifts from your target allocation. Rebalancing brings it back in line.

**Example**:
```
Your Target: 60% Stocks, 30% Bonds, 10% Cash
Current Actual: 75% Stocks, 15% Bonds, 10% Cash
Drift: Stocks +15% (overweight)
```

**Rebalancing Recommendations**:
1. **Sell £6,000 of stocks** (reduce from 75% to 60%)
2. **Buy £6,000 of bonds** (increase from 15% to 30%)
3. **Keep cash at 10%**

**When to Rebalance**:
- Once or twice per year
- When allocation drifts >5% from target
- After major market movements

**How to Rebalance**:
1. Click **"Rebalancing"** tab
2. Review current vs. target allocation
3. See specific recommendations
4. Execute trades with your broker
5. Update investment values in app

### Tips & Best Practices

✅ **Long-Term Focus**: Don't panic sell during downturns - stay invested

✅ **Diversify**: Don't put all eggs in one basket (spread across asset classes)

✅ **Low Fees**: Prefer index funds/ETFs over expensive active funds

✅ **ISA/SIPP Wrappers**: Use tax-efficient accounts (£20k ISA, £60k pension annual allowance)

✅ **Regular Contributions**: Pound-cost averaging reduces timing risk

---

## Retirement Module

**Goal**: Build a pension pot for financial independence in retirement.

### What is the Retirement Module?

The Retirement Module helps you:
- Track all your pension schemes (workplace, personal, SIPPs)
- Project retirement income
- Monitor annual allowance usage
- Optimize pension contributions for tax relief

### Getting Started

1. **Navigate to Retirement Module**
   - From main dashboard, click **"Retirement"** card
   - Or use navigation: **Modules > Retirement**

2. **Add Your First Pension**
   - Click **"Add Pension"**
   - Select pension type:
     - **Workplace Pension**: Auto-enrolment or company scheme
     - **Personal Pension**: Private pension
     - **SIPP**: Self-Invested Personal Pension
     - **Defined Benefit**: Final salary scheme (rare)
     - **State Pension**: Government pension (auto-calculated)
   - Enter pension details:
     - Pension name (e.g., "Workplace Pension")
     - Provider (e.g., "Example Pension Provider")
     - Current value (e.g., £150,000)
     - Annual contribution (your contributions: £12,000)
     - Employer contribution (£4,000 if workplace)
     - Tax relief (auto-calculated at 20-45%)
   - Click **"Save Pension"**

3. **Review Your Retirement Status**
   - **Total Pension Value**: All schemes combined
   - **Projected Income**: Estimated annual income at retirement
   - **Retirement Readiness**: On track / Behind / Ahead
   - **Years to Retirement**: Based on target retirement age

### Understanding Your Retirement Dashboard

**Key Metrics**:
- **Total Pension Value**: £225,000 across 2 pensions
- **Projected Annual Income**: £9,000/year (4% withdrawal rate)
- **Retirement Age**: 65 (configurable)
- **Years to Retirement**: 25 years
- **Retirement Readiness**: On Track

**Status Indicators**:
- **Ahead**: Exceeding retirement savings target
- **On Track**: Meeting retirement goals
- **Behind**: Need to increase contributions
- **At Risk**: Significantly behind target

### Retirement Projections

**4% Withdrawal Rule**:
The app assumes you'll withdraw 4% of your pension pot annually in retirement (sustainable rate).

**Example**:
```
Pension Pot at 65: £450,000
Annual Withdrawal (4%): £18,000
Plus State Pension: £11,500
Total Retirement Income: £29,500/year
```

**Running Projections**:
1. Click **"Projections"** tab
2. Select retirement age (60, 65, 67, 70)
3. See projected outcomes:
   - Pension pot size at retirement
   - Annual income available
   - Comparison to target income
4. Try different scenarios:
   - Increase contributions by £100/month
   - Retire 2 years later
   - Adjust investment returns

**Monte Carlo Simulation**:
See range of possible outcomes based on market volatility:
- **Best Case (90th percentile)**: £650,000
- **Expected (50th percentile)**: £450,000
- **Worst Case (10th percentile)**: £300,000
- **Success Rate**: 85% chance of meeting target

### Annual Allowance Tracking

**What is Annual Allowance?**
The maximum you can contribute to pensions each tax year with tax relief: £60,000 (2024/25).

**Tracking Usage**:
```
Annual Allowance: £60,000
Used This Year: £16,000 (26.7%)
  - Your contributions: £12,000
  - Employer contributions: £4,000
Remaining: £44,000
```

**Carry Forward**:
If you didn't use full allowance in previous 3 years, you can carry forward unused allowance.

**Tapered Allowance**:
High earners (£200k-£360k income) have reduced annual allowance. The app auto-calculates this.

### Tips & Best Practices

✅ **Start Early**: Compound growth is powerful - 25-year-olds need half the contributions of 40-year-olds for same outcome

✅ **Maximize Employer Match**: Free money - always contribute enough to get full employer match

✅ **Use Salary Sacrifice**: Save on National Insurance (ask your employer)

✅ **State Pension**: Check your forecast at gov.uk/check-state-pension - you need 35 qualifying years for full amount (£11,500/year in 2024/25)

✅ **Consolidate Old Pensions**: Track down old workplace pensions and consider consolidating to reduce fees

---

## IHT Planning Module

**Goal**: Protect your wealth and minimize inheritance tax for your beneficiaries.

### What is IHT Planning?

The IHT Planning Module helps you:
- Calculate potential inheritance tax liability
- Track gifts made in the last 7 years (for taper relief)
- Manage trusts and estate planning strategies
- Optimize estate to reduce IHT

### Getting Started

1. **Navigate to IHT Planning Module**
   - From main dashboard, click **"IHT Planning"** card
   - Or use navigation: **Modules > IHT Planning**

2. **Calculate Your IHT Liability**
   - Click **"Calculate IHT"**
   - Enter your estate:
     - **Assets**: Property £500k, Savings £100k, Investments £50k, Pensions £150k
     - **Liabilities**: Mortgage £200k, Other debts £0
   - Enter gifts in last 7 years (if any)
   - Select options:
     - Do you own main residence? Yes/No
     - Leaving to direct descendants? Yes/No
   - Click **"Calculate"**

3. **Review Your IHT Status**
   - **Estate Value**: £600,000 (assets - liabilities)
   - **IHT Liability**: £70,000 (if you died today)
   - **Nil-Rate Bands**: £325k standard + £175k residence
   - **Effective Rate**: 11.7% of estate

### Understanding Your IHT Dashboard

**Key Metrics**:
- **Estate Value**: £600,000
- **IHT Liability**: £70,000
- **Status**: Attention Needed (significant IHT)
- **Potential Savings**: £45,000 (with planning)

**Status Indicators**:
- **No Liability**: Estate below £325k (or £500k with residence band)
- **Low Risk**: Minimal IHT, easy to plan around
- **Attention Needed**: Moderate IHT, planning recommended
- **High Risk**: Significant IHT, urgent action needed

### Managing Gifts (7-Year Rule)

**What is the 7-Year Rule?**
Gifts made more than 7 years before death are IHT-free. Gifts within 7 years may be taxed with taper relief.

**Recording a Gift**:
1. Click **"Gifts"** tab
2. Click **"Add Gift"**
3. Enter gift details:
   - Recipient name (e.g., "Son")
   - Relationship (child, grandchild, spouse, friend)
   - Gift date (e.g., "15 Jan 2022")
   - Amount (e.g., £50,000)
   - Gift type (cash, property, shares)
   - Notes (e.g., "Wedding gift")
4. Click **"Save Gift"**

**Taper Relief**:
The app automatically calculates taper relief:
```
Gift made 5 years ago: £100,000
IHT due if you died today: 60% relief
Taxable amount: £40,000 (£100k - 60%)
IHT: £16,000 (40% of £40k)
```

**Taper Relief Schedule**:
- 0-3 years: 0% relief (full IHT)
- 3-4 years: 20% relief
- 4-5 years: 40% relief
- 5-6 years: 60% relief
- 6-7 years: 80% relief
- 7+ years: 100% relief (no IHT)

### Managing Trusts

**What are Trusts?**
Legal arrangements to hold assets for beneficiaries, with potential IHT advantages.

**Recording a Trust**:
1. Click **"Trusts"** tab
2. Click **"Add Trust"**
3. Enter trust details:
   - Trust name (e.g., "Family Trust")
   - Trust type (discretionary, bare, interest in possession)
   - Establishment date
   - Trust value
   - Beneficiaries
   - Trustees
4. Click **"Save Trust"**

**Trust Tax**:
- **10-Year Periodic Charge**: 6% of trust value every 10 years (discretionary trusts)
- **Exit Charge**: When assets leave trust
- App calculates and reminds you of upcoming charges

### IHT Reduction Strategies

**Recommendations Based on Your Situation**:

1. **Make Regular Gifts**
   - Use £3,000 annual exemption
   - Use £250 small gift exemption (per recipient)
   - Regular gifts from income (exempt if doesn't reduce standard of living)

2. **Use Residence Nil-Rate Band**
   - Worth £175,000 if leaving home to children/grandchildren
   - Tapers away for estates over £2m

3. **Spouse Exemption**
   - Gifts to spouse are IHT-free
   - Transfer unused nil-rate band to spouse

4. **Charitable Giving**
   - Gifts to charity are IHT-free
   - 10%+ to charity reduces IHT rate from 40% to 36%

5. **Business/Agricultural Relief**
   - Qualifying business assets: 50-100% relief
   - Agricultural property: 50-100% relief

6. **Life Insurance in Trust**
   - Life policy pays out IHT liability
   - Held in trust = outside estate

### Tips & Best Practices

✅ **Start Early**: The 7-year rule means early gifting saves more tax

✅ **Keep Records**: Document all gifts (date, amount, recipient) - the app does this for you

✅ **Annual Exemptions**: Use £3,000 annual gift exemption every year (can carry forward 1 year if unused)

✅ **Review Regularly**: Life changes (marriage, children, house value changes) affect IHT

✅ **Get Professional Advice**: Complex estates benefit from IFA or solicitor advice

---

## IHT Calculator

### Overview

The Inheritance Tax (IHT) Calculator helps you:
- Calculate potential IHT liability
- Plan gift strategies
- Optimize estate planning
- Ensure compliance with HMRC rules

### Basic IHT Calculation

1. Navigate to **Estate Planning > IHT Calculator**
2. Enter your estate details:
   - **Total Estate Value**: All assets minus liabilities
   - **Property Value**: Main residence value (for RNRB)
   - **Spouse NRB Used**: Transferred nil-rate band (0-100%)
3. Add **Gifts** made in last 7 years:
   - Click **"Add Gift"**
   - Enter amount, date, and recipient
   - Apply exemptions (annual, small, wedding)
4. Add **Charitable Donations**:
   - Donations reduce taxable estate
   - 10%+ qualifies for reduced 36% rate
5. Click **"Calculate IHT"**

### Understanding Your Results

**Nil-Rate Band (NRB)**
- Standard: £325,000 per person
- Transferable from deceased spouse (up to 100%)

**Residence Nil-Rate Band (RNRB)**
- Additional: £175,000 for main residence
- Only if property left to direct descendants
- Tapered for estates over £2 million (£1 lost per £2 over)
- Transferable from deceased spouse

**Taper Relief**
- Gifts made 3-7 years before death get relief:
  - 3-4 years: 20% relief
  - 4-5 years: 40% relief
  - 5-6 years: 60% relief
  - 6-7 years: 80% relief

**Tax Rates**
- Standard rate: 40% on amount over threshold
- Charitable rate: 36% if 10%+ left to charity

### Advanced IHT Features

**Gift History Manager**
1. Navigate to **Estate Planning > IHT Planning Suite**
2. Select **"Gift History"** tab
3. Features:
   - Track all gifts with dates and recipients
   - Monitor 7-year taper relief countdown
   - Apply exemptions automatically
   - View gift status (Exempt, PET, CLT)

**Trust Manager**
1. Select **"Trust Management"** tab
2. Create and manage trusts:
   - Discretionary trusts
   - Life interest trusts
   - Bare trusts
3. Calculate trust charges:
   - 10-year periodic charge (up to 6%)
   - Exit charges (pro-rated)

**Estate Planning Scenarios**
1. Select **"Planning Scenarios"** tab
2. Compare multiple strategies:
   - Do nothing (baseline)
   - Annual gifting program
   - Charitable legacy
   - Life insurance trust
   - Business property relief
3. View side-by-side comparison
4. See optimal strategy recommendation

**Valuation Tools**
1. Select **"Valuation Tools"** tab
2. Professional asset valuation:
   - Property valuation calculator
   - Share portfolio valuation
   - Business relief eligibility checker
   - Loss relief calculator

**Compliance Dashboard**
1. Navigate to **Estate Planning > IHT Compliance**
2. Features:
   - IHT400 form preparation
   - Excepted estate eligibility checker
   - Direct Payment Scheme calculator
   - Instalment payment planner
   - Deadline tracker

### IHT Best Practices

✅ **Do:**
- Use annual exemptions (£3,000 per year)
- Consider lifetime gifting strategies
- Use small gifts exemption (£250 per person)
- Plan 7 years ahead for major gifts
- Keep detailed gift records
- Review estate plan annually

❌ **Don't:**
- Gift assets you may need
- Forget Gift with Reservation rules
- Ignore taper relief timing
- Miss annual exemption opportunities
- Forget to claim RNRB
- Neglect to update valuations

---

## Pension Planning

### Overview

Comprehensive UK pension planning with:
- Annual Allowance tracking
- Tax relief calculations
- Multi-scheme management
- Retirement projections

### Annual Allowance Tracker

1. Navigate to **Pensions > Retirement Planning UK**
2. Select **"Annual Allowance"** tab
3. View:
   - Standard AA: £60,000 (2025/26)
   - Current usage across all schemes
   - Available carry-forward (3 years)
   - Warnings if approaching limits

**Tapered Annual Allowance**
- Applies if adjusted income > £260,000
- Reduces AA by £1 for every £2 over £260k
- Minimum tapered AA: £10,000 (at £360k+)
- Automatically calculated

**Money Purchase Annual Allowance (MPAA)**
- Triggered by flexible access to DC pension
- Reduces DC allowance to £10,000
- DB allowance remains at £60,000
- Blocks carry-forward for DC

### Tax Relief Calculator

1. Select **"Tax Relief"** tab
2. Enter your details:
   - Gross income
   - Pension contribution
   - Relief method (Relief at Source or Net Pay)
   - Scotland resident (if applicable)
3. View:
   - Basic rate relief (20% automatic)
   - Higher rate relief (additional 20%)
   - Additional rate relief (additional 25%)
   - Total tax saved

**Salary Sacrifice**
- Compare sacrifice vs personal contribution
- See NI savings (employee & employer)
- Calculate total compensation impact
- View recommendations

### Managing Multiple Schemes

1. Select **"Schemes"** tab
2. Click **"Add Scheme"**
3. Enter details:
   - Scheme name and provider
   - Type (DC, DB, Hybrid)
   - Current value
   - Contribution amounts
   - Employer match details
4. View consolidated annual statement

### Retirement Projections

1. Select **"Projections"** tab
2. Input:
   - Target retirement age
   - Expected investment returns
   - Contribution increases
3. View:
   - Projected pension pot at retirement
   - Annual income available
   - Replacement ratio
   - Monte Carlo simulation ranges

### Contribution Optimizer

1. Select **"Optimization"** tab
2. System analyzes:
   - Current contribution levels
   - Employer match efficiency
   - AA utilization
   - Tax relief optimization
3. Receive recommendations:
   - Optimal contribution amount
   - Best relief method
   - Employer match maximization
   - AA threshold management

---

## Financial Statements

### Balance Sheet

**What It Shows**: Snapshot of assets and liabilities at a point in time.

**Creating a Balance Sheet**:
1. Navigate to **Financial > Balance Sheet**
2. Click **"Add Balance Sheet"**
3. Enter date (e.g., end of month/quarter)
4. Add **Assets**:
   - Current assets (cash, savings)
   - Investments (ISAs, GIAs, pensions)
   - Property (main residence, buy-to-lets)
   - Other assets (vehicles, valuables)
5. Add **Liabilities**:
   - Current liabilities (credit cards, loans)
   - Mortgage
   - Other long-term debt
6. System calculates **Net Worth** automatically
7. Click **"Save"**

**Viewing History**:
- See trend of net worth over time
- Compare month-to-month changes
- Export to Excel/PDF

### Profit & Loss Statement

**What It Shows**: Income and expenses over a period (monthly/quarterly/yearly).

**Creating P&L**:
1. Navigate to **Financial > Profit & Loss**
2. Click **"Add Statement"**
3. Select period (start and end dates)
4. Add **Income**:
   - Salary/wages
   - Dividends
   - Rental income
   - Other income sources
5. Add **Expenses** by category:
   - Housing (mortgage/rent, utilities)
   - Food and groceries
   - Transportation
   - Healthcare
   - Entertainment
   - Other expenses
6. System calculates **Net Income**
7. Click **"Save"**

**Key Metrics**:
- **Gross Income**: Total income before expenses
- **Net Income**: Income after all expenses
- **Savings Rate**: Percentage saved

### Cash Flow Statement

**What It Shows**: Movement of cash in and out over a period.

**Creating Cash Flow**:
1. Navigate to **Financial > Cash Flow**
2. Click **"Add Statement"**
3. Enter period dates
4. Add **Operating Cash Flow**:
   - Income received (actual cash in)
   - Expenses paid (actual cash out)
5. Add **Investing Cash Flow**:
   - Asset purchases
   - Investment contributions
   - Asset sales
6. Add **Financing Cash Flow**:
   - Loan proceeds
   - Debt repayments
   - Dividends received
7. System calculates **Net Cash Flow**
8. Click **"Save"**

### Financial Summary

View comprehensive overview:
1. Navigate to **Financial > Summary**
2. See combined view of:
   - Latest balance sheet
   - Latest P&L
   - Latest cash flow
3. Key financial ratios:
   - Debt-to-income ratio
   - Emergency fund months
   - Investment allocation %
   - Liquidity ratio

---

## Portfolio Management

### Products Overview

**Viewing All Products**:
1. Navigate to **Products** (top-level menu)
2. See all financial products:
   - Pensions
   - Investments (ISAs, GIAs, SEIS, EIS, etc.)
3. Filter by product type
4. Sort by value, provider, or date

**Note**: Protection products have their own dedicated section in the main navigation.

### Adding Pensions

1. Navigate to **Products > Pensions**
2. Click **"Add Pension"**
3. Enter details:
   - Pension name
   - Provider (e.g., Aviva, Vanguard)
   - Scheme type (DC, DB, Hybrid)
   - Current value
   - Annual contributions
   - Employer match percentage
   - Relief method
4. Click **"Save"**

### Adding Investments

1. Navigate to **Products > Investments**
2. Click **"Add Investment"**
3. Enter details:
   - Investment name
   - Provider
   - Type (Stocks & Shares ISA, GIA, SEIS, EIS, etc.)
   - Current value
   - Purchase date
   - Annual return (historical or expected)
4. Click **"Save"**

**Investment Types**:
- **Stocks & Shares ISA**: Tax-free growth and withdrawals
- **General Investment Account (GIA)**: Taxable investment
- **SEIS**: Seed Enterprise Investment Scheme (50% income tax relief)
- **EIS**: Enterprise Investment Scheme (30% income tax relief)
- **VCT**: Venture Capital Trust (tax reliefs)
- **Bonds**: Corporate or government bonds
- **Shares**: Individual company shares
- **Funds**: Mutual funds or unit trusts
- **ETFs**: Exchange-traded funds
- **Crypto**: Cryptocurrency holdings

**Note**: SIPPs (Self-Invested Personal Pensions) are pension products and should be added under **Products > Pensions** or **UK Pension** section.

### Adding Protection

1. Navigate to **Protection** (top-level menu)
2. Click **"Add Protection"**
3. Enter details:
   - Policy name
   - Provider
   - Type (Life, Critical Illness, Income Protection)
   - Coverage amount
   - Monthly/annual premium
   - Policy start and end dates
4. Click **"Save"**

### Portfolio Analytics

1. Navigate to **Portfolio Analytics** (top-level menu under "Analytics")
2. View comprehensive analysis:

**Asset Allocation**
- Pie chart showing distribution
- Compare to target allocation
- Identify overweight/underweight assets

**Performance Tracking**
- Historical returns by asset class
- Year-to-date performance
- Total return calculation

**Risk Analysis**
- Portfolio risk score (1-10)
- Diversification metrics
- Volatility measures
- Maximum drawdown

**Rebalancing Recommendations**
- See drift from target allocation
- Get specific buy/sell recommendations
- View tax-efficient rebalancing strategies

---

## Tax Optimization

### Tax Position Analysis

1. Navigate to **Tax Optimisation** (top-level menu)
2. Select **"Overview"** tab
3. Enter all income sources:
   - Employment income
   - Dividend income
   - Rental income
   - Savings interest
   - Other income
4. Enter deductions:
   - Pension contributions
   - Gift Aid donations
   - Trading allowances
5. View tax breakdown:
   - Income Tax
   - National Insurance
   - Dividend Tax
   - Total tax liability
   - Effective tax rate
   - Marginal tax rate

### Pension Optimization

1. Select **"Pension Optimization"** tab
2. See current pension contributions
3. View recommendations:
   - Optimal contribution amount
   - Annual Allowance utilization
   - Carry-forward usage
   - Tax relief maximization
4. Compare scenarios:
   - Current contributions
   - Recommended contributions
   - Maximum AA contributions

**Key Benefits**:
- Reduce taxable income
- Claim 20/40/45% tax relief
- Utilize unused AA from previous 3 years
- Avoid AA charges

### Salary/Dividend Split

**For Company Directors**:
1. Select **"Salary/Dividend"** tab
2. Enter company profits available
3. Compare 3 scenarios:
   - All salary
   - NI threshold salary + dividends
   - Basic rate threshold salary + dividends
4. See tax breakdown for each:
   - Income Tax
   - National Insurance
   - Dividend Tax
   - Corporation Tax
   - Total tax
   - Net take-home

**Optimization Factors**:
- State pension considerations
- Student loan repayments
- Personal Allowance protection
- Dividend allowance (£500)
- NI threshold (£12,570)

### ISA vs Taxable Investment

1. Select **"ISA vs Taxable"** tab
2. Enter investment details:
   - Initial investment
   - Annual contribution
   - Investment period (years)
   - Expected return
3. Compare outcomes:
   - ISA: Tax-free growth
   - GIA: CGT and dividend tax applied
4. See total tax saved over period

**ISA Allowances**:
- £20,000 per tax year (2024/25)
- Use-it-or-lose-it annual allowance
- Tax-free growth forever
- No CGT or dividend tax

### Comprehensive Tax Report

1. Select **"Full Report"** tab
2. View prioritized recommendations:
   - **High Priority**: Immediate actions (e.g., use ISA allowance)
   - **Medium Priority**: Planning actions (e.g., pension review)
   - **Low Priority**: Long-term strategies
3. See estimated savings for each
4. Export report as PDF

---

## Financial Projections

### Multi-Year Projections

1. Navigate to **Estate Planning > Financial Projections**
2. Select **"Input"** tab
3. Enter current situation:
   - Current age
   - Retirement age
   - Current assets
   - Current liabilities
   - Annual income
   - Annual expenses
4. Enter assumptions:
   - Income growth rate
   - Expense growth rate
   - Investment return
   - Inflation rate
5. Add planned changes:
   - Major expenses (home purchase, education)
   - Income changes (promotions, bonuses)
6. Click **"Calculate Projection"**

### Viewing Projections

1. Select **"Projections"** tab
2. View 30-year forecast:
   - Net worth trajectory
   - Income vs expenses
   - Investment growth
   - Debt reduction
3. Interactive chart:
   - Hover for year details
   - Toggle data series on/off
   - Zoom in on specific periods

### Scenario Comparison

1. Select **"Scenarios"** tab
2. Compare three scenarios:
   - **Conservative**: Lower returns, higher expenses
   - **Moderate**: Expected outcomes
   - **Optimistic**: Higher returns, controlled expenses
3. See range of outcomes at retirement
4. Understand best/worst case scenarios

**Key Insights**:
- Retirement net worth range
- Annual retirement income
- Probability of meeting goals
- Risk factors to monitor

### Retirement Readiness

1. Select **"Retirement"** tab
2. View readiness score (0-100):
   - **80-100**: On track
   - **60-79**: Some concern
   - **Below 60**: Action needed
3. See income gap:
   - Projected retirement income
   - Target income (70% of current)
   - Shortfall/surplus
4. Get recommendations:
   - Increase pension contributions
   - Adjust retirement age
   - Review investment allocation
   - Reduce planned retirement expenses

---

## AI Chat Assistant

### Starting a Conversation

1. Navigate to **Chat** (icon in header)
2. Type your question in the message box
3. Press **Enter** or click **"Send"**

### What the AI Can Help With

**Financial Queries**:
- "What is my net worth?"
- "How much are my pensions worth?"
- "What's my savings rate this year?"

**IHT Planning**:
- "Calculate my inheritance tax"
- "How can I reduce IHT liability?"
- "Explain taper relief"

**Pension Advice**:
- "How much should I contribute to my pension?"
- "What's my Annual Allowance usage?"
- "Will I have enough for retirement?"

**Tax Planning**:
- "How can I reduce my tax bill?"
- "Should I use salary or dividends?"
- "What's my marginal tax rate?"

**General Guidance**:
- "Explain the ISA allowance"
- "What is the nil-rate band?"
- "How does pension tax relief work?"

### Understanding AI Responses

**Intent Classification**:
AI identifies what you're asking about:
- Query (information request)
- Calculation (compute something)
- Planning (strategic advice)
- Compliance (rules and regulations)

**Extracted Data**:
AI pulls relevant information from your profile to answer accurately.

**Suggestions**:
After answering, AI suggests related actions or follow-up questions.

### Chat Best Practices

✅ **Do**:
- Ask specific questions
- Provide context when needed
- Follow up for clarification
- Use suggestions for deeper insights

❌ **Don't**:
- Ask for regulated financial advice (AI provides information only)
- Rely solely on AI for major financial decisions
- Share sensitive information unnecessarily

---

## Export & Reports

### Exporting IHT Data

**PDF Export**:
1. Navigate to IHT Calculator
2. Complete calculation
3. Click **"Export PDF"**
4. Save comprehensive IHT report with:
   - Full calculation breakdown
   - Gift history with taper relief
   - Estate valuation
   - Tax planning recommendations

**Excel Export**:
1. Click **"Export Excel"**
2. Receive detailed spreadsheet with:
   - Asset listing
   - Gift schedule
   - Tax calculations
   - Charts and graphs
   - Editable assumptions

### Exporting Financial Statements

**CSV Export**:
1. Navigate to Financial Statements
2. Select statement type (Balance Sheet, P&L, Cash Flow)
3. Choose date range
4. Click **"Export CSV"**
5. Open in Excel/Google Sheets

**PDF Report**:
1. Click **"Export PDF"**
2. Select report type:
   - Single statement
   - Combined financial report
   - Year-end summary
3. Customize report options
4. Download PDF

### Importing Data

**CSV Import**:
1. Prepare CSV file with required columns
2. Navigate to relevant section
3. Click **"Import CSV"**
4. Select file
5. Map columns (if prompted)
6. Review import preview
7. Click **"Confirm Import"**

**Supported Import Types**:
- Bank transactions
- Gift history
- Asset valuations
- Investment transactions
- Pension contributions

---

## Tips & Best Practices

### Data Management

**Regular Updates**:
- Update balance sheet monthly
- Review investment values quarterly
- Record all significant gifts immediately
- Update pension values annually

**Accuracy**:
- Use actual figures, not estimates
- Keep supporting documentation
- Record transactions on the date they occur
- Include all income sources

**Organization**:
- Use consistent naming conventions
- Categorize transactions properly
- Tag related items
- Add notes for context

### Financial Planning

**IHT Planning**:
- Start gifting early (7-year rule)
- Use annual exemptions every year
- Document all gifts properly
- Review estate plan annually
- Consider life insurance for IHT liability

**Pension Optimization**:
- Maximize employer match
- Use full Annual Allowance
- Claim carry-forward if available
- Review tax relief methods
- Consolidate old pensions (carefully)

**Tax Efficiency**:
- Use ISA allowance fully each year
- Optimize salary/dividend split (directors)
- Claim all available reliefs
- Time income/gains strategically
- Keep good records for HMRC

**Portfolio Management**:
- Diversify across asset classes
- Rebalance annually (or when 5%+ drift)
- Keep some emergency cash (6 months expenses)
- Review investment performance quarterly
- Use tax-efficient accounts first (ISA, pension)

### Security Best Practices

**Account Security**:
- Use strong, unique password
- Change password every 6 months
- Log out after each session
- Don't share login credentials
- Enable browser password manager

**Data Privacy**:
- Review privacy settings
- Only share necessary data
- Download regular backups
- Delete old/unnecessary data
- Be cautious with public Wi-Fi

---

## Troubleshooting

### Login Issues

**Can't log in**:
1. Verify username/email is correct
2. Check password (case-sensitive)
3. Clear browser cache and cookies
4. Try different browser
5. Contact support if persistent

**Forgot password**:
1. Click "Forgot Password" (if available)
2. Enter email address
3. Check email for reset link
4. Create new password
5. Contact support if no email received

### Calculation Issues

**IHT calculation seems wrong**:
1. Verify all asset values are current
2. Check gift dates are accurate
3. Ensure exemptions applied correctly
4. Review RNRB eligibility (property to descendants)
5. Check spouse NRB transfer percentage

**Pension AA showing incorrect**:
1. Verify all schemes added
2. Check contribution dates (correct tax year)
3. Confirm employer contributions included
4. Review MPAA status if triggered
5. Check carry-forward years available

### Display Issues

**Page not loading**:
1. Refresh browser (F5 or Cmd+R)
2. Clear browser cache
3. Check internet connection
4. Try incognito/private mode
5. Try different browser

**Charts not showing**:
1. Ensure JavaScript is enabled
2. Update to latest browser version
3. Disable ad blockers temporarily
4. Check browser console for errors

### Data Issues

**Missing transactions**:
1. Check date filters applied
2. Verify correct account selected
3. Check transaction status
4. Look in correct category
5. Check if accidentally deleted

**Incorrect balances**:
1. Verify all transactions recorded
2. Check for duplicate entries
3. Ensure dates are correct
4. Recalculate balances (refresh page)
5. Review transaction categories

### Export Issues

**Export not downloading**:
1. Check browser download settings
2. Disable pop-up blockers
3. Try different file format
4. Check available disk space
5. Try different browser

**Import failing**:
1. Verify CSV format is correct
2. Check column headers match template
3. Ensure dates in correct format (YYYY-MM-DD)
4. Check for special characters
5. Reduce file size if very large

### Getting Help

**In-App Support**:
- Check FAQ section
- Use AI Chat for guidance
- Review documentation

**External Support**:
- Email: support@example.com
- GitHub Issues: https://github.com/yourrepo/issues
- Phone: (if available)

**Before Contacting Support**:
1. Note exact error message
2. Document steps to reproduce
3. Screenshot the issue
4. Check system status page
5. Try basic troubleshooting steps

---

## Keyboard Shortcuts

**Navigation**:
- `Ctrl/Cmd + K`: Open search
- `Esc`: Close modals/dialogs
- `Tab`: Navigate between fields
- `Enter`: Submit forms

**Editing**:
- `Ctrl/Cmd + S`: Save current form
- `Ctrl/Cmd + Z`: Undo
- `Ctrl/Cmd + Y`: Redo

**General**:
- `?`: Show keyboard shortcuts help
- `Ctrl/Cmd + /`: Open AI chat

---

## Glossary

**Annual Allowance (AA)**: Maximum pension contribution with tax relief (£60,000 for 2025/26)

**Carry-Forward**: Use unused AA from previous 3 tax years

**CGT**: Capital Gains Tax - Tax on profits from selling assets

**Discretionary Trust**: Trust where trustees decide how to distribute

**Estate**: All assets and liabilities at death

**ISA**: Individual Savings Account - Tax-free investment wrapper

**MPAA**: Money Purchase Annual Allowance - £10,000 DC limit after flexible access

**NRB**: Nil-Rate Band - £325,000 IHT-free threshold

**PET**: Potentially Exempt Transfer - Gift that becomes exempt after 7 years

**RNRB**: Residence Nil-Rate Band - Additional £175,000 for main residence

**SIPP**: Self-Invested Personal Pension

**Taper Relief**: IHT reduction for gifts made 3-7 years before death

**TNRB/TRNRB**: Transferable NRB/RNRB from deceased spouse

---

## Additional Resources

**HMRC Resources**:
- IHT guidance: https://www.gov.uk/inheritance-tax
- Pension tax: https://www.gov.uk/tax-on-your-private-pension
- Tax calculators: https://www.gov.uk/government/collections/tax-calculators

**External Tools**:
- MoneyHelper: https://www.moneyhelper.org.uk
- Pension Tracing: https://www.gov.uk/find-pension-contact-details
- ISA comparison: MoneySavingExpert.com

**Professional Advice**:
Consider consulting:
- Independent Financial Adviser (IFA)
- Chartered Financial Planner
- Tax Accountant
- Solicitor (for estate planning)

---

## Feedback & Feature Requests

We value your feedback! Help us improve:

**Submit Feedback**:
- Email: feedback@example.com
- GitHub: https://github.com/yourrepo/issues
- In-app feedback form

**Feature Requests**:
- Describe the feature clearly
- Explain the use case
- Suggest how it should work
- Vote on existing requests

**Bug Reports**:
- Describe what happened
- What you expected to happen
- Steps to reproduce
- Screenshots if applicable
- Browser and OS version

---

*Thank you for using the Financial Planning Application!*

*Last Updated: 2025-09-30*
*Version: 1.0.0*