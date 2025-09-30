# UK Inheritance Tax Calculator - User Guide

## Table of Contents
1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Core Features](#core-features)
4. [Step-by-Step Guides](#step-by-step-guides)
5. [Understanding IHT Calculations](#understanding-iht-calculations)
6. [Advanced Features](#advanced-features)
7. [Compliance and Reporting](#compliance-and-reporting)
8. [Frequently Asked Questions](#frequently-asked-questions)

---

## Introduction

### What is the IHT Calculator?

The UK Inheritance Tax (IHT) Calculator is a comprehensive estate planning tool that helps you:
- Calculate your potential IHT liability accurately
- Plan gifts and transfers tax-efficiently
- Manage trusts and their associated charges
- Track exemptions and reliefs
- Prepare for HMRC compliance requirements

### Who Should Use This Tool?

This calculator is designed for:
- Financial advisers working with clients on estate planning
- Individuals planning their estate distribution
- Executors preparing IHT calculations
- Anyone needing to understand UK inheritance tax implications

### Current Tax Rules (2024/25)

- **Nil-Rate Band (NRB)**: £325,000
- **Residence Nil-Rate Band (RNRB)**: £175,000
- **Standard IHT Rate**: 40%
- **Reduced Charity Rate**: 36% (if 10%+ estate goes to charity)
- **7-Year Rule**: Gifts become IHT-free after 7 years
- **Taper Relief**: Available on PETs given 3-7 years before death

---

## Getting Started

### Accessing the IHT Calculator

1. Log in to your account at http://localhost:3000/login
2. Navigate to **IHT Planning** from the main menu
3. Choose your starting point:
   - **IHT Calculator** - Basic calculations
   - **IHT Planning Suite** - Complete toolset (recommended)
   - **IHT Compliance** - HMRC forms and deadlines

### Test Accounts

For demonstration purposes:
- **Username**: demouser
- **Email**: demo@example.com
- **Password**: demo123

### Navigation Overview

The IHT Planning Suite contains 6 main tabs:

1. **Gift Timeline** - Visualize your 7-year gift history
2. **Estate Scenarios** - Compare different planning strategies
3. **Gift Management** - Add, edit, and track all gifts
4. **Trust Manager** - Create and manage trust structures
5. **Exemptions** - Optimize use of annual exemptions
6. **Valuation Tools** - Professional asset valuation assistance

---

## Core Features

### 1. Estate Calculation

**What it does**: Calculates your total IHT liability based on your current estate.

**How to use**:
1. Navigate to IHT Calculator
2. Enter your assets by category:
   - Property (main residence and other properties)
   - Business assets
   - Investments and savings
   - Personal possessions
3. Add liabilities (mortgages, loans, debts)
4. Click **Calculate IHT**

**Example**:
```
Total Estate: £2,000,000
Main Residence: £500,000
Liabilities: £200,000
Net Estate: £1,800,000

Available Reliefs:
- NRB: £325,000
- RNRB: £175,000 (main residence to direct descendants)
- Total Tax-Free: £500,000

Taxable Estate: £1,300,000
IHT Due: £520,000 (40% of £1,300,000)
```

### 2. Gift Timeline Visualization

**What it does**: Shows all gifts on an interactive timeline with taper relief percentages.

**How to use**:
1. Open **Gift Timeline** tab
2. View your gifts on the 7-year timeline
3. Check gift status:
   - 🟢 **Green** (0-3 years): Full IHT applies
   - 🟡 **Yellow** (3-7 years): Taper relief available
   - ✅ **Exempt** (7+ years): No IHT

**Taper Relief Scale**:
| Years Since Gift | Tax Reduction |
|------------------|---------------|
| 0-3 years        | 0%            |
| 3-4 years        | 20%           |
| 4-5 years        | 40%           |
| 5-6 years        | 60%           |
| 6-7 years        | 80%           |
| 7+ years         | 100% (exempt) |

**Example**: A £100,000 gift made 5 years ago would have 60% taper relief, reducing the IHT charge from £40,000 to £16,000.

### 3. Gift History Manager

**What it does**: Full CRUD (Create, Read, Update, Delete) operations for gift tracking.

**How to use**:
1. Open **Gift Management** tab
2. Click **Add Gift** button
3. Enter gift details:
   - Recipient name and relationship
   - Gift amount
   - Date given
   - Gift type (PET/CLT/Exempt)
4. Apply exemptions if eligible:
   - Annual exemption (£3,000/year)
   - Small gifts (£250 per recipient)
   - Wedding gifts (£1,000-£5,000)
   - Normal expenditure out of income

**Gift Types Explained**:

- **PET (Potentially Exempt Transfer)**: Gifts to individuals that become exempt after 7 years
- **CLT (Chargeable Lifetime Transfer)**: Gifts to trusts that are immediately chargeable
- **Exempt**: Gifts covered by exemptions (annual, small, wedding, etc.)

### 4. Estate Planning Scenarios

**What it does**: Compares multiple estate planning strategies side-by-side.

**How to use**:
1. Open **Estate Scenarios** tab
2. Enter your current estate details
3. Create scenarios:
   - **Baseline**: Do nothing
   - **Gift Strategy**: Regular gifting program
   - **Trust Strategy**: Transfer assets to trusts
   - **Charitable Strategy**: Leave 10%+ to charity
   - **Combined Strategy**: Multiple approaches

**Example Scenario**:
```
Current Estate: £2,500,000
IHT Liability (Do Nothing): £870,000

Strategy 1: Gift £200,000 over 4 years
- Uses annual exemptions
- Potential savings: £80,000

Strategy 2: £250,000 to charity (10%)
- Qualifies for 36% reduced rate
- Savings: £100,000

Strategy 3: Combined approach
- Total savings: £160,000
```

### 5. Trust Manager

**What it does**: Creates and manages trust structures with automatic charge calculations.

**How to use**:
1. Open **Trust Manager** tab
2. Click **Create Trust**
3. Enter trust details:
   - Trust name and type
   - Initial value
   - Date created
   - Beneficiaries

**Trust Types**:

- **Discretionary Trust**: Trustees decide distributions (relevant property regime)
- **Life Interest Trust (IPDI)**: Income to life tenant, capital to remaindermen
- **Bereaved Minor Trust**: For children under 18
- **Age 18-25 Trust**: Structured for young adults

**Trust Charges**:

- **Entry Charge**: Up to 20% of amount over NRB
- **10-Year Periodic Charge**: Up to 6% of trust value
- **Exit Charge**: Proportional charge when assets leave trust

**Example**:
```
Discretionary Trust created with £500,000
Entry charge (if NRB already used): £35,000

After 10 years, trust worth £700,000:
10-year charge: £42,000 (6% of £700,000)

Exit distribution of £100,000 at year 6:
Exit charge: £2,400
```

### 6. Exemption Tracker

**What it does**: Tracks and optimizes use of all available IHT exemptions.

**How to use**:
1. Open **Exemptions** tab
2. Review available exemptions:
   - Annual exemption (£3,000 + £3,000 carried forward)
   - Small gifts (£250 per person, unlimited recipients)
   - Wedding gifts (varies by relationship)
   - Normal expenditure out of income
3. Apply exemptions to gifts strategically

**Exemption Rules**:

| Exemption Type | Amount | Rules |
|----------------|--------|-------|
| Annual | £3,000/year | Can carry forward 1 year |
| Small gifts | £250/person | Unlimited recipients, not with annual |
| Wedding (child) | £5,000 | Must be in contemplation of marriage |
| Wedding (grandchild) | £2,500 | Same as above |
| Wedding (other) | £1,000 | Same as above |
| Normal expenditure | Unlimited | Must be regular, from income, leave sufficient income |

### 7. Valuation Tools

**What it does**: Provides professional guidance on valuing different asset types.

**How to use**:
1. Open **Valuation Tools** tab
2. Select asset type:
   - Property
   - Quoted shares
   - Unquoted shares
   - Business assets
   - Chattels
3. Use calculators for:
   - Joint ownership adjustments
   - Mortgage deductions
   - Share portfolio valuation (quarter-up rule)
   - Loss relief calculations

**Property Valuation**:
- Use market value at date of death
- Deduct outstanding mortgage
- Apply joint ownership percentage
- Consider VOA guidance

**Share Valuation (Quarter-Up Rule)**:
```
Lower price: £2.50
Higher price: £2.70
Quarter-up value: £2.50 + (0.25 × £0.20) = £2.55
```

**Loss Relief**:
- **Property**: Available if sold within 4 years at a loss
- **Shares**: Available if sold within 12 months at a loss

---

## Step-by-Step Guides

### Guide 1: Calculating Your Basic IHT Liability

**Time required**: 10 minutes

**Steps**:

1. **Gather information**:
   - List all assets (property, savings, investments, pensions)
   - List all liabilities (mortgages, loans, debts)
   - Note your marital status
   - Confirm if you have direct descendants

2. **Navigate to IHT Calculator**:
   - Click **IHT Planning** > **IHT Calculator**

3. **Enter personal details**:
   - Marital status: Select from dropdown
   - Direct descendants: Yes/No

4. **Add assets**:
   - Click **Add Asset** for each holding
   - Select asset type (property, business, investment, personal)
   - Enter value
   - Mark main residence if applicable

5. **Add liabilities**:
   - Enter mortgage balances
   - Add other debts

6. **Calculate**:
   - Click **Calculate IHT**
   - Review results:
     - Net estate value
     - Available reliefs (NRB, RNRB)
     - Taxable estate
     - IHT liability

7. **Review breakdown**:
   - Check the tax waterfall chart
   - Understand which reliefs apply
   - Note any warnings

### Guide 2: Setting Up a Gifting Strategy

**Time required**: 20 minutes

**Steps**:

1. **Assess annual exemptions**:
   - Navigate to **Exemptions** tab
   - Check available exemptions:
     - Current year: £3,000
     - Previous year carried forward: £3,000
     - Total available: £6,000

2. **Plan gifts**:
   - Open **Estate Scenarios** tab
   - Enter current estate value
   - Create "Gift Strategy" scenario
   - Plan annual gifts up to exemption limits

3. **Record gifts**:
   - Go to **Gift Management** tab
   - Click **Add Gift**
   - Enter details:
     - Recipient: [Name]
     - Relationship: [e.g., "Child"]
     - Amount: £6,000 (using both exemptions)
     - Date: [Today's date]
     - Type: PET (will become exempt if you survive 7 years)

4. **Apply exemptions**:
   - Select "Annual Exemption" checkbox
   - Gift amount reduces to £0 taxable

5. **Review timeline**:
   - Open **Gift Timeline** tab
   - See your gift positioned on the 7-year timeline
   - Note when it will become fully exempt

6. **Set reminders**:
   - Create calendar reminders for:
     - Annual exemption renewal (each tax year)
     - 7-year anniversary of major gifts

### Guide 3: Managing Trust Charges

**Time required**: 15 minutes

**Steps**:

1. **Create or select trust**:
   - Navigate to **Trust Manager** tab
   - Click **Create Trust** or select existing trust

2. **Enter trust details**:
   - Trust name: [e.g., "Family Discretionary Trust"]
   - Type: Discretionary Trust
   - Initial value: £500,000
   - Date created: [Date]
   - Beneficiaries: [List names]

3. **Calculate entry charge**:
   - System automatically calculates if NRB is exceeded
   - Entry charge = (Amount - £325,000) × 20%
   - Example: £500,000 trust = £35,000 charge

4. **View 10-year charge projection**:
   - System shows timeline of 10-year anniversaries
   - Projects charges based on assumed growth
   - 10-year charge = Up to 6% of trust value

5. **Plan exit distributions**:
   - Click **Calculate Exit Charge**
   - Enter distribution amount
   - Enter distribution date
   - System calculates proportional charge

6. **Review charge history**:
   - View all past charges
   - Track cumulative IHT paid
   - Export for tax records

### Guide 4: Preparing for HMRC Compliance

**Time required**: 30 minutes

**Steps**:

1. **Navigate to IHT Compliance**:
   - Click **IHT Planning** > **IHT Compliance**

2. **Check excepted estate eligibility**:
   - Click **Excepted Estate Checker**
   - Answer questions:
     - Is gross estate under £3M?
     - Any foreign assets?
     - Any trusts?
   - System determines if you need:
     - IHT205 (simple estates)
     - IHT207 (slightly complex estates)
     - IHT400 (full account)

3. **Prepare IHT400 data** (if required):
   - Click **IHT400 Preparation**
   - System pre-populates fields:
     - Schedule 1: Asset list
     - Schedule 2: Gifts
     - Schedule 3: Trusts
     - Schedule 4: Reliefs
   - Review and download checklist

4. **Calculate payment due**:
   - Use **Payment Calculator**
   - Enter estate details
   - System calculates:
     - IHT due before grant: Estate funds
     - IHT payable in instalments: Property
     - Interest charges if paid late

5. **Check Direct Payment Scheme**:
   - System identifies DPS-eligible assets
   - Generates authorization forms for banks

6. **Review deadlines**:
   - IHT due: 6 months after end of month of death
   - Account due: 12 months after end of month of death
   - Set calendar reminders

### Guide 5: Optimizing Business Relief

**Time required**: 25 minutes

**Steps**:

1. **Identify qualifying assets**:
   - Unquoted company shares
   - AIM-listed shares (not all qualify)
   - Business property
   - Farmland (may qualify for APR instead)

2. **Check ownership period**:
   - Must own for 2+ years for 100% relief
   - Some assets need 2+ years for 50% relief

3. **Add business assets**:
   - Navigate to IHT Calculator
   - Add asset, select type: "Business"
   - Choose relief type:
     - Unquoted shares: 100%
     - AIM shares: 100%
     - Quoted controlling: 50%
     - Business assets: 50%
   - Enter ownership years: [Must be 2+]

4. **Identify excepted assets**:
   - Mark if asset is:
     - Investments (not trading)
     - Excess cash not needed for business
     - Personal assets

5. **Calculate relief**:
   - System applies appropriate relief percentage
   - Reduces taxable estate accordingly

6. **Plan for future changes**:
   - Note: From April 2026, BR/APR capped at £1M per person
   - System shows warning if affected
   - Consider advance planning

7. **Monitor relief qualification**:
   - Use **Valuation Tools** > **Ownership Period Tracker**
   - Track when 2-year requirement is met
   - Set reminders for review

---

## Understanding IHT Calculations

### How IHT is Calculated

The calculation follows this order:

1. **Gross Estate**: Add up all assets at market value
2. **Deduct Liabilities**: Subtract debts, funeral expenses
3. **Net Estate**: Gross estate minus liabilities
4. **Apply Exemptions**: Spouse exemption, charity gifts
5. **Chargeable Estate**: Net estate after exemptions
6. **Add Gifts**: Include CLTs and failed PETs (within 7 years)
7. **Cumulative Total**: Estate + chargeable gifts
8. **Apply Nil-Rate Bands**: NRB and RNRB
9. **Calculate Tax**: 40% (or 36%) on amount above NRBs

### Example Full Calculation

**Scenario**: John dies leaving an estate of £2.5M, including his £400K home to his daughter.

```
Step 1: Gross Estate
- Main residence: £400,000
- Investments: £1,800,000
- Personal effects: £300,000
Total: £2,500,000

Step 2: Liabilities
- Mortgage: £100,000
- Funeral: £5,000
Total: £105,000

Step 3: Net Estate
£2,500,000 - £105,000 = £2,395,000

Step 4: Exemptions
- Charitable gift: £50,000
Chargeable estate: £2,345,000

Step 5: Add Gifts (within 7 years)
- Gift to son (5 years ago): £150,000
- Less: Annual exemption: £3,000
- Less: Taper relief (60%): £58,800
Chargeable gift: £88,200

Step 6: Cumulative Total
£2,345,000 + £88,200 = £2,433,200

Step 7: Apply Nil-Rate Bands
- Standard NRB: £325,000
- RNRB: £175,000 (home to direct descendant)
- Total tax-free: £500,000

Step 8: RNRB Taper Check
Estate over £2M, so RNRB tapers:
£2,433,200 - £2,000,000 = £433,200 over threshold
RNRB reduction: £433,200 ÷ 2 = £216,600
Reduced RNRB: £175,000 - £175,000 = £0 (fully tapered)

Revised NRB: £325,000 only

Step 9: Calculate Tax
Taxable: £2,433,200 - £325,000 = £2,108,200
IHT due: £2,108,200 × 40% = £843,280
```

### RNRB Tapering Explained

The Residence Nil-Rate Band (RNRB) tapers when the net estate exceeds £2 million.

**Taper rate**: £1 reduction for every £2 over the threshold

**Examples**:

| Estate Value | Amount Over £2M | RNRB Reduction | Remaining RNRB |
|--------------|-----------------|----------------|----------------|
| £2,000,000   | £0              | £0             | £175,000       |
| £2,100,000   | £100,000        | £50,000        | £125,000       |
| £2,200,000   | £200,000        | £100,000       | £75,000        |
| £2,350,000+  | £350,000+       | £175,000       | £0             |

**Key points**:
- RNRB fully disappears at £2.35M
- Only applies if home passes to direct descendants
- Can be transferred between spouses (TRNRB)

### Taper Relief on Gifts

Taper relief reduces IHT on PETs given 3-7 years before death.

**Important**: Taper relief reduces the TAX, not the gift value.

**Example**:
```
Gift of £500,000 made 5 years ago
Less: NRB available: £325,000
Taxable: £175,000
IHT at 40%: £70,000
Taper relief (60%): -£42,000
IHT due: £28,000
```

**Without taper relief, IHT would be £70,000. With 60% taper (5 years), it's reduced to £28,000.**

### Charitable Rate Reduction

If you leave 10% or more of your net estate to charity, the IHT rate reduces from 40% to 36%.

**Calculation**:

1. Calculate baseline amount (net estate after NRBs but before charitable gift)
2. Check if charitable gift ≥ 10% of baseline
3. If yes, apply 36% rate instead of 40%

**Example**:
```
Net estate: £1,000,000
NRB: £325,000
Baseline: £675,000

Charitable gift: £70,000 (10.37% of £675,000)
Qualifies for reduced rate ✓

Chargeable estate: £930,000 (£1M - £70K)
Less NRB: £325,000
Taxable: £605,000

IHT at 36%: £217,800
(vs. £242,000 at 40% without charity)

Net benefit:
- Tax saved: £24,200
- Charity receives: £70,000
- Estate receives: £45,800 less, but saves £24,200 = £21,600 actual cost
```

### Business Property Relief (BR)

BR provides relief on qualifying business assets:

**100% Relief**:
- Shares in unquoted trading companies
- AIM shares (if trading company)
- Sole trader business assets

**50% Relief**:
- Controlling shareholding in quoted company
- Land/buildings used in partnership
- Assets used in business

**Requirements**:
- Owned for 2+ years
- Trading business (not investment)
- Not excepted assets (cash, investments)

**Post-April 2026**: BR and APR capped at £1M per person

### Agricultural Property Relief (APR)

APR provides relief on agricultural property:

**100% Relief**:
- Owner occupied for 2+ years
- Let for agricultural use for 7+ years

**50% Relief**:
- Certain lettings

**Qualifying property**:
- Farmland
- Farm buildings
- Cottages for farm workers
- Farmhouse (if character appropriate)

**Not qualifying**:
- Residential development land
- Diversified business assets

---

## Advanced Features

### Multiple Marriage Tracking

If you're claiming unused nil-rate bands from deceased spouse(s), track multiple marriages:

1. Navigate to **Estate Scenarios** or use advanced calculator
2. Add deceased spouse details:
   - Date of death
   - Estate value at death
   - IHT paid
   - Unused NRB percentage
   - Unused RNRB percentage

3. System calculates:
   - Transferred NRB (TNRB)
   - Transferred RNRB (TRNRB)
   - Maximum: 100% additional from all spouses combined

**Example**:
```
First spouse died 2010:
- Used 50% of NRB
- Available TNRB: 50%

Second spouse died 2018:
- Used 30% of NRB
- Available TNRB: 70%

However, combined TNRB capped at 100%
Your total NRB: £325K + £325K = £650K
```

### Downsizing Addition

If you downsize or sell your home after 8 July 2015, you may still get RNRB.

**Rules**:
1. Sold/disposed of main residence after 8 July 2015
2. Estate includes a qualifying residential interest OR
3. Assets of equivalent value passed to direct descendants
4. Total estate must be under RNRB taper threshold (£2M)

**Calculation**:
```
Previous home value: £500,000
RNRB limit: £175,000
Capped at: £175,000

Current home value: £100,000
Shortfall: £75,000

Other assets to descendants: £200,000
Downsizing addition: £75,000 (limited to shortfall)

Total RNRB: £100,000 + £75,000 = £175,000
```

### Gift with Reservation (GWR)

A gift where you retain a benefit is treated as still being in your estate.

**Examples of GWR**:
- Gift house to children but continue living there rent-free
- Gift shares but retain dividends
- Gift property but keep a key and use it

**Consequences**:
- Asset still in estate for IHT
- May trigger Pre-Owned Assets Tax (POAT) during lifetime

**Avoiding GWR**:
1. Pay market rent if using gifted property
2. Make gift outright with no benefit
3. Structure as trust (but trust charges apply)

**Our system**:
- Flags potential GWR gifts
- Calculates POAT liability
- Suggests compliant alternatives

### Quick Succession Relief (QSR)

If you inherit assets and die within 5 years, QSR reduces IHT on those assets.

**Relief scale**:
| Death Within | Relief |
|--------------|--------|
| 1 year       | 100%   |
| 1-2 years    | 80%    |
| 2-3 years    | 60%    |
| 3-4 years    | 40%    |
| 4-5 years    | 20%    |
| 5+ years     | 0%     |

**Calculation**:
```
Inheritance received: £400,000
IHT paid on it: £160,000
Death 3.5 years later

QSR: £160,000 × 40% = £64,000
IHT liability reduced by £64,000
```

### Foreign Assets and Domicile

UK domicile determines worldwide IHT exposure.

**UK Domiciled**:
- IHT on worldwide assets
- All reliefs available

**Non-UK Domiciled**:
- IHT on UK assets only
- Excluded property: Non-UK assets

**Deemed Domicile** (from April 2025):
- Based on residence, not domicile
- Resident for 10+ years of last 20 years
- Long-term residence rules

**Our calculator**:
- Flags non-UK assets
- Calculates excluded property
- Applies residence-based rules post-2025

---

## Compliance and Reporting

### Excepted Estate Rules

Not all estates require a full IHT400 account. Check if you qualify as an excepted estate:

**Excepted Estate Categories**:

1. **Low Value Estate** (IHT205):
   - Gross estate under £325,000 OR
   - Net chargeable estate under NRB (after exemptions/reliefs)
   - No more than £150,000 trust assets
   - No foreign assets over £100,000

2. **Exempt Estate** (IHT207):
   - Everything to spouse/charity
   - Only UK/Channel Islands/Isle of Man assets
   - No trusts (except immediate post-death interest)

3. **Foreign Domicile** (IHT400C):
   - Non-UK domiciled
   - Only UK assets
   - UK assets under £150,000

**Use our checker**:
1. Go to **IHT Compliance** > **Excepted Estate**
2. Answer questions about the estate
3. System determines which form needed

### IHT400 Preparation

If you need a full IHT400, our system helps:

**Data Collection**:
- All assets with values
- All liabilities
- 7-year gift history
- Trust details
- Exemptions and reliefs

**Form Schedules**:
- IHT400: Main form
- IHT401: UK residential property
- IHT402: Quoted stocks and shares
- IHT403: Business or partnership interests
- IHT404: Unlisted stocks and shares
- IHT405: Agricultural property
- IHT406: Transferred nil rate band
- IHT407: Gifts made before death
- IHT408: Trusts
- IHT409: Foreign assets
- IHT410: Relief for business property

**Our system**:
- Pre-populates all fields
- Calculates totals
- Generates PDF checklist
- Flags missing information

### Payment Planning

**When IHT is Due**:
- 6 months after end of month of death
- Example: Death in March 2024 → IHT due by 30 September 2024

**Payment Options**:

1. **Immediate Payment**:
   - Most assets must be paid upfront
   - From estate liquid assets

2. **Instalment Option**:
   - Available for:
     - Land and buildings
     - Business/partnership interests
     - Controlling shareholdings
   - 10 annual instalments
   - Interest charged on outstanding balance

3. **Direct Payment Scheme (DPS)**:
   - Instruct banks/institutions to pay directly to HMRC
   - Avoids need for executors to access funds
   - Our system identifies DPS-eligible assets

**Interest Charges**:
- Late payment interest: Currently 7.75% (varies)
- Instalment interest: 4.75% (varies)
- Interest accrues daily

**Our calculator helps**:
- Determine which assets qualify for instalments
- Calculate total interest if paid in instalments
- Optimize payment strategy

### Record Keeping

**What to keep**:
- All gift records (perpetually for gifts within 7 years)
- Asset valuations
- Trust deeds and accounts
- Business accounts (if claiming BR)
- Agricultural records (if claiming APR)
- Evidence of normal expenditure out of income

**Our system**:
- Stores all gift records
- Exports complete gift history
- Generates annual gift summaries
- Produces trust charge reports

---

## Frequently Asked Questions

### General IHT Questions

**Q: Do I need to worry about IHT?**

A: Check these factors:
- Is your estate over £325,000? (or £500,000 with RNRB)
- Are you married? Spouse exemption applies
- Have you made gifts over £3,000/year?
- Do you have business/agricultural property?

Most estates under £500,000 have no IHT, especially if married.

**Q: Can I give away everything and avoid IHT?**

A: Technically yes, but:
- You must survive 7 years after gifting
- Gifts with reservation don't work
- You need income/assets to live on
- POAT may apply if you retain benefit

**Q: How does being married affect IHT?**

A: Major benefits:
- Unlimited spouse exemption (if UK domiciled)
- Can transfer unused NRB to surviving spouse
- Can transfer unused RNRB to surviving spouse
- Estate planning opportunities on first death

**Q: What counts as a direct descendant for RNRB?**

A: Includes:
- Children (including adopted, step, foster)
- Grandchildren
- Great-grandchildren
- Spouses of descendants

**Q: Do pensions form part of my estate for IHT?**

A: Currently (2024/25):
- Most pensions: No IHT (discretionary payment)
- From April 2027: Unused pensions WILL be included

**Q: How does the 7-year rule work?**

A: Gifts become exempt if you survive 7 years:
- 0-3 years: Full IHT if you die
- 3-7 years: IHT with taper relief
- 7+ years: Fully exempt

But cumulation rules apply for CLTs.

### Gift Questions

**Q: What's the difference between PET and CLT?**

A:
- **PET**: Gift to individual. No immediate IHT. Becomes exempt after 7 years.
- **CLT**: Gift to trust. May have immediate IHT. Counts in cumulation for 7 years.

**Q: Can I use annual exemption on CLT?**

A: Yes, annual exemption (£3,000) can apply to both PETs and CLTs.

**Q: What happens if I make gifts exceeding annual exemption?**

A:
- Exempt amount: £3,000 (+ previous year if unused)
- Excess becomes PET
- If you survive 7 years, no IHT
- If you die within 7 years, IHT may apply (with taper relief after 3 years)

**Q: Can I give wedding gifts?**

A: Yes, special exemptions:
- To your child: £5,000
- To your grandchild: £2,500
- To anyone else: £1,000

Must be "in contemplation of marriage" (usually shortly before).

**Q: What is "normal expenditure out of income"?**

A: Gifts that are:
- Made regularly (pattern established)
- From income (not capital)
- Leave you with sufficient income to maintain normal lifestyle

Examples: Regular payments to children, premiums on life insurance for someone else.

**Q: Do small gifts count toward annual exemption?**

A: No, separate exemptions:
- Annual exemption: £3,000
- Small gifts: £250 per person (can't combine with annual for same person)

You can give £250 to unlimited people separately from your £3,000.

### Trust Questions

**Q: Why use a trust?**

A: Benefits:
- Control asset distribution
- Protect assets for beneficiaries
- Manage assets for minors
- IHT planning (but trust charges apply)

**Q: What's a 10-year charge?**

A: Periodic charge on relevant property trusts:
- Occurs every 10 years
- Up to 6% of trust value
- Calculated based on how much of NRB was used at entry

**Q: What's an exit charge?**

A: Charge when assets leave trust:
- Before first 10-year anniversary: Complex calculation
- After: Pro-rated from last 10-year charge
- Can be 0% if trust value under NRB

**Q: Are all trusts subject to these charges?**

A: No, exemptions:
- Bare trusts: No charges
- IPDI (life interest) trusts: In life tenant's estate
- Bereaved minor trusts: Special treatment
- Disabled person trusts: Special treatment

**Q: Can I avoid trust charges?**

A: Strategies:
- Use NRB at trust creation (no entry charge)
- Distribute before 10-year anniversary
- Use excluded property (non-UK assets for non-dom)
- Structure as IPDI instead

### Business Relief Questions

**Q: Does BR apply to my company shares?**

A: Check:
- Trading company? (not investment company)
- Owned 2+ years?
- Unquoted or AIM? Usually 100%
- Quoted but controlling? 50%

**Q: What's an excepted asset?**

A: Asset not used for business:
- Excess cash
- Investment properties
- Quoted investments
- No BR on these

**Q: Can I get BR on my rental properties?**

A: Generally no, unless:
- FHL (furnished holiday lettings) qualifying as trade
- Part of BR-qualifying farming enterprise
- Genuine B&B/hotel operation

**Q: What happens to BR in 2026?**

A: From 6 April 2026:
- BR and APR capped at £1M per person
- 50% relief above £1M
- Significant impact on larger estates

**Q: Does the 2-year rule restart if I sell shares?**

A: Complex rules:
- If replacing with similar shares: May not restart
- If investing proceeds in different business: Restarts
- Keep detailed records

### Compliance Questions

**Q: When do I need to report a death to HMRC?**

A: Timescales:
- IHT400/205/207: Within 12 months
- IHT payment: Within 6 months (usually)
- Probate application: After IHT sorted

**Q: What if I can't pay IHT before grant?**

A: Options:
- Direct Payment Scheme (DPS): Banks pay directly
- Borrow against estate
- Instalment option for qualifying assets
- HMRC may allow payment from estate in rare cases

**Q: Can I use the instalment option for IHT?**

A: Available for:
- Land and buildings: Yes
- Business interests: Yes
- Controlling shareholdings: Yes
- Quoted shares (non-controlling): No
- Cash/investments: No

**Q: What's the Direct Payment Scheme?**

A: Scheme where:
- Banks/institutions pay IHT directly to HMRC
- No need for executors to access funds first
- Speeds up probate process
- Limited to certain institutions

**Q: What penalties apply for late filing?**

A: HMRC penalties:
- Late IHT400: £100 initial, then daily/percentage
- Late payment: Interest charged (currently 7.75%)
- Incorrect information: Penalties for careless/deliberate errors

**Q: How long do I keep estate records?**

A: Recommended:
- Permanently: Will, grant of probate, IHT forms
- 10+ years: Asset valuations, tax calculations
- 7 years: Gift records (from date of gift)
- Indefinitely: Trust deeds and major documents

### Technical Questions

**Q: How is taper relief calculated?**

A: On the TAX, not the gift:
```
Gift: £425,000 (4.5 years before death)
Less NRB: £325,000
Taxable: £100,000
Tax at 40%: £40,000
Taper relief at 40%: £16,000
IHT due: £24,000
```

**Q: How does RNRB tapering work exactly?**

A: £1 reduction per £2 over £2M:
```
Estate: £2,200,000
Excess: £200,000
Reduction: £200,000 ÷ 2 = £100,000
RNRB: £175,000 - £100,000 = £75,000
```

**Q: Can I get RNRB if I don't own a home?**

A: Possibly, through downsizing addition:
- Must have owned qualifying residence after 8 July 2015
- Disposed of it
- Leave assets of equivalent value to descendants

**Q: How does the charitable rate reduction work?**

A:
1. Calculate baseline (estate - NRBs, before charity)
2. Check if charity ≥ 10% of baseline
3. If yes, use 36% instead of 40% on remaining estate

Net effect: Costs about 1.5% to give 10% to charity.

**Q: What's cumulation in relation to gifts?**

A:
- CLTs cumulate for 7 years
- Later gifts use up earlier NRB
- Example:
  - Year 1: CLT £100,000 (uses £100K of NRB)
  - Year 3: CLT £250,000 (uses remaining £225K of NRB, £25K taxable)

**Q: Can I transfer RNRB if my spouse didn't own a home?**

A: From 6 April 2017, yes:
- RNRB introduced 6 April 2017
- If first death before this, can still transfer unused portion
- Based on proportion, not actual value

---

## Getting Help

### In-App Help

Every section includes:
- **Tooltips**: Hover over ⓘ icons for quick explanations
- **Examples**: Click "Show Example" for worked scenarios
- **Guidance**: Step-by-step instructions in each tool

### Documentation

- **User Guide**: This document (comprehensive how-to)
- **Calculation Methodology**: Technical document on calculation rules
- **Compliance Checklist**: HMRC compliance requirements
- **API Documentation**: For developers integrating with the system

### Support Contacts

For technical issues:
- In-app feedback form
- Email: support@finplan.example (if applicable)

For tax advice:
- Consult a qualified tax adviser or solicitor
- This tool provides calculations, not professional advice

### Professional Advice

**When to seek professional advice**:
- Complex estates (over £2M)
- Overseas assets or non-UK domicile
- Business valuations
- Trust structuring
- Contentious estates
- Any uncertainty

**What professionals can help**:
- Solicitor: Estate planning, trust deeds, probate
- Accountant: Tax calculations, business valuations
- Financial adviser: Investment and pension planning
- Tax adviser: Complex IHT scenarios
- Valuer: Property and business valuations

---

## Appendix: Key Terms

**Annual Exemption**: £3,000 per year gift allowance, can carry forward 1 year

**APR**: Agricultural Property Relief - 100% or 50% relief on qualifying farmland

**BPR**: Business Property Relief - 100% or 50% relief on qualifying business assets

**Chargeable Transfer**: Gift that may be subject to IHT (CLT or failed PET)

**CLT**: Chargeable Lifetime Transfer - gift to trust, immediately chargeable

**Cumulation**: Adding previous gifts when calculating IHT on later gifts/death

**Domicile**: Country of permanent home, determines worldwide IHT exposure

**DPS**: Direct Payment Scheme - banks pay IHT directly to HMRC

**Excepted Estate**: Estate that doesn't require full IHT400 form

**GWR**: Gift with Reservation - gift where donor retains benefit

**IPDI**: Immediate Post-Death Interest - type of life interest trust

**NRB**: Nil-Rate Band - £325,000 threshold below which no IHT

**PET**: Potentially Exempt Transfer - gift to individual, exempt if survive 7 years

**POAT**: Pre-Owned Assets Tax - annual charge on certain gifted assets

**QSR**: Quick Succession Relief - relief when die within 5 years of inheriting

**RNRB**: Residence Nil-Rate Band - additional £175,000 for main residence to descendants

**Taper Relief**: Reduces IHT on PETs given 3-7 years before death

**TNRB**: Transferred Nil-Rate Band - unused NRB from deceased spouse

**TRNRB**: Transferred RNRB - unused RNRB from deceased spouse

---

## Document Information

**Version**: 1.0
**Last Updated**: 2025-09-30
**Tax Year**: 2024/25
**Next Review**: 2026-04-06 (after Spring Budget)

**Disclaimer**: This guide is for educational purposes only. While every effort has been made to ensure accuracy, it does not constitute professional tax or legal advice. Always consult qualified professionals for your specific circumstances. Tax rules and rates are subject to change.