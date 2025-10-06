"""
UK IHT Calculator - Refactored Implementation
Compliant with 2024/25 tax year rules and upcoming 2025-2027 changes
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Tuple
from datetime import datetime, date
from pydantic import BaseModel, Field
from enum import Enum

from app.database import get_db
from app.models.iht import IHTProfile, Gift, Trust, Asset
from app.api.auth.auth import get_current_user
from app.models.user import User

router = APIRouter()

# UK IHT Constants for 2024/25 tax year
STANDARD_NIL_RATE_BAND = 325000
RESIDENCE_NIL_RATE_BAND = 175000
IHT_RATE = 0.40
REDUCED_CHARITY_RATE = 0.36
RNRB_TAPER_THRESHOLD = 2000000
RNRB_TAPER_RATE = 0.5  # £1 reduction for every £2 over threshold

# Gift exemptions
ANNUAL_EXEMPTION = 3000
SMALL_GIFT_EXEMPTION = 250
WEDDING_GIFT_PARENT = 5000
WEDDING_GIFT_GRANDPARENT = 2500
WEDDING_GIFT_OTHER = 1000

# Future changes tracking
BR_APR_CAP_DATE = date(2026, 4, 6)
BR_APR_CAP_AMOUNT = 1000000
PENSION_IHT_DATE = date(2027, 4, 6)

class GiftType(str, Enum):
    PET = "pet"  # Potentially Exempt Transfer
    CLT = "clt"  # Chargeable Lifetime Transfer
    EXEMPT = "exempt"

class AssetType(str, Enum):
    PROPERTY = "property"
    BUSINESS = "business"
    AGRICULTURAL = "agricultural"
    INVESTMENT = "investment"
    PERSONAL = "personal"
    PENSION = "pension"

class BusinessReliefType(str, Enum):
    UNQUOTED_SHARES = "unquoted_shares"  # 100% relief
    AIM_SHARES = "aim_shares"  # 100% relief
    QUOTED_CONTROLLING = "quoted_controlling"  # 50% relief
    BUSINESS_ASSETS = "business_assets"  # 50% relief
    NONE = "none"

class AssetInput(BaseModel):
    asset_type: AssetType
    value: float
    description: Optional[str] = None
    is_main_residence: bool = False
    business_relief_type: Optional[BusinessReliefType] = None
    ownership_years: float = 0
    is_excepted_asset: bool = False

class GiftInput(BaseModel):
    recipient: str
    recipient_relationship: str
    amount: float
    date_given: date
    gift_type: GiftType = GiftType.PET
    is_to_trust: bool = False
    exemption_claimed: Optional[str] = None
    with_reservation: bool = False

class TrustInput(BaseModel):
    trust_name: str
    trust_type: str
    value: float
    date_created: date
    is_relevant_property: bool = True
    beneficiaries: List[str] = []

class IHTCalculationRequest(BaseModel):
    assets: List[AssetInput]
    gifts: List[GiftInput]
    trusts: List[TrustInput]
    marital_status: str
    residence_value: float
    charitable_gifts: float = 0
    tnrb_claimed_percentage: float = 0  # 0-100% of deceased spouse's unused NRB
    trnrb_claimed_percentage: float = 0  # 0-100% of deceased spouse's unused RNRB
    has_direct_descendants: bool = True
    annual_exemption_used_current: float = 0
    annual_exemption_used_previous: float = 0

class EnhancedIHTResponse(BaseModel):
    # Estate values
    total_estate_value: float
    net_estate_value: float

    # Nil-rate bands
    nil_rate_band: float
    tnrb_amount: float  # Transferred NRB
    total_nil_rate_band: float
    residence_nil_rate_band: float
    trnrb_amount: float  # Transferred RNRB
    rnrb_taper_amount: float

    # Tax calculation
    taxable_estate: float
    iht_due: float
    effective_rate: float
    applicable_rate: float  # 40% or 36% if charitable

    # Reliefs
    business_property_relief: float
    agricultural_property_relief: float
    charitable_exemption: float
    charity_rate_applied: bool
    baseline_amount: float  # For charity calculation

    # Gifts
    pets_total: float
    clts_total: float
    failed_pets_tax: float
    taper_relief_on_tax: float  # Correctly applied to tax, not gift value
    gift_exemptions_used: Dict[str, float]

    # Warnings
    warnings: List[str]
    future_changes: List[str]

def calculate_taper_relief_on_tax(gift_date: date, tax_amount: float) -> float:
    """
    Calculate taper relief on the TAX due, not the gift amount
    This is a critical fix from the original implementation
    """
    years_since_gift = (datetime.now().date() - gift_date).days / 365.25

    if years_since_gift < 3:
        return 0  # No taper relief
    elif years_since_gift >= 7:
        return tax_amount  # Full relief (gift is exempt)
    else:
        # Taper relief percentages on TAX based on complete years
        if years_since_gift >= 6:
            relief_rate = 0.80  # 80% relief on tax (6-7 years)
        elif years_since_gift >= 5:
            relief_rate = 0.60  # 60% relief on tax (5-6 years)
        elif years_since_gift >= 4:
            relief_rate = 0.40  # 40% relief on tax (4-5 years)
        else:  # years_since_gift >= 3
            relief_rate = 0.20  # 20% relief on tax (3-4 years)

        return tax_amount * relief_rate

def calculate_business_relief(assets: List[AssetInput]) -> Tuple[float, List[str]]:
    """
    Calculate business property relief with correct rates
    100% for unquoted/AIM shares, 50% for quoted controlling shares
    """
    total_relief = 0
    warnings = []

    for asset in assets:
        if asset.asset_type != AssetType.BUSINESS:
            continue

        # Check 2-year ownership rule
        if asset.ownership_years < 2:
            warnings.append(f"Business asset '{asset.description}' not owned for 2+ years - no relief")
            continue

        # Check for excepted assets
        if asset.is_excepted_asset:
            warnings.append(f"Asset '{asset.description}' is an excepted asset - no relief")
            continue

        # Apply correct relief rates
        if asset.business_relief_type in [BusinessReliefType.UNQUOTED_SHARES, BusinessReliefType.AIM_SHARES]:
            total_relief += asset.value * 1.0  # 100% relief
        elif asset.business_relief_type in [BusinessReliefType.QUOTED_CONTROLLING, BusinessReliefType.BUSINESS_ASSETS]:
            total_relief += asset.value * 0.5  # 50% relief

    # Check for future BR cap
    if datetime.now().date() >= BR_APR_CAP_DATE and total_relief > BR_APR_CAP_AMOUNT:
        warnings.append(f"Business Relief capped at £{BR_APR_CAP_AMOUNT:,.0f} from April 2026")
        total_relief = min(total_relief, BR_APR_CAP_AMOUNT)

    return total_relief, warnings

def calculate_rnrb_with_taper(estate_value: float, residence_value: float,
                              has_descendants: bool, trnrb_percentage: float) -> Tuple[float, float]:
    """
    Calculate RNRB with correct tapering formula
    Reduces by £1 for every £2 over £2m (not 0.5 multiplication)
    """
    if not has_descendants or residence_value <= 0:
        return 0, 0

    # Base RNRB
    base_rnrb = min(RESIDENCE_NIL_RATE_BAND, residence_value)

    # Add transferred RNRB from deceased spouse
    transferred_rnrb = RESIDENCE_NIL_RATE_BAND * (trnrb_percentage / 100)
    total_rnrb = base_rnrb + transferred_rnrb

    # Apply taper if estate exceeds £2m
    taper_amount = 0
    if estate_value > RNRB_TAPER_THRESHOLD:
        # CORRECT: Reduce by £1 for every £2 over threshold
        excess = estate_value - RNRB_TAPER_THRESHOLD
        taper_amount = excess / 2  # This is the fix
        total_rnrb = max(0, total_rnrb - taper_amount)

    return total_rnrb, taper_amount

def calculate_charitable_rate(estate_value: float, charitable_gifts: float,
                              nil_rate_band: float, rnrb: float) -> Tuple[float, float, bool]:
    """
    Calculate if estate qualifies for 36% reduced rate
    Must leave 10% of baseline amount to charity
    """
    # Calculate baseline amount (estate minus NRB and RNRB)
    baseline_amount = max(0, estate_value - nil_rate_band - rnrb)

    # Check if charitable giving is 10% or more of baseline
    if baseline_amount > 0:
        charity_percentage = charitable_gifts / baseline_amount
        if charity_percentage >= 0.10:
            return REDUCED_CHARITY_RATE, baseline_amount, True

    return IHT_RATE, baseline_amount, False

def process_gifts_with_exemptions(gifts: List[GiftInput],
                                  annual_exemption_current: float,
                                  annual_exemption_previous: float) -> Dict:
    """
    Process gifts with proper exemption application and PET/CLT distinction
    """
    pets = []
    clts = []
    exempt_gifts = []
    exemptions_used = {
        "annual_current": 0,
        "annual_previous": 0,
        "small_gifts": 0,
        "wedding_gifts": 0,
        "normal_expenditure": 0
    }

    # Available annual exemptions
    available_current = ANNUAL_EXEMPTION - annual_exemption_current
    available_previous = ANNUAL_EXEMPTION - annual_exemption_previous

    for gift in gifts:
        gift_amount = gift.amount

        # Apply exemptions if claimed
        if gift.exemption_claimed == "annual":
            # Use current year first, then previous year
            if available_current > 0:
                exemption = min(gift_amount, available_current)
                available_current -= exemption
                gift_amount -= exemption
                exemptions_used["annual_current"] += exemption

            if gift_amount > 0 and available_previous > 0:
                exemption = min(gift_amount, available_previous)
                available_previous -= exemption
                gift_amount -= exemption
                exemptions_used["annual_previous"] += exemption

        elif gift.exemption_claimed == "small_gift":
            if gift.amount <= SMALL_GIFT_EXEMPTION:
                exemptions_used["small_gifts"] += gift.amount
                gift_amount = 0

        elif gift.exemption_claimed == "wedding":
            # Apply wedding gift exemptions based on relationship
            # Check grandparent first since it contains "parent"
            if "grandparent" in gift.recipient_relationship.lower():
                max_exemption = WEDDING_GIFT_GRANDPARENT
            elif "parent" in gift.recipient_relationship.lower():
                max_exemption = WEDDING_GIFT_PARENT
            else:
                max_exemption = WEDDING_GIFT_OTHER

            exemption = min(gift_amount, max_exemption)
            gift_amount -= exemption
            exemptions_used["wedding_gifts"] += exemption

        # Categorize remaining gift amount
        if gift_amount > 0:
            gift_data = {
                "amount": gift_amount,
                "original_amount": gift.amount,
                "date": gift.date_given,
                "recipient": gift.recipient,
                "with_reservation": gift.with_reservation
            }

            if gift.gift_type == GiftType.CLT or gift.is_to_trust:
                clts.append(gift_data)
            elif gift.gift_type == GiftType.PET:
                pets.append(gift_data)
        else:
            exempt_gifts.append(gift)

    return {
        "pets": pets,
        "clts": clts,
        "exempt_gifts": exempt_gifts,
        "exemptions_used": exemptions_used
    }

@router.post("/calculate-enhanced", response_model=EnhancedIHTResponse)
def calculate_iht_enhanced(
    request: IHTCalculationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Enhanced IHT calculation with all critical fixes:
    1. Taper relief applied to tax, not gift amount
    2. Correct business relief rates (100% vs 50%)
    3. Fixed RNRB taper calculation
    4. TNRB percentage-based transfer
    5. Charitable rate reduction
    6. PET vs CLT distinction
    """

    warnings = []
    future_changes = []

    # Calculate total estate value
    total_estate_value = sum(asset.value for asset in request.assets)
    net_estate_value = total_estate_value  # Could subtract liabilities here

    # Calculate nil-rate bands with TNRB
    base_nrb = STANDARD_NIL_RATE_BAND
    tnrb_amount = STANDARD_NIL_RATE_BAND * (request.tnrb_claimed_percentage / 100)
    total_nil_rate_band = base_nrb + tnrb_amount

    # Calculate RNRB with correct tapering
    rnrb, rnrb_taper = calculate_rnrb_with_taper(
        total_estate_value,
        request.residence_value,
        request.has_direct_descendants,
        request.trnrb_claimed_percentage
    )

    # Calculate business and agricultural relief
    business_relief, br_warnings = calculate_business_relief(request.assets)
    warnings.extend(br_warnings)

    agricultural_relief = sum(
        asset.value for asset in request.assets
        if asset.asset_type == AssetType.AGRICULTURAL
    )

    # Check for future BR/APR cap
    if datetime.now().date() >= BR_APR_CAP_DATE:
        total_br_apr = business_relief + agricultural_relief
        if total_br_apr > BR_APR_CAP_AMOUNT:
            future_changes.append(f"BR/APR capped at £{BR_APR_CAP_AMOUNT:,.0f} from April 2026")

    # Calculate charitable rate
    iht_rate, baseline_amount, charity_rate_applied = calculate_charitable_rate(
        total_estate_value,
        request.charitable_gifts,
        total_nil_rate_band,
        rnrb
    )

    # Process gifts with exemptions
    gift_results = process_gifts_with_exemptions(
        request.gifts,
        request.annual_exemption_used_current,
        request.annual_exemption_used_previous
    )

    pets_total = sum(g["amount"] for g in gift_results["pets"])
    clts_total = sum(g["amount"] for g in gift_results["clts"])

    # Calculate failed PETs tax (gifts within 7 years)
    failed_pets_tax = 0
    taper_relief_total = 0

    for pet in gift_results["pets"]:
        years_since = (datetime.now().date() - pet["date"]).days / 365.25
        if years_since < 7:
            # Gift uses NRB first
            if pet["amount"] > total_nil_rate_band:
                taxable_amount = pet["amount"] - total_nil_rate_band
                tax_due = taxable_amount * IHT_RATE

                # Apply taper relief to the TAX (not the gift amount)
                taper_relief = calculate_taper_relief_on_tax(pet["date"], tax_due)
                taper_relief_total += taper_relief
                failed_pets_tax += (tax_due - taper_relief)

                if pet["with_reservation"]:
                    warnings.append(f"Gift to {pet['recipient']} may be subject to GWR rules")

    # Calculate taxable estate
    taxable_estate = max(0,
        total_estate_value
        - total_nil_rate_band
        - rnrb
        - request.charitable_gifts
        - business_relief
        - agricultural_relief
    )

    # Calculate IHT due
    iht_due = (taxable_estate * iht_rate) + failed_pets_tax
    iht_due = max(0, iht_due)

    # Calculate effective rate
    effective_rate = (iht_due / total_estate_value * 100) if total_estate_value > 0 else 0

    # Add warnings for future changes
    if datetime.now().date() < BR_APR_CAP_DATE:
        future_changes.append("From April 2026: BR/APR will be capped at £1m combined")
    if datetime.now().date() < PENSION_IHT_DATE:
        future_changes.append("From April 2027: Unused pension funds will be subject to IHT")

    # Check for CLTs that need immediate tax
    for clt in gift_results["clts"]:
        if clt["amount"] > total_nil_rate_band:
            warnings.append(f"CLT to {clt['recipient']} may trigger 20% lifetime charge")

    return EnhancedIHTResponse(
        total_estate_value=total_estate_value,
        net_estate_value=net_estate_value,
        nil_rate_band=base_nrb,
        tnrb_amount=tnrb_amount,
        total_nil_rate_band=total_nil_rate_band,
        residence_nil_rate_band=rnrb,
        trnrb_amount=request.trnrb_claimed_percentage * RESIDENCE_NIL_RATE_BAND / 100,
        rnrb_taper_amount=rnrb_taper,
        taxable_estate=taxable_estate,
        iht_due=iht_due,
        effective_rate=effective_rate,
        applicable_rate=iht_rate,
        business_property_relief=business_relief,
        agricultural_property_relief=agricultural_relief,
        charitable_exemption=request.charitable_gifts,
        charity_rate_applied=charity_rate_applied,
        baseline_amount=baseline_amount,
        pets_total=pets_total,
        clts_total=clts_total,
        failed_pets_tax=failed_pets_tax,
        taper_relief_on_tax=taper_relief_total,
        gift_exemptions_used=gift_results["exemptions_used"],
        warnings=warnings,
        future_changes=future_changes
    )

@router.post("/gift/validate")
def validate_gift_exemption(
    gift: GiftInput,
    annual_exemption_remaining: float,
    current_user: User = Depends(get_current_user)
):
    """
    Validate if a gift qualifies for exemptions
    """
    eligible_exemptions = []

    # Check annual exemption
    if annual_exemption_remaining > 0:
        eligible_exemptions.append({
            "type": "annual",
            "max_amount": min(gift.amount, annual_exemption_remaining),
            "description": f"Annual exemption (£{annual_exemption_remaining:,.0f} available)"
        })

    # Check small gift exemption
    if gift.amount <= SMALL_GIFT_EXEMPTION:
        eligible_exemptions.append({
            "type": "small_gift",
            "max_amount": gift.amount,
            "description": f"Small gift exemption (max £{SMALL_GIFT_EXEMPTION})"
        })

    # Check wedding gift exemptions
    if "wedding" in gift.recipient.lower() or "marriage" in gift.recipient.lower():
        if "parent" in gift.recipient_relationship.lower():
            max_amount = WEDDING_GIFT_PARENT
        elif "grandparent" in gift.recipient_relationship.lower():
            max_amount = WEDDING_GIFT_GRANDPARENT
        else:
            max_amount = WEDDING_GIFT_OTHER

        eligible_exemptions.append({
            "type": "wedding",
            "max_amount": min(gift.amount, max_amount),
            "description": f"Wedding gift exemption (max £{max_amount:,.0f})"
        })

    return {
        "gift_amount": gift.amount,
        "eligible_exemptions": eligible_exemptions,
        "is_pet": not gift.is_to_trust,
        "is_clt": gift.is_to_trust
    }

@router.post("/trust/ten-year-charge")
def calculate_ten_year_charge(
    trust_value: float,
    cumulative_clts: float,
    current_user: User = Depends(get_current_user)
):
    """
    Calculate 10-year periodic charge for relevant property trusts
    Maximum effective rate is 6%
    """
    # Available nil-rate band
    available_nrb = max(0, STANDARD_NIL_RATE_BAND - cumulative_clts)

    # Taxable amount
    taxable_amount = max(0, trust_value - available_nrb)

    if taxable_amount == 0:
        return {
            "trust_value": trust_value,
            "taxable_amount": 0,
            "ten_year_charge": 0,
            "effective_rate": 0,
            "message": "No charge - trust value within available NRB"
        }

    # Calculate notional tax at 20% lifetime rate
    notional_tax = taxable_amount * 0.20

    # Effective rate (30% of lifetime rate = 6% max)
    effective_rate = (notional_tax / trust_value) * 0.30
    effective_rate = min(effective_rate, 0.06)  # Cap at 6%

    ten_year_charge = trust_value * effective_rate

    return {
        "trust_value": trust_value,
        "available_nrb": available_nrb,
        "taxable_amount": taxable_amount,
        "ten_year_charge": ten_year_charge,
        "effective_rate": effective_rate * 100,
        "message": f"10-year charge at effective rate of {effective_rate*100:.2f}%"
    }

@router.post("/trust/exit-charge")
def calculate_exit_charge(
    distribution_amount: float,
    last_ten_year_rate: float,
    quarters_since_charge: int,
    current_user: User = Depends(get_current_user)
):
    """
    Calculate exit charge for distributions from relevant property trusts
    Pro-rated based on complete quarters since last 10-year charge
    """
    # Maximum 40 quarters in 10 years
    quarters_since_charge = min(quarters_since_charge, 40)

    # Pro-rate the last 10-year rate
    exit_rate = (last_ten_year_rate / 100) * (quarters_since_charge / 40)

    exit_charge = distribution_amount * exit_rate

    return {
        "distribution_amount": distribution_amount,
        "last_ten_year_rate": last_ten_year_rate,
        "quarters_since_charge": quarters_since_charge,
        "exit_rate": exit_rate * 100,
        "exit_charge": exit_charge,
        "message": f"Exit charge at {exit_rate*100:.2f}% ({quarters_since_charge}/40 quarters)"
    }

@router.get("/excepted-estate/check")
def check_excepted_estate_eligibility(
    estate_value: float,
    iht_due: float,
    foreign_assets: float = 0,
    trust_interests: bool = False,
    current_user: User = Depends(get_current_user)
):
    """
    Check if estate qualifies as excepted (simpler IHT205 instead of IHT400)
    """
    # Excepted estate thresholds for 2024/25
    EXCEPTED_ESTATE_LIMIT = 650000  # Including transferred NRB
    FOREIGN_ASSET_LIMIT = 100000

    reasons_fail = []

    # Check basic threshold
    if estate_value > EXCEPTED_ESTATE_LIMIT:
        reasons_fail.append(f"Estate value £{estate_value:,.0f} exceeds £{EXCEPTED_ESTATE_LIMIT:,.0f} limit")

    # Check IHT due
    if iht_due > 0:
        reasons_fail.append(f"IHT due of £{iht_due:,.0f} (excepted estates have no IHT)")

    # Check foreign assets
    if foreign_assets > FOREIGN_ASSET_LIMIT:
        reasons_fail.append(f"Foreign assets £{foreign_assets:,.0f} exceed £{FOREIGN_ASSET_LIMIT:,.0f} limit")

    # Check trust interests
    if trust_interests:
        reasons_fail.append("Estate includes trust interests")

    is_excepted = len(reasons_fail) == 0

    return {
        "is_excepted": is_excepted,
        "form_required": "IHT205" if is_excepted else "IHT400",
        "reasons_fail": reasons_fail,
        "message": "Excepted estate - use simplified IHT205" if is_excepted else "Full IHT400 required"
    }

@router.post("/quick-succession-relief")
def calculate_quick_succession_relief(
    first_death_date: date,
    second_death_date: date,
    tax_paid_first_death: float,
    increase_in_estate: float,
    current_user: User = Depends(get_current_user)
):
    """
    Calculate Quick Succession Relief (QSR) for estates inheriting from someone
    who died within 5 years
    """
    # Calculate years between deaths
    years_between = (second_death_date - first_death_date).days / 365.25

    if years_between > 5:
        return {
            "years_between": years_between,
            "relief_percentage": 0,
            "relief_amount": 0,
            "message": "No QSR - more than 5 years between deaths"
        }

    # QSR percentages based on years
    qsr_rates = {
        0: 100,  # Within 1 year
        1: 80,   # 1-2 years
        2: 60,   # 2-3 years
        3: 40,   # 3-4 years
        4: 20,   # 4-5 years
    }

    years_bracket = int(years_between)
    relief_percentage = qsr_rates.get(years_bracket, 0)

    # Relief is percentage of tax attributable to the increased value
    relief_amount = (tax_paid_first_death * increase_in_estate / 100) * (relief_percentage / 100)

    return {
        "years_between": years_between,
        "relief_percentage": relief_percentage,
        "relief_amount": relief_amount,
        "tax_paid_first_death": tax_paid_first_death,
        "increase_in_estate": increase_in_estate,
        "message": f"QSR at {relief_percentage}% - {years_bracket}-{years_bracket+1} years between deaths"
    }

@router.get("/forms/iht400-data")
def generate_iht400_data(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate data structure for IHT400 form pre-population
    """
    # Get user's IHT profile
    profile = db.query(IHTProfile).filter(IHTProfile.user_id == current_user.id).first()

    if not profile:
        raise HTTPException(status_code=404, detail="No IHT profile found")

    # Get related data
    assets = db.query(Asset).filter(Asset.iht_profile_id == profile.id).all()
    gifts = db.query(Gift).filter(Gift.iht_profile_id == profile.id).all()
    trusts = db.query(Trust).filter(Trust.iht_profile_id == profile.id).all()

    # Structure data for IHT400
    iht400_data = {
        "main_form": {
            "deceased_details": {
                "name": current_user.full_name,
                "date_of_death": datetime.now().date().isoformat(),
            },
            "estate_in_uk": {
                "assets_total": sum(a.value for a in assets),
                "gifts_total": sum(g.amount for g in gifts),
                "trusts_total": sum(t.value for t in trusts),
            },
            "exemptions_and_reliefs": {
                "spouse_exemption": 0,  # Would need spouse details
                "charity_exemption": profile.charitable_gifts,
                "business_relief": sum(a.value for a in assets if a.qualifies_for_bpr),
                "agricultural_relief": sum(a.value for a in assets if a.qualifies_for_apr),
            }
        },
        "schedules_required": [],
        "supporting_documents": []
    }

    # Determine required schedules
    if any(a.asset_type == "property" for a in assets):
        iht400_data["schedules_required"].append("IHT405 - Houses and land")

    if gifts:
        iht400_data["schedules_required"].append("IHT403 - Gifts")

    if trusts:
        iht400_data["schedules_required"].append("IHT418 - Trusts")

    if any(a.qualifies_for_bpr for a in assets):
        iht400_data["schedules_required"].append("IHT413 - Business relief")

    return iht400_data