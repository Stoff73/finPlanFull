# UK Inheritance Tax - Calculation Methodology

## Document Purpose

This technical document explains the mathematical formulas, algorithms, and logic used in the IHT Calculator. It serves as a reference for developers, auditors, and tax professionals who need to understand the exact methodology behind the calculations.

## Document Information

**Version**: 1.0
**Tax Year**: 2024/25
**Last Updated**: 2025-09-30
**Compliance**: HMRC Inheritance Tax Manual (IHTM)
**Legislation**: Inheritance Tax Act 1984 (as amended)

---

## Table of Contents

1. [Core Constants and Parameters](#core-constants-and-parameters)
2. [Estate Valuation](#estate-valuation)
3. [Nil-Rate Band Calculations](#nil-rate-band-calculations)
4. [Residence Nil-Rate Band (RNRB)](#residence-nil-rate-band-rnrb)
5. [Gift Calculations](#gift-calculations)
6. [Taper Relief](#taper-relief)
7. [Exemptions](#exemptions)
8. [Business and Agricultural Property Relief](#business-and-agricultural-property-relief)
9. [Trust Calculations](#trust-calculations)
10. [Charitable Rate Reduction](#charitable-rate-reduction)
11. [Quick Succession Relief](#quick-succession-relief)
12. [Advanced Scenarios](#advanced-scenarios)
13. [Compliance Calculations](#compliance-calculations)

---

## Core Constants and Parameters

### 2024/25 Tax Year Constants

```python
# Nil-Rate Bands
STANDARD_NRB = 325000  # £325,000 (frozen until 2030)
RESIDENCE_NRB = 175000  # £175,000 (frozen until 2030)

# Tax Rates
IHT_STANDARD_RATE = 0.40  # 40%
IHT_REDUCED_CHARITY_RATE = 0.36  # 36%
LIFETIME_RATE = 0.20  # 20% on lifetime CLTs

# RNRB Taper
RNRB_TAPER_THRESHOLD = 2000000  # £2,000,000
RNRB_TAPER_RATE = 0.5  # £1 reduction per £2 over threshold

# Gift Exemptions
ANNUAL_EXEMPTION = 3000  # £3,000 per tax year
SMALL_GIFT_LIMIT = 250  # £250 per person
WEDDING_GIFT_CHILD = 5000  # £5,000
WEDDING_GIFT_GRANDCHILD = 2500  # £2,500
WEDDING_GIFT_OTHER = 1000  # £1,000

# Trust Charges
TRUST_ENTRY_RATE = 0.20  # 20% on amount over NRB
TRUST_TEN_YEAR_RATE = 0.06  # 6% maximum
TRUST_EFFECTIVE_RATE_MULTIPLIER = 0.30  # 30% of death rate

# Future Changes
BR_APR_CAP_DATE = date(2026, 4, 6)  # 6 April 2026
BR_APR_CAP_AMOUNT = 1000000  # £1,000,000
PENSION_IHT_INCLUSION_DATE = date(2027, 4, 6)  # 6 April 2027
```

### Time Calculations

```python
def years_between_dates(start_date: date, end_date: date) -> float:
    """
    Calculate years between two dates with precision.
    Used for taper relief and trust charge calculations.
    """
    delta = end_date - start_date
    return delta.days / 365.25  # Account for leap years

def get_tax_year(calculation_date: date) -> str:
    """
    Determine UK tax year from a date.
    Tax year runs 6 April to 5 April.
    """
    if calculation_date.month < 4 or (calculation_date.month == 4 and calculation_date.day < 6):
        return f"{calculation_date.year - 1}/{calculation_date.year % 100:02d}"
    else:
        return f"{calculation_date.year}/{(calculation_date.year + 1) % 100:02d}"
```

---

## Estate Valuation

### Gross Estate Calculation

```python
def calculate_gross_estate(assets: List[Asset]) -> float:
    """
    Sum all assets at market value on date of death.

    Formula:
    Gross Estate = Σ(asset_value_i) for all i
    """
    gross_estate = sum(asset.value for asset in assets)
    return gross_estate
```

### Net Estate Calculation

```python
def calculate_net_estate(gross_estate: float, liabilities: List[Liability]) -> float:
    """
    Deduct allowable liabilities from gross estate.

    Formula:
    Net Estate = Gross Estate - Σ(liability_i) - Funeral Expenses

    Allowable liabilities:
    - Mortgages and secured debts
    - Unsecured debts owed at death
    - Reasonable funeral expenses (typically £5,000-£15,000)
    """
    total_liabilities = sum(liability.amount for liability in liabilities)
    net_estate = gross_estate - total_liabilities
    return net_estate
```

### Chargeable Estate Calculation

```python
def calculate_chargeable_estate(
    net_estate: float,
    spouse_exemption: float,
    charitable_gifts: float,
    other_exemptions: float
) -> float:
    """
    Apply exemptions to determine chargeable estate.

    Formula:
    Chargeable Estate = Net Estate - Spouse Gifts - Charity - Other Exemptions

    Exemptions:
    - Spouse/civil partner: Unlimited (if UK domiciled)
    - Charity: Unlimited
    - Political parties: Certain conditions
    - National institutions: Museums, universities, etc.
    """
    chargeable = net_estate - spouse_exemption - charitable_gifts - other_exemptions
    return max(0, chargeable)  # Cannot be negative
```

---

## Nil-Rate Band Calculations

### Standard NRB Application

```python
def calculate_available_nrb(
    standard_nrb: float = 325000,
    tnrb_percentage: float = 0,
    lifetime_gifts: List[Gift] = None
) -> float:
    """
    Calculate available NRB after transfers and lifetime gifts.

    Formula:
    Available NRB = (Standard NRB × (1 + TNRB%)) - Lifetime CLTs within 7 years

    Where:
    - TNRB% = Transferred nil-rate band from deceased spouse (0-100%)
    - Lifetime CLTs = Chargeable lifetime transfers within 7 years

    Maximum NRB = £650,000 (£325k + 100% transfer)
    """
    # Base NRB plus any transferred amount
    total_nrb = standard_nrb * (1 + tnrb_percentage / 100)

    # Reduce by CLTs made within 7 years of death
    if lifetime_gifts:
        clt_total = sum(
            gift.net_amount for gift in lifetime_gifts
            if gift.gift_type == "CLT" and gift.years_before_death <= 7
        )
        total_nrb -= clt_total

    return max(0, total_nrb)
```

### Transferred NRB (TNRB) Calculation

```python
def calculate_tnrb_percentage(
    deceased_spouse_estate: float,
    deceased_spouse_nrb: float,
    deceased_spouse_exempt_amount: float
) -> float:
    """
    Calculate percentage of NRB unused by deceased spouse.

    Formula:
    TNRB% = ((NRB - (Estate - Exemptions)) / NRB) × 100

    Simplified:
    TNRB% = ((NRB - Chargeable Estate) / NRB) × 100

    Example:
    Estate: £400,000
    Spouse exemption: £300,000
    NRB at death: £325,000
    Chargeable: £100,000
    TNRB% = ((325,000 - 100,000) / 325,000) × 100 = 69.23%

    Surviving spouse can claim 69.23% of current NRB (£225,000)
    """
    chargeable = deceased_spouse_estate - deceased_spouse_exempt_amount
    unused_nrb = deceased_spouse_nrb - chargeable
    percentage = (unused_nrb / deceased_spouse_nrb) * 100
    return max(0, min(100, percentage))  # Clamp between 0-100%

def calculate_combined_tnrb(spouse_records: List[DeceasedSpouse]) -> float:
    """
    Calculate combined TNRB from multiple deceased spouses.

    Rule: Maximum 100% additional NRB regardless of number of spouses.

    Formula:
    Total TNRB% = min(100%, Σ(TNRB%_i) for each deceased spouse i)
    """
    total_percentage = sum(spouse.tnrb_percentage for spouse in spouse_records)
    return min(100, total_percentage)
```

---

## Residence Nil-Rate Band (RNRB)

### Basic RNRB Qualification

```python
def qualifies_for_rnrb(
    has_qualifying_residence: bool,
    has_direct_descendants: bool,
    residence_left_to_descendants: bool
) -> bool:
    """
    Check if estate qualifies for RNRB.

    Conditions:
    1. Estate includes qualifying residential interest (QRI)
    2. QRI closely inherited by direct descendants
    3. Dies on or after 6 April 2017

    Direct descendants include:
    - Children (biological, adopted, step, foster)
    - Grandchildren
    - Great-grandchildren
    - Spouses/civil partners of descendants
    """
    return (
        has_qualifying_residence
        and has_direct_descendants
        and residence_left_to_descendants
    )
```

### RNRB Tapering Calculation

```python
def calculate_tapered_rnrb(
    net_estate: float,
    base_rnrb: float = 175000,
    taper_threshold: float = 2000000,
    taper_rate: float = 0.5
) -> float:
    """
    Calculate RNRB after tapering for estates over £2M.

    Formula:
    Tapered RNRB = max(0, Base RNRB - ((Net Estate - Threshold) × Taper Rate))

    Where:
    - Taper Rate = 0.5 (£1 reduction per £2 over threshold)
    - Threshold = £2,000,000

    Example 1:
    Estate: £2,100,000
    Excess: £100,000
    Reduction: £100,000 × 0.5 = £50,000
    RNRB: £175,000 - £50,000 = £125,000

    Example 2:
    Estate: £2,350,000 or more
    Excess: £350,000+
    Reduction: £175,000+ (fully tapered)
    RNRB: £0
    """
    if net_estate <= taper_threshold:
        return base_rnrb

    excess = net_estate - taper_threshold
    reduction = excess * taper_rate
    tapered_rnrb = base_rnrb - reduction

    return max(0, tapered_rnrb)
```

### RNRB with Property Value Limits

```python
def calculate_available_rnrb(
    tapered_rnrb: float,
    qualifying_residence_value: float,
    residence_liabilities: float
) -> float:
    """
    RNRB limited to net value of qualifying residence.

    Formula:
    Available RNRB = min(Tapered RNRB, Net Residence Value)

    Where:
    Net Residence Value = Residence Value - Residence Liabilities (mortgages)

    Example:
    Tapered RNRB: £175,000
    House value: £400,000
    Mortgage: £50,000
    Net value: £350,000
    Available RNRB: £175,000 (full amount, as £350k > £175k)

    Example 2:
    Tapered RNRB: £175,000
    House value: £150,000
    Mortgage: £0
    Net value: £150,000
    Available RNRB: £150,000 (limited by property value)
    """
    net_residence_value = qualifying_residence_value - residence_liabilities
    return min(tapered_rnrb, net_residence_value)
```

### Transferred RNRB (TRNRB)

```python
def calculate_trnrb(
    deceased_spouse_estate: float,
    deceased_spouse_rnrb: float,
    deceased_spouse_residence_value: float,
    deceased_spouse_to_descendants: float
) -> float:
    """
    Calculate transferable RNRB from deceased spouse.

    Rules:
    - RNRB introduced 6 April 2017
    - If first death before 2017, can still calculate as if existed
    - Based on percentage unused
    - Applied at current RNRB rate when second dies

    Formula:
    TRNRB% = ((Available RNRB - Used RNRB) / Available RNRB) × 100

    Example:
    First death 2020:
    RNRB available: £175,000
    Residence to descendants: £100,000
    Used: £100,000
    Unused: £75,000
    TRNRB%: (£75,000 / £175,000) × 100 = 42.86%

    Second death 2025:
    Current RNRB: £175,000
    TRNRB: £175,000 × 42.86% = £75,000
    Total RNRB: £175,000 + £75,000 = £250,000
    """
    # Calculate what was available at first death
    available_rnrb = min(deceased_spouse_rnrb, deceased_spouse_residence_value)

    # Calculate what was used
    used_rnrb = min(available_rnrb, deceased_spouse_to_descendants)

    # Unused percentage
    unused_rnrb = available_rnrb - used_rnrb
    trnrb_percentage = (unused_rnrb / deceased_spouse_rnrb) * 100 if deceased_spouse_rnrb > 0 else 0

    return trnrb_percentage
```

### Downsizing Addition

```python
def calculate_downsizing_addition(
    previous_residence_value: float,
    current_residence_value: float,
    assets_to_descendants: float,
    date_of_disposal: date,
    date_of_death: date,
    base_rnrb: float = 175000
) -> float:
    """
    Calculate downsizing addition for estates that disposed of residence.

    Conditions:
    1. Disposed of residence after 8 July 2015
    2. Current residence worth less OR no residence
    3. Other assets left to direct descendants

    Formula:
    Lost RNRB = min(Previous Value, Base RNRB) - min(Current Value, Base RNRB)
    Replacement Assets = Assets to Descendants
    Addition = min(Lost RNRB, Replacement Assets, Base RNRB)

    Example:
    Previous home: £500,000
    RNRB limit: £175,000 (capped)
    Current home: £100,000
    Lost RNRB: £175,000 - £100,000 = £75,000
    Assets to descendants: £200,000
    Addition: min(£75,000, £200,000, £175,000) = £75,000

    Total RNRB: £100,000 (current home) + £75,000 (addition) = £175,000
    """
    # Check disposal date
    if date_of_disposal < date(2015, 7, 8):
        return 0

    # Calculate lost RNRB
    previous_rnrb_value = min(previous_residence_value, base_rnrb)
    current_rnrb_value = min(current_residence_value, base_rnrb)
    lost_rnrb = previous_rnrb_value - current_rnrb_value

    if lost_rnrb <= 0:
        return 0

    # Downsizing addition is lowest of:
    # 1. Lost RNRB
    # 2. Assets to descendants
    # 3. Base RNRB
    addition = min(lost_rnrb, assets_to_descendants, base_rnrb)

    return addition
```

---

## Gift Calculations

### PET (Potentially Exempt Transfer) Calculation

```python
def calculate_pet_tax(
    gift_amount: float,
    date_of_gift: date,
    date_of_death: date,
    available_nrb: float,
    exemptions_applied: float = 0
) -> Dict[str, float]:
    """
    Calculate IHT on a PET if donor dies within 7 years.

    Process:
    1. Determine years between gift and death
    2. If > 7 years: No tax (fully exempt)
    3. If ≤ 7 years: Calculate tax with taper relief

    Formula:
    Net Gift = Gift Amount - Exemptions
    Taxable = max(0, Net Gift - Available NRB)
    Gross Tax = Taxable × 40%
    Taper Relief = Gross Tax × Taper %
    Net Tax = Gross Tax - Taper Relief
    """
    years_since_gift = years_between_dates(date_of_gift, date_of_death)

    # Fully exempt if over 7 years
    if years_since_gift > 7:
        return {
            "taxable_amount": 0,
            "tax_before_taper": 0,
            "taper_relief": 0,
            "tax_due": 0,
            "status": "exempt"
        }

    # Calculate net gift after exemptions
    net_gift = gift_amount - exemptions_applied

    # Amount over NRB is taxable
    taxable = max(0, net_gift - available_nrb)

    # Calculate tax at 40%
    gross_tax = taxable * IHT_STANDARD_RATE

    # Apply taper relief if 3-7 years
    taper_percentage = calculate_taper_relief_percentage(years_since_gift)
    taper_relief = gross_tax * (taper_percentage / 100)

    net_tax = gross_tax - taper_relief

    return {
        "taxable_amount": taxable,
        "tax_before_taper": gross_tax,
        "taper_relief": taper_relief,
        "tax_due": net_tax,
        "years_since_gift": years_since_gift,
        "taper_percentage": taper_percentage,
        "status": "chargeable"
    }
```

### CLT (Chargeable Lifetime Transfer) Calculation

```python
def calculate_clt_lifetime_tax(
    transfer_amount: float,
    previous_clts_in_7_years: float,
    current_nrb: float = 325000,
    donor_pays: bool = True
) -> Dict[str, float]:
    """
    Calculate immediate IHT on CLT (typically gift to trust).

    Lifetime rate: 20% (half of death rate)

    Process:
    1. Calculate cumulative total (this CLT + previous CLTs within 7 years)
    2. Determine amount over available NRB
    3. Apply 20% tax
    4. If donor pays, gross up (tax on tax)

    Formula (donor pays):
    Available NRB = Current NRB - Previous CLTs
    Net Transfer = Transfer Amount
    Grossed Up = Net Transfer / (1 - 0.20) = Net Transfer / 0.80
    Taxable = max(0, Grossed Up - Available NRB)
    Tax = Taxable × 20%

    Formula (recipient pays):
    Available NRB = Current NRB - Previous CLTs
    Taxable = max(0, Transfer Amount - Available NRB)
    Tax = Taxable × 20%
    """
    available_nrb = current_nrb - previous_clts_in_7_years

    if donor_pays:
        # Gross up the gift
        grossed_up_amount = transfer_amount / (1 - LIFETIME_RATE)
        taxable = max(0, grossed_up_amount - available_nrb)
        tax = taxable * LIFETIME_RATE
        net_to_trust = transfer_amount
        gross_transfer = transfer_amount + tax
    else:
        # Recipient pays from the gift
        taxable = max(0, transfer_amount - available_nrb)
        tax = taxable * LIFETIME_RATE
        net_to_trust = transfer_amount - tax
        gross_transfer = transfer_amount

    return {
        "gross_transfer": gross_transfer,
        "net_to_trust": net_to_trust,
        "tax_paid": tax,
        "available_nrb_used": min(transfer_amount, available_nrb),
        "taxable_amount": taxable
    }

def calculate_clt_additional_death_tax(
    clt_amount: float,
    lifetime_tax_paid: float,
    death_rate_tax: float
) -> float:
    """
    Calculate additional tax on CLT if donor dies within 7 years.

    Process:
    1. Calculate tax at death rates (40% with taper relief)
    2. Deduct lifetime tax already paid
    3. Additional tax = max(0, Death Tax - Lifetime Tax)

    Note: If lifetime tax > death tax (rare), no refund

    Formula:
    Death Tax = (CLT - Available NRB) × 40% × (1 - Taper%)
    Additional = max(0, Death Tax - Lifetime Tax Paid)
    """
    additional_tax = max(0, death_rate_tax - lifetime_tax_paid)
    return additional_tax
```

### Gift Cumulation

```python
def calculate_cumulative_total(
    gifts: List[Gift],
    date_of_death: date,
    years_to_cumulate: int = 7
) -> List[Gift]:
    """
    Calculate cumulative running total for gift tax purposes.

    Rules:
    1. Gifts cumulate for 7 years before each subsequent gift
    2. Order: Earliest gifts first
    3. Later gifts use NRB remaining after earlier gifts
    4. PETs only cumulate if donor dies within 7 years

    Process:
    For each gift:
        Look back 7 years
        Sum all previous chargeable gifts
        This reduces NRB available for current gift
    """
    # Sort gifts by date (earliest first)
    sorted_gifts = sorted(gifts, key=lambda g: g.date_given)

    cumulative_gifts = []

    for i, gift in enumerate(sorted_gifts):
        # Calculate cumulation window (7 years before this gift)
        window_start = gift.date_given - timedelta(days=365.25 * years_to_cumulate)

        # Sum previous gifts in window
        previous_total = sum(
            g.chargeable_amount
            for g in sorted_gifts[:i]
            if g.date_given >= window_start
        )

        gift.cumulative_total = previous_total + gift.chargeable_amount
        cumulative_gifts.append(gift)

    return cumulative_gifts
```

---

## Taper Relief

### Taper Relief Percentage Calculation

```python
def calculate_taper_relief_percentage(years_since_gift: float) -> float:
    """
    Calculate taper relief percentage based on years since gift.

    Applies to: PETs and CLTs if donor dies within 7 years
    Applies to: The TAX, not the gift amount

    Scale:
    0-3 years:   0% relief
    3-4 years:  20% relief
    4-5 years:  40% relief
    5-6 years:  60% relief
    6-7 years:  80% relief
    7+ years:  100% relief (exempt)

    Important: Use precise years (including days) for boundary cases

    Example:
    Gift made 4 years and 6 months ago: 40% relief
    Tax before relief: £50,000
    Taper relief: £50,000 × 40% = £20,000
    Tax after relief: £30,000
    """
    if years_since_gift < 3:
        return 0
    elif years_since_gift < 4:
        return 20
    elif years_since_gift < 5:
        return 40
    elif years_since_gift < 6:
        return 60
    elif years_since_gift < 7:
        return 80
    else:
        return 100  # Fully exempt

def apply_taper_relief(
    tax_amount: float,
    years_since_gift: float
) -> Dict[str, float]:
    """
    Apply taper relief to calculated tax.

    Formula:
    Taper % = calculate_taper_relief_percentage(years)
    Relief Amount = Tax × (Taper % / 100)
    Tax After Relief = Tax - Relief Amount
    """
    taper_percentage = calculate_taper_relief_percentage(years_since_gift)
    relief_amount = tax_amount * (taper_percentage / 100)
    tax_after_relief = tax_amount - relief_amount

    return {
        "tax_before_relief": tax_amount,
        "taper_percentage": taper_percentage,
        "relief_amount": relief_amount,
        "tax_after_relief": tax_after_relief
    }
```

### Edge Cases in Taper Relief

```python
def handle_taper_boundary_cases(
    gift_date: date,
    death_date: date
) -> Dict[str, Any]:
    """
    Handle precise calculations for gifts near taper boundaries.

    Critical dates:
    - Exactly 3 years: No taper
    - Exactly 3 years + 1 day: 20% taper starts
    - Exactly 7 years: 80% taper
    - 7 years + 1 day: Fully exempt

    Use precise day counting, not rounded years.
    """
    days_difference = (death_date - gift_date).days
    years_precise = days_difference / 365.25

    # Check critical boundaries
    if days_difference == 1095:  # Exactly 3 years
        return {"taper_percentage": 0, "note": "Exactly 3 years - no taper"}
    elif days_difference == 2555:  # Exactly 7 years
        return {"taper_percentage": 80, "note": "Exactly 7 years - 80% taper"}
    elif days_difference > 2555:
        return {"taper_percentage": 100, "note": "Over 7 years - fully exempt"}

    # Standard calculation
    taper_percentage = calculate_taper_relief_percentage(years_precise)
    return {"taper_percentage": taper_percentage, "years_precise": years_precise}
```

---

## Exemptions

### Annual Exemption

```python
def apply_annual_exemption(
    gift_amount: float,
    current_year_used: float = 0,
    previous_year_used: float = 0,
    previous_year_available: bool = True
) -> Dict[str, float]:
    """
    Apply annual gift exemption with carry-forward rules.

    Rules:
    - £3,000 per tax year
    - Can carry forward unused from previous year ONLY
    - Use current year first, then previous year
    - Carry forward expires if not used

    Formula:
    Current Year Available = £3,000 - Current Year Used
    Previous Year Available = £3,000 - Previous Year Used (if eligible)
    Total Available = Current + Previous (if eligible)

    Allocation:
    1. Use current year exemption first
    2. Then use previous year carried forward
    3. Excess is chargeable

    Example:
    Gift: £8,000
    Current year: £3,000 available
    Previous year: £3,000 available (unused from last year)
    Total exemption: £6,000
    Chargeable: £2,000
    """
    ANNUAL_LIMIT = 3000

    # Calculate available exemptions
    current_available = ANNUAL_LIMIT - current_year_used
    previous_available = (ANNUAL_LIMIT - previous_year_used) if previous_year_available else 0
    total_available = current_available + previous_available

    # Apply exemption
    exemption_used = min(gift_amount, total_available)

    # Allocate between current and previous year
    current_used = min(gift_amount, current_available)
    previous_used = max(0, exemption_used - current_used)

    chargeable_amount = gift_amount - exemption_used

    return {
        "gift_amount": gift_amount,
        "exemption_used": exemption_used,
        "current_year_used": current_used,
        "previous_year_used": previous_used,
        "chargeable_amount": chargeable_amount,
        "remaining_current": current_available - current_used,
        "remaining_previous": previous_available - previous_used
    }
```

### Small Gifts Exemption

```python
def apply_small_gifts_exemption(
    gifts_to_recipient: List[Gift]
) -> List[Gift]:
    """
    Apply small gifts exemption (£250 per person per year).

    Rules:
    - £250 per recipient per tax year
    - Unlimited number of recipients
    - Cannot combine with annual exemption for same gift
    - All or nothing (if gift > £250, no exemption)

    Example:
    Gifts of £250 to 10 different people: All exempt
    Gift of £251 to one person: Not exempt under small gifts
    Gift of £250 + £3,000 annual to one person: Annual applies, not small gifts
    """
    SMALL_GIFT_LIMIT = 250

    exempt_gifts = []
    chargeable_gifts = []

    for gift in gifts_to_recipient:
        # Check if eligible
        if (gift.amount <= SMALL_GIFT_LIMIT and
            not gift.annual_exemption_claimed and
            gift.amount == SMALL_GIFT_LIMIT):  # Must be exactly £250 or less

            gift.small_gift_exemption = True
            gift.chargeable_amount = 0
            exempt_gifts.append(gift)
        else:
            chargeable_gifts.append(gift)

    return exempt_gifts + chargeable_gifts
```

### Wedding Gifts Exemption

```python
def calculate_wedding_gift_exemption(
    gift_amount: float,
    relationship: str
) -> float:
    """
    Calculate wedding gift exemption based on relationship.

    Limits:
    - Child: £5,000
    - Grandchild/great-grandchild: £2,500
    - Other: £1,000

    Rules:
    - Must be in contemplation of marriage/civil partnership
    - Given before or shortly after ceremony
    - One exemption per relationship per marriage

    Formula:
    Exemption = min(Gift Amount, Exemption Limit for Relationship)
    Chargeable = Gift Amount - Exemption
    """
    exemption_limits = {
        "child": 5000,
        "grandchild": 2500,
        "great-grandchild": 2500,
        "other": 1000
    }

    relationship_lower = relationship.lower()
    exemption_limit = exemption_limits.get(relationship_lower, 1000)

    exemption_used = min(gift_amount, exemption_limit)
    chargeable = gift_amount - exemption_used

    return {
        "gift_amount": gift_amount,
        "relationship": relationship,
        "exemption_limit": exemption_limit,
        "exemption_used": exemption_used,
        "chargeable_amount": chargeable
    }
```

### Normal Expenditure Out of Income

```python
def qualifies_as_normal_expenditure(
    gift_amount: float,
    total_income: float,
    regular_expenditure: float,
    gift_pattern: List[Gift],
    years_of_pattern: int
) -> Dict[str, Any]:
    """
    Determine if gifts qualify as normal expenditure out of income.

    Three tests (ALL must be satisfied):
    1. Gift is part of normal expenditure
    2. Made out of income (not capital)
    3. Left donor with sufficient income to maintain usual standard of living

    Normal expenditure test:
    - Regular pattern established (usually 2+ years)
    - Similar amounts at similar intervals
    - Habitual and not ad-hoc

    Income test:
    - Clearly from income (salary, pension, dividends, interest)
    - Not from capital or asset sales

    Sufficient income test:
    Remaining Income = Total Income - Gift - Regular Expenditure
    Must be adequate for donor's normal standard of living

    No fixed percentage or amount - based on facts
    """
    # Check pattern (need at least 2 years to establish pattern)
    if years_of_pattern < 2:
        return {
            "qualifies": False,
            "reason": "Insufficient pattern established (need 2+ years)"
        }

    # Check if amounts are consistent
    pattern_amounts = [g.amount for g in gift_pattern]
    avg_amount = sum(pattern_amounts) / len(pattern_amounts)
    variance = max(pattern_amounts) - min(pattern_amounts)

    if variance / avg_amount > 0.5:  # More than 50% variation
        return {
            "qualifies": False,
            "reason": "Amounts not sufficiently regular"
        }

    # Check if made from income
    if gift_amount > total_income:
        return {
            "qualifies": False,
            "reason": "Gift exceeds income"
        }

    # Check if sufficient income remains
    remaining_income = total_income - gift_amount - regular_expenditure

    if remaining_income < regular_expenditure * 0.8:  # Heuristic: need 80% of regular expenditure
        return {
            "qualifies": False,
            "reason": "Insufficient income remaining for normal living"
        }

    return {
        "qualifies": True,
        "exemption_amount": gift_amount,
        "remaining_income": remaining_income
    }
```

---

## Business and Agricultural Property Relief

### Business Property Relief (BPR)

```python
def calculate_business_relief(
    asset_value: float,
    business_type: str,
    ownership_years: float,
    excepted_asset_value: float = 0
) -> Dict[str, float]:
    """
    Calculate Business Property Relief on qualifying assets.

    Relief Rates:
    100% Relief:
    - Unquoted company shares
    - AIM-listed company shares (if trading)
    - Business or interest in business

    50% Relief:
    - Quoted company shares (controlling interest >50%)
    - Land/buildings/machinery used in business

    Requirements:
    - Owned for 2+ years
    - Trading business (not investment)
    - Not excepted assets (investments, excess cash)

    Formula:
    Qualifying Value = Asset Value - Excepted Asset Value
    Relief = Qualifying Value × Relief %
    Chargeable = Asset Value - Relief

    Post-April 2026:
    Cap at £1,000,000 per person
    100% relief on first £1M
    50% relief above £1M
    """
    relief_rates = {
        "unquoted_shares": 1.00,  # 100%
        "aim_shares": 1.00,  # 100%
        "business": 1.00,  # 100%
        "quoted_controlling": 0.50,  # 50%
        "business_property": 0.50  # 50%
    }

    # Check ownership requirement
    if ownership_years < 2:
        return {
            "relief_rate": 0,
            "relief_amount": 0,
            "chargeable_value": asset_value,
            "reason": "Owned less than 2 years"
        }

    # Get relief rate
    relief_rate = relief_rates.get(business_type, 0)

    # Calculate qualifying value (exclude excepted assets)
    qualifying_value = asset_value - excepted_asset_value

    # Calculate relief
    relief_amount = qualifying_value * relief_rate
    chargeable_value = asset_value - relief_amount

    return {
        "asset_value": asset_value,
        "excepted_asset_value": excepted_asset_value,
        "qualifying_value": qualifying_value,
        "relief_rate": relief_rate,
        "relief_amount": relief_amount,
        "chargeable_value": chargeable_value
    }

def calculate_post_2026_br_cap(
    total_br_assets: float,
    cap_amount: float = 1000000
) -> Dict[str, float]:
    """
    Apply BR/APR cap for deaths after 6 April 2026.

    Rules:
    - First £1M: Full relief (100% or 50% as applicable)
    - Above £1M: Half relief (50% or 25% as applicable)

    Formula:
    If total BR assets ≤ £1M:
        Relief = Assets × Original Relief %

    If total BR assets > £1M:
        Relief = (£1M × Original Relief %) + ((Assets - £1M) × (Original Relief % ÷ 2))

    Example:
    Assets: £2M at 100% relief
    Pre-2026: £2M relief, £0 chargeable
    Post-2026: £1M + (£1M × 50%) = £1.5M relief, £500K chargeable
    """
    if total_br_assets <= cap_amount:
        # Under cap - no change
        return {
            "applies_cap": False,
            "relief_at_full_rate": total_br_assets,
            "relief_at_half_rate": 0,
            "note": "Under £1M cap"
        }

    # Over cap - split calculation
    relief_at_full = cap_amount
    relief_at_half = (total_br_assets - cap_amount) * 0.5
    total_relief = relief_at_full + relief_at_half

    return {
        "applies_cap": True,
        "relief_at_full_rate": relief_at_full,
        "relief_at_half_rate": relief_at_half,
        "total_relief": total_relief,
        "chargeable_value": total_br_assets - total_relief
    }
```

### Agricultural Property Relief (APR)

```python
def calculate_agricultural_relief(
    property_value: float,
    occupation_type: str,
    occupation_years: float,
    agricultural_use: bool = True
) -> Dict[str, float]:
    """
    Calculate Agricultural Property Relief.

    Relief Rates:
    100% Relief:
    - Owner occupied (or contract farming) for 2+ years
    - Let for agricultural use for 7+ years (starting 1 Sept 1995)

    50% Relief:
    - Let before 1 Sept 1995 (transitional)

    Qualifying Property:
    - Agricultural land or pasture
    - Growing crops
    - Stud farms (horses for agricultural purposes)
    - Farm buildings
    - Farmhouses (character appropriate test)
    - Cottages for farm workers

    Formula:
    Relief = Property Value × Relief %
    Chargeable = Property Value - Relief

    Post-April 2026: Combined BR/APR cap of £1M
    """
    if not agricultural_use:
        return {
            "relief_amount": 0,
            "chargeable_value": property_value,
            "reason": "Not in agricultural use"
        }

    # Determine relief rate based on occupation
    if occupation_type == "owner_occupied":
        if occupation_years >= 2:
            relief_rate = 1.00  # 100%
        else:
            return {
                "relief_amount": 0,
                "chargeable_value": property_value,
                "reason": "Owner occupied less than 2 years"
            }

    elif occupation_type == "let_post_1995":
        if occupation_years >= 7:
            relief_rate = 1.00  # 100%
        else:
            return {
                "relief_amount": 0,
                "chargeable_value": property_value,
                "reason": "Let less than 7 years"
            }

    elif occupation_type == "let_pre_1995":
        relief_rate = 0.50  # 50%

    else:
        return {
            "relief_amount": 0,
            "chargeable_value": property_value,
            "reason": "Unknown occupation type"
        }

    relief_amount = property_value * relief_rate
    chargeable_value = property_value - relief_amount

    return {
        "property_value": property_value,
        "occupation_type": occupation_type,
        "occupation_years": occupation_years,
        "relief_rate": relief_rate,
        "relief_amount": relief_amount,
        "chargeable_value": chargeable_value
    }
```

---

## Trust Calculations

### Trust Entry Charge

```python
def calculate_trust_entry_charge(
    transfer_amount: float,
    previous_clts: float,
    available_nrb: float = 325000,
    donor_pays: bool = True
) -> Dict[str, float]:
    """
    Calculate entry charge when assets transferred to discretionary trust.

    Rate: 20% on amount over available NRB

    Formula:
    Available NRB = £325,000 - Previous CLTs in 7 years
    Chargeable = max(0, Transfer - Available NRB)
    Entry Charge = Chargeable × 20%

    If donor pays:
    Gross up: Transfer / 0.80

    Example:
    Transfer: £500,000
    Previous CLTs: £0
    NRB: £325,000
    Chargeable: £175,000
    Entry charge: £35,000
    """
    # Calculate available NRB
    remaining_nrb = available_nrb - previous_clts

    if donor_pays:
        # Gross up the transfer
        grossed_amount = transfer_amount / (1 - LIFETIME_RATE)
        chargeable = max(0, grossed_amount - remaining_nrb)
        entry_charge = chargeable * LIFETIME_RATE
    else:
        chargeable = max(0, transfer_amount - remaining_nrb)
        entry_charge = chargeable * LIFETIME_RATE

    return {
        "transfer_amount": transfer_amount,
        "available_nrb": remaining_nrb,
        "chargeable_amount": chargeable,
        "entry_charge": entry_charge,
        "net_to_trust": transfer_amount - (0 if donor_pays else entry_charge)
    }
```

### 10-Year Periodic Charge

```python
def calculate_ten_year_charge(
    trust_value: float,
    date_created: date,
    charge_date: date,
    nrb_at_creation: float,
    nrb_at_charge: float,
    settlor_clts_at_creation: float
) -> Dict[str, float]:
    """
    Calculate 10-year periodic charge on relevant property trust.

    Complex calculation in 3 stages:

    1. Hypothetical transfer rate:
        Assume trust created on 10-year anniversary
        Calculate what rate would apply

    2. Effective rate:
        Hypothetical rate × 30% (special trust rate)

    3. Proportionate charge:
        Effective rate × (Quarters complete / 40)

    Maximum rate: 6%

    Formula:
    Step 1: Hypothetical chargeable = max(0, Trust Value - (NRB - Settlor CLTs))
    Step 2: Hypothetical rate = (Hypothetical chargeable / Trust Value) × 20%
    Step 3: Effective rate = Hypothetical rate × 0.30
    Step 4: Rate for full 10 years = Effective rate
    Step 5: Charge = Trust Value × Effective rate

    Simplified for assets in trust entire 10 years:
    Rate = ((Trust Value - (NRB - Settlor CLTs)) / Trust Value) × 20% × 30%
    Maximum rate: 6% (when Trust Value >> NRB)

    Example:
    Trust value: £700,000
    NRB at creation: £325,000
    Settlor CLTs: £0
    Hypothetical chargeable: £700,000 - £325,000 = £375,000
    Hypothetical rate: (£375,000 / £700,000) × 20% = 10.71%
    Effective rate: 10.71% × 30% = 3.21%
    10-year charge: £700,000 × 3.21% = £22,500
    """
    # Calculate hypothetical rate at 10-year point
    available_nrb = nrb_at_charge - settlor_clts_at_creation
    hypothetical_chargeable = max(0, trust_value - available_nrb)

    if trust_value == 0:
        return {"ten_year_charge": 0}

    # Hypothetical rate
    hypothetical_rate = (hypothetical_chargeable / trust_value) * LIFETIME_RATE

    # Effective rate (30% of death rate)
    effective_rate = hypothetical_rate * TRUST_EFFECTIVE_RATE_MULTIPLIER

    # Cap at 6%
    effective_rate = min(effective_rate, TRUST_TEN_YEAR_RATE)

    # Calculate charge
    ten_year_charge = trust_value * effective_rate

    return {
        "trust_value": trust_value,
        "available_nrb": available_nrb,
        "hypothetical_chargeable": hypothetical_chargeable,
        "hypothetical_rate": hypothetical_rate,
        "effective_rate": effective_rate,
        "ten_year_charge": ten_year_charge
    }
```

### Trust Exit Charge

```python
def calculate_exit_charge(
    distribution_amount: float,
    trust_value_at_exit: float,
    last_ten_year_charge_date: Optional[date],
    exit_date: date,
    effective_rate_at_last_charge: float
) -> Dict[str, float]:
    """
    Calculate exit charge when assets leave relevant property trust.

    Two scenarios:

    A. Before first 10-year anniversary:
    Similar to 10-year charge but proportionate

    B. After 10-year charge(s):
    Use effective rate from last charge
    Proportionate to quarters since last charge

    Formula (after first 10 years):
    Quarters since last charge = (Exit Date - Last Charge Date) / 0.25 years
    Exit rate = Effective Rate × (Quarters / 40)
    Exit charge = Distribution Amount × Exit rate

    Example:
    Distribution: £100,000
    Last 10-year charge: 6 years ago (effective rate was 3%)
    Quarters: 24
    Exit rate: 3% × (24 / 40) = 1.8%
    Exit charge: £100,000 × 1.8% = £1,800
    """
    if last_ten_year_charge_date:
        # After first 10-year charge
        days_since_charge = (exit_date - last_ten_year_charge_date).days
        quarters_since_charge = days_since_charge / (365.25 / 4)

        # Exit rate is proportionate
        exit_rate = effective_rate_at_last_charge * (quarters_since_charge / 40)

    else:
        # Before first 10-year charge
        # Calculate as if had 10-year charge, then proportionate
        # (Simplified - full calculation similar to 10-year charge)
        quarters_since_creation = ((exit_date - date_created).days / (365.25 / 4))

        # Use simplified rate calculation
        exit_rate = calculate_hypothetical_rate(trust_value_at_exit) * (quarters_since_creation / 40)

    exit_charge = distribution_amount * exit_rate

    return {
        "distribution_amount": distribution_amount,
        "exit_rate": exit_rate,
        "exit_charge": exit_charge,
        "quarters_since_last_charge": quarters_since_charge if last_ten_year_charge_date else None
    }
```

---

## Charitable Rate Reduction

### Charitable Legacy Calculation

```python
def calculate_charitable_rate_reduction(
    net_estate: float,
    charitable_legacy: float,
    available_nrb: float,
    available_rnrb: float
) -> Dict[str, float]:
    """
    Calculate IHT with reduced 36% rate if 10%+ left to charity.

    Process:
    1. Calculate baseline amount (estate after NRBs, before charity)
    2. Check if charity ≥ 10% of baseline
    3. If yes, apply 36% rate instead of 40%

    Formula:
    Baseline = Net Estate - NRB - RNRB
    Charitable % = (Charitable Legacy / Baseline) × 100%

    If Charitable % ≥ 10%:
        Chargeable = Baseline - Charitable Legacy
        IHT = Chargeable × 36%
    Else:
        Chargeable = Baseline - Charitable Legacy
        IHT = Chargeable × 40%

    Example:
    Estate: £1,000,000
    NRB: £325,000
    RNRB: £175,000
    Baseline: £500,000
    Charity: £50,000 (10%)
    Qualifies for 36% rate ✓

    Chargeable: £450,000
    IHT at 36%: £162,000

    vs. Without charity:
    Chargeable: £500,000
    IHT at 40%: £200,000

    Saving: £38,000 (charity £50K but net cost only £12K)
    """
    # Calculate baseline (amount subject to IHT before charity)
    baseline = net_estate - available_nrb - available_rnrb

    if baseline <= 0:
        return {
            "qualifies_for_reduction": False,
            "iht_rate": 0,
            "iht_due": 0,
            "reason": "Estate below nil-rate bands"
        }

    # Calculate charitable percentage
    charitable_percentage = (charitable_legacy / baseline) * 100

    # Check if qualifies (10% threshold)
    qualifies = charitable_percentage >= 10

    # Calculate IHT
    if qualifies:
        rate = IHT_REDUCED_CHARITY_RATE  # 36%
        chargeable = baseline - charitable_legacy
        iht_due = chargeable * rate
    else:
        rate = IHT_STANDARD_RATE  # 40%
        chargeable = baseline - charitable_legacy
        iht_due = chargeable * rate

    # Calculate comparison
    iht_without_charity = baseline * IHT_STANDARD_RATE
    saving = iht_without_charity - (iht_due + (charitable_legacy * IHT_STANDARD_RATE))

    return {
        "baseline_amount": baseline,
        "charitable_legacy": charitable_legacy,
        "charitable_percentage": charitable_percentage,
        "qualifies_for_reduction": qualifies,
        "iht_rate": rate,
        "chargeable_amount": chargeable,
        "iht_due": iht_due,
        "iht_without_charity": iht_without_charity,
        "potential_saving": saving
    }

def optimize_charitable_gift(
    baseline_amount: float
) -> Dict[str, float]:
    """
    Calculate optimal charitable gift to qualify for 36% rate.

    Minimum to qualify: 10% of baseline

    Net cost calculation:
    Charity receives: 10% of baseline
    IHT saved: (Baseline - Charity) × (40% - 36%) = Baseline × 0.4%
    Net cost to estate: Charity - IHT saved

    Example:
    Baseline: £500,000
    Minimum charity: £50,000 (10%)
    IHT saved: £450,000 × 4% = £18,000
    Net cost: £50,000 - £18,000 = £32,000

    Effective cost: 6.4% of baseline to give 10% to charity
    """
    minimum_charitable = baseline_amount * 0.10

    # Calculate IHT with and without charity
    iht_without = baseline_amount * IHT_STANDARD_RATE
    iht_with = (baseline_amount - minimum_charitable) * IHT_REDUCED_CHARITY_RATE

    iht_saved = iht_without - iht_with
    net_cost_to_estate = minimum_charitable - iht_saved

    return {
        "baseline_amount": baseline_amount,
        "minimum_charitable_gift": minimum_charitable,
        "iht_without_charity": iht_without,
        "iht_with_charity": iht_with,
        "iht_saved": iht_saved,
        "charity_receives": minimum_charitable,
        "net_cost_to_estate": net_cost_to_estate,
        "effective_cost_percentage": (net_cost_to_estate / baseline_amount) * 100
    }
```

---

## Quick Succession Relief

### QSR Calculation

```python
def calculate_quick_succession_relief(
    inherited_asset_value: float,
    iht_paid_on_inheritance: float,
    years_between_deaths: float
) -> Dict[str, float]:
    """
    Calculate Quick Succession Relief for assets inherited within 5 years.

    QSR Scale:
    Death within 1 year:    100% relief
    Death within 1-2 years:  80% relief
    Death within 2-3 years:  60% relief
    Death within 3-4 years:  40% relief
    Death within 4-5 years:  20% relief
    Death after 5 years:      0% relief

    Formula:
    QSR = IHT paid on first death × Relief %

    Note: Relief is on tax paid, not asset value
    Asset may have changed value - doesn't matter

    Example:
    Inherited: £500,000
    IHT paid on it: £200,000
    Second death: 3.5 years later
    Relief %: 40%
    QSR: £200,000 × 40% = £80,000

    Second death IHT calculation:
    Asset now worth: £600,000 (increased)
    IHT on it: £240,000
    Less QSR: £80,000
    Net IHT: £160,000
    """
    # Determine relief percentage
    if years_between_deaths < 1:
        relief_percentage = 1.00  # 100%
    elif years_between_deaths < 2:
        relief_percentage = 0.80  # 80%
    elif years_between_deaths < 3:
        relief_percentage = 0.60  # 60%
    elif years_between_deaths < 4:
        relief_percentage = 0.40  # 40%
    elif years_between_deaths < 5:
        relief_percentage = 0.20  # 20%
    else:
        relief_percentage = 0  # No relief

    # Calculate QSR
    qsr_amount = iht_paid_on_inheritance * relief_percentage

    return {
        "inherited_asset_value": inherited_asset_value,
        "iht_paid_on_first_death": iht_paid_on_inheritance,
        "years_between_deaths": years_between_deaths,
        "relief_percentage": relief_percentage,
        "qsr_relief": qsr_amount
    }
```

---

## Advanced Scenarios

### Gift with Reservation (GWR)

```python
def detect_gift_with_reservation(
    gift: Gift,
    benefit_retained: bool,
    market_rent_paid: float = 0
) -> Dict[str, Any]:
    """
    Detect if gift has reservation of benefit.

    GWR occurs when:
    1. Asset gifted to another person, but
    2. Donor retains benefit or enjoyment

    Examples:
    - Gift house but continue living there rent-free
    - Gift shares but retain voting rights
    - Gift property but keep using it

    Consequences:
    - Asset still in estate for IHT
    - Pre-Owned Assets Tax (POAT) may apply during lifetime

    Exceptions (not GWR):
    - Pay full market rent
    - Gift entire property (not shared use)
    - No benefit retained

    Formula:
    If Market Rent Paid ≥ Full Market Rent:
        Not GWR (clean gift)
    Else:
        GWR applies
    """
    if not benefit_retained:
        return {
            "is_gwr": False,
            "reason": "No benefit retained"
        }

    # Check if full market rent paid
    if market_rent_paid >= gift.market_rent_value:
        return {
            "is_gwr": False,
            "reason": "Full market rent paid - clean gift",
            "market_rent_paid": market_rent_paid
        }

    # GWR applies
    return {
        "is_gwr": True,
        "gift_amount": gift.amount,
        "still_in_estate": True,
        "poat_may_apply": True,
        "market_rent_shortfall": gift.market_rent_value - market_rent_paid
    }

def calculate_poat(
    asset_value: float,
    asset_type: str,
    benefit_value: float
) -> Dict[str, float]:
    """
    Calculate Pre-Owned Assets Tax (annual charge).

    POAT rates:
    - Land/property: Official interest rate × (value - consideration paid)
    - Chattels: Official interest rate × value
    - Intangible property: 5% × value

    Current official rate: Varies (check HMRC) - assume 5.75%

    Formula:
    POAT = Value × Rate

    Example:
    Gifted property: £400,000
    No rent paid
    Rate: 5.75%
    Annual POAT: £400,000 × 5.75% = £23,000
    """
    OFFICIAL_RATE = 0.0575  # 5.75% (example - varies)

    rates = {
        "property": OFFICIAL_RATE,
        "chattels": OFFICIAL_RATE,
        "intangible": 0.05
    }

    rate = rates.get(asset_type, OFFICIAL_RATE)
    annual_poat = asset_value * rate

    return {
        "asset_value": asset_value,
        "asset_type": asset_type,
        "poat_rate": rate,
        "annual_poat_charge": annual_poat
    }
```

### Foreign Assets and Domicile

```python
def determine_iht_scope(
    domicile_status: str,
    asset_location: str,
    residence_years: int = 0
) -> Dict[str, Any]:
    """
    Determine IHT scope based on domicile and asset location.

    Rules (current - pre-April 2025):

    UK Domiciled:
    - IHT on worldwide assets
    - No exclusions

    Non-UK Domiciled:
    - IHT on UK assets only
    - Non-UK assets are "excluded property"

    Deemed Domiciled:
    - UK resident 15+ of last 20 years
    - Treated as UK domiciled

    Post-April 2025 (residence-based):
    - 10+ years UK residence: Worldwide IHT exposure
    - "Tail" provisions: 3-year exit period

    Formula:
    If UK Domiciled:
        All assets chargeable
    Elif Deemed Domiciled:
        All assets chargeable
    Else:
        UK assets chargeable
        Non-UK assets excluded
    """
    # Current rules
    if domicile_status == "uk_domiciled":
        return {
            "iht_applies": True,
            "scope": "worldwide",
            "excluded_property": False
        }

    elif domicile_status == "deemed_domiciled" or residence_years >= 15:
        return {
            "iht_applies": True,
            "scope": "worldwide",
            "deemed_domiciled": True,
            "excluded_property": False
        }

    elif domicile_status == "non_uk_domiciled":
        if asset_location == "uk":
            return {
                "iht_applies": True,
                "scope": "uk_assets_only",
                "excluded_property": False
            }
        else:
            return {
                "iht_applies": False,
                "scope": "excluded_property",
                "excluded_property": True
            }

    # Post-2025 residence-based rules
    elif residence_years >= 10:
        return {
            "iht_applies": True,
            "scope": "worldwide",
            "residence_based_rules": True,
            "years_resident": residence_years
        }
```

---

## Compliance Calculations

### Excepted Estate Determination

```python
def check_excepted_estate_eligibility(
    gross_estate: float,
    net_chargeable_estate: float,
    trust_assets: float,
    foreign_assets: float,
    domicile_status: str
) -> Dict[str, Any]:
    """
    Determine if estate qualifies as excepted (no full IHT400 needed).

    Three categories:

    1. Low Value Estate (IHT205):
    - Gross estate < £325,000, OR
    - Net chargeable < NRB after spouse/charity exemptions
    - Trust assets < £150,000
    - Foreign assets < £100,000

    2. Exempt Estate (IHT207):
    - Everything to spouse or charity
    - UK-based assets only
    - No complex trusts

    3. Foreign Domicile (IHT400C):
    - Non-UK domiciled
    - UK assets < £150,000

    Formula:
    If conditions for any category met:
        Return simplified form
    Else:
        Full IHT400 required
    """
    # Check Low Value Estate
    if (gross_estate < 325000 or net_chargeable_estate < 325000) and \
       trust_assets < 150000 and \
       foreign_assets < 100000:
        return {
            "excepted_estate": True,
            "form_required": "IHT205",
            "category": "Low Value Estate"
        }

    # Check Exempt Estate
    if net_chargeable_estate == 0 and foreign_assets == 0:
        return {
            "excepted_estate": True,
            "form_required": "IHT207",
            "category": "Exempt Estate (all to spouse/charity)"
        }

    # Check Foreign Domicile
    if domicile_status == "non_uk_domiciled" and gross_estate < 150000:
        return {
            "excepted_estate": True,
            "form_required": "IHT400C",
            "category": "Foreign Domicile"
        }

    # Full account required
    return {
        "excepted_estate": False,
        "form_required": "IHT400",
        "category": "Full Account Required"
    }
```

### Payment Calculations

```python
def calculate_payment_schedule(
    total_iht: float,
    liquid_assets: float,
    instalment_qualifying_assets: float,
    interest_rate: float = 0.0475
) -> Dict[str, Any]:
    """
    Calculate IHT payment schedule and options.

    Payment rules:
    - IHT due: 6 months after end of month of death
    - Most assets: Pay immediately
    - Qualifying assets: 10 annual instalments

    Instalment-qualifying assets:
    - Land and buildings
    - Business/partnership interests
    - Controlling shareholdings (>50%)
    - Unquoted shares if HMRC agrees

    Interest:
    - Interest-free on qualifying assets (usually property)
    - Interest charged on business assets
    - Late payment interest on all

    Formula:
    Immediate IHT = IHT attributable to non-qualifying assets
    Instalment IHT = IHT attributable to qualifying assets
    Annual Instalment = Instalment IHT / 10
    Total Interest = Sum of interest on declining balance
    """
    # Proportion IHT between asset types
    total_assets = liquid_assets + instalment_qualifying_assets

    immediate_proportion = liquid_assets / total_assets
    instalment_proportion = instalment_qualifying_assets / total_assets

    immediate_iht = total_iht * immediate_proportion
    instalment_iht = total_iht * instalment_proportion

    # Calculate instalment schedule
    annual_instalment = instalment_iht / 10

    # Calculate interest (on declining balance)
    total_interest = 0
    remaining_balance = instalment_iht

    instalment_schedule = []
    for year in range(1, 11):
        interest = remaining_balance * interest_rate
        total_interest += interest

        instalment_schedule.append({
            "year": year,
            "capital": annual_instalment,
            "interest": interest,
            "total_payment": annual_instalment + interest,
            "remaining_balance": remaining_balance - annual_instalment
        })

        remaining_balance -= annual_instalment

    return {
        "total_iht": total_iht,
        "immediate_payment": immediate_iht,
        "instalment_option": instalment_iht,
        "annual_instalment": annual_instalment,
        "total_interest": total_interest,
        "total_cost": total_iht + total_interest,
        "instalment_schedule": instalment_schedule
    }

def identify_dps_eligible_assets(
    assets: List[Asset]
) -> List[Asset]:
    """
    Identify assets eligible for Direct Payment Scheme.

    DPS allows financial institutions to pay IHT directly to HMRC.

    Eligible assets:
    - Bank accounts
    - Building society accounts
    - National Savings
    - Premium Bonds
    - Stocks and shares (some institutions)

    Not eligible:
    - Property
    - Business assets
    - Foreign assets (usually)
    - Private company shares
    """
    dps_types = [
        "bank_account",
        "building_society",
        "national_savings",
        "premium_bonds",
        "quoted_shares"  # If institution participates
    ]

    eligible_assets = [
        asset for asset in assets
        if asset.asset_type in dps_types
    ]

    total_dps_value = sum(asset.value for asset in eligible_assets)

    return {
        "eligible_assets": eligible_assets,
        "total_dps_value": total_dps_value,
        "can_pay_via_dps": total_dps_value > 0
    }
```

---

## Complete IHT Calculation Algorithm

### Master Calculation Function

```python
def calculate_complete_iht(
    estate: Estate,
    gifts: List[Gift],
    trusts: List[Trust],
    date_of_death: date
) -> Dict[str, Any]:
    """
    Master function orchestrating complete IHT calculation.

    Process Flow:
    1. Value gross estate
    2. Deduct liabilities → net estate
    3. Apply spouse/charity exemptions → chargeable estate
    4. Calculate available NRB (with TNRB)
    5. Calculate available RNRB (with TRNRB and taper)
    6. Process lifetime gifts (PETs and CLTs)
    7. Apply business/agricultural reliefs
    8. Calculate charitable rate reduction
    9. Calculate final IHT
    10. Process trust charges
    11. Apply quick succession relief
    12. Generate tax breakdown

    Returns complete calculation with all components.
    """
    # Step 1: Gross estate
    gross_estate = calculate_gross_estate(estate.assets)

    # Step 2: Net estate
    net_estate = calculate_net_estate(gross_estate, estate.liabilities)

    # Step 3: Chargeable estate
    chargeable_estate = calculate_chargeable_estate(
        net_estate,
        estate.spouse_exemption,
        estate.charitable_gifts,
        estate.other_exemptions
    )

    # Step 4: NRB
    available_nrb = calculate_available_nrb(
        STANDARD_NRB,
        estate.tnrb_percentage,
        gifts
    )

    # Step 5: RNRB
    tapered_rnrb = calculate_tapered_rnrb(net_estate, RESIDENCE_NRB)
    available_rnrb = calculate_available_rnrb(
        tapered_rnrb,
        estate.residence_value,
        estate.residence_mortgage
    )

    # Step 6: Process gifts
    gift_tax_total = 0
    for gift in gifts:
        gift_tax = calculate_pet_tax(
            gift.amount,
            gift.date_given,
            date_of_death,
            available_nrb,
            gift.exemptions_applied
        )
        gift_tax_total += gift_tax["tax_due"]

    # Step 7: Business/Agricultural Relief
    br_relief_total = sum(
        calculate_business_relief(
            asset.value,
            asset.business_type,
            asset.ownership_years
        )["relief_amount"]
        for asset in estate.assets
        if asset.asset_type == "business"
    )

    # Step 8: Charitable rate
    charitable_calc = calculate_charitable_rate_reduction(
        net_estate,
        estate.charitable_gifts,
        available_nrb,
        available_rnrb
    )

    # Step 9: Final IHT
    estate_over_nrbs = max(0, chargeable_estate - available_nrb - available_rnrb - br_relief_total)
    estate_iht = estate_over_nrbs * charitable_calc["iht_rate"]

    total_iht = estate_iht + gift_tax_total

    # Step 10: Trust charges
    trust_charges = sum(
        calculate_ten_year_charge(
            trust.value,
            trust.date_created,
            date_of_death,
            STANDARD_NRB,
            STANDARD_NRB,
            0
        )["ten_year_charge"]
        for trust in trusts
    )

    # Step 11: Generate breakdown
    return {
        "gross_estate": gross_estate,
        "net_estate": net_estate,
        "chargeable_estate": chargeable_estate,
        "available_nrb": available_nrb,
        "available_rnrb": available_rnrb,
        "business_relief": br_relief_total,
        "estate_iht": estate_iht,
        "gift_iht": gift_tax_total,
        "trust_charges": trust_charges,
        "total_iht": total_iht,
        "effective_rate": (total_iht / net_estate * 100) if net_estate > 0 else 0,
        "charitable_rate_applied": charitable_calc["qualifies_for_reduction"],
        "detailed_breakdown": {
            "gifts": gifts,
            "reliefs": {
                "nrb": available_nrb,
                "rnrb": available_rnrb,
                "business_relief": br_relief_total
            },
            "charitable": charitable_calc
        }
    }
```

---

## Document Maintenance

### Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-09-30 | Initial documentation created |

### Review Schedule

- **Annual Review**: Each April after Spring Budget
- **Legislative Updates**: When IHT law changes
- **Rate Updates**: When HMRC publishes new rates
- **Next Review**: April 2026 (BR/APR cap implementation)

### Key Future Changes to Monitor

1. **April 2025**: Residence-based scope replaces domicile rules
2. **April 2026**: BR/APR capped at £1M per person
3. **April 2027**: Unused pensions included in IHT estate
4. **April 2030**: End of NRB/RNRB freeze (subject to review)

---

## Disclaimer

This document describes the calculation methodology used in the IHT Calculator application. While every effort has been made to ensure accuracy and compliance with current UK tax law, it should not be construed as professional tax or legal advice.

Users should:
- Consult qualified tax advisers for specific cases
- Verify calculations with HMRC guidance
- Keep updated with tax law changes
- Seek professional valuations for complex assets

Tax legislation is complex and subject to change. The calculations herein are based on the law as at the date stated and may be affected by subsequent legislation or case law.

**Last Updated**: 2025-09-30
**Tax Year**: 2024/25
**Legislation**: Inheritance Tax Act 1984 (as amended)