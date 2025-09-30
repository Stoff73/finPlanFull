# Financial Planning Application - User Guide

**Complete Guide to Using Your Financial Planning Platform**

Version 1.0.0 | Last Updated: 2025-09-30

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Dashboard Overview](#dashboard-overview)
3. [IHT Calculator](#iht-calculator)
4. [Pension Planning](#pension-planning)
5. [Financial Statements](#financial-statements)
6. [Portfolio Management](#portfolio-management)
7. [Tax Optimization](#tax-optimization)
8. [Financial Projections](#financial-projections)
9. [AI Chat Assistant](#ai-chat-assistant)
10. [Export & Reports](#export--reports)
11. [Tips & Best Practices](#tips--best-practices)
12. [Troubleshooting](#troubleshooting)

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