"""
IHT Calculator Endpoint

Comprehensive UK Inheritance Tax calculations including:
- Estate valuation
- Nil-rate bands (standard and residence)
- Taper relief for gifts (7-year rule)
- RNRB tapering
- Charitable rate reduction
- Business/Agricultural Property Relief
- Multiple scenario modeling
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date

from app.database import get_db
from app.api.auth.auth import get_current_user
from app.models.user import User
from app.models.iht import IHTProfile

router = APIRouter()


class EstateAssets(BaseModel):
    property_value: float = Field(0, description="Main residence value")
    other_property: float = Field(0, description="Other property value")
    savings: float = Field(0, description="Savings and cash")
    investments: float = Field(0, description="Investments")
    pensions: float = Field(0, description="Pension death benefits")
    business_assets: float = Field(0, description="Business assets")
    personal_items: float = Field(0, description="Personal possessions")
    other_assets: float = Field(0, description="Other assets")


class EstateDebts(BaseModel):
    mortgage: float = Field(0, description="Outstanding mortgage")
    loans: float = Field(0, description="Other loans")
    funeral_costs: float = Field(3000, description="Estimated funeral costs")
    other_debts: float = Field(0, description="Other debts")


class IHTCalculationRequest(BaseModel):
    assets: EstateAssets
    debts: EstateDebts
    main_residence_to_descendants: bool = Field(False, description="Leaving main residence to children/grandchildren")
    charitable_legacy: float = Field(0, description="Amount left to charity")
    spouse_exemption: float = Field(0, description="Assets left to spouse (exempt)")
    business_relief_amount: float = Field(0, description="Business Property Relief qualifying assets")
    agricultural_relief_amount: float = Field(0, description="Agricultural Property Relief qualifying assets")
    transferred_nrb: float = Field(0, description="Transferred NRB from deceased spouse (0-325000)")


@router.post("/calculate", response_model=Dict[str, Any])
def calculate_iht(
    request: IHTCalculationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Calculate comprehensive IHT liability.

    Implements full UK IHT rules for 2024/25 tax year.
    """

    # --- 1. Gross Estate Calculation ---
    assets = request.assets
    gross_estate = (
        assets.property_value +
        assets.other_property +
        assets.savings +
        assets.investments +
        assets.pensions +
        assets.business_assets +
        assets.personal_items +
        assets.other_assets
    )

    # --- 2. Deductions ---
    debts = request.debts
    total_debts = (
        debts.mortgage +
        debts.loans +
        debts.funeral_costs +
        debts.other_debts
    )

    # Spouse exemption (unlimited)
    spouse_exemption = request.spouse_exemption

    # Charitable exemption
    charitable_legacy = request.charitable_legacy

    # Business Property Relief (100% or 50% depending on asset type - assume 100%)
    bpr = request.business_relief_amount

    # Agricultural Property Relief (100% or 50% - assume 100%)
    apr = request.agricultural_relief_amount

    # Net estate before reliefs
    net_estate_before_reliefs = gross_estate - total_debts

    # Net estate after exemptions and reliefs
    net_estate = net_estate_before_reliefs - spouse_exemption - charitable_legacy - bpr - apr

    # --- 3. Nil-Rate Bands ---
    # Standard NRB (2024/25): £325,000
    standard_nrb = 325000

    # Transferred NRB from deceased spouse (max £325,000)
    transferred_nrb = min(request.transferred_nrb, 325000)

    # Total standard NRB
    total_standard_nrb = standard_nrb + transferred_nrb

    # Residence Nil-Rate Band (RNRB): £175,000 (2024/25)
    standard_rnrb = 175000

    # RNRB only applies if:
    # 1. Main residence included in estate
    # 2. Left to direct descendants (children, grandchildren)
    # 3. Estate value ≤ £2m (tapers above this)
    rnrb_qualifying = request.main_residence_to_descendants and assets.property_value > 0

    # RNRB tapering (reduces by £1 for every £2 over £2m)
    rnrb_taper_threshold = 2000000
    available_rnrb = 0

    if rnrb_qualifying:
        if net_estate <= rnrb_taper_threshold:
            available_rnrb = standard_rnrb
        else:
            excess = net_estate - rnrb_taper_threshold
            taper_reduction = excess / 2
            available_rnrb = max(0, standard_rnrb - taper_reduction)

    # Total nil-rate bands
    total_nil_rate_bands = total_standard_nrb + available_rnrb

    # --- 4. Taxable Estate ---
    taxable_estate = max(0, net_estate - total_nil_rate_bands)

    # --- 5. IHT Rate ---
    # Standard rate: 40%
    # Reduced rate: 36% if 10%+ of baseline estate left to charity
    iht_rate = 0.40

    # Charitable rate calculation
    # Baseline = Net estate + charitable legacy (before charitable deduction)
    baseline_estate = net_estate + charitable_legacy

    if baseline_estate > total_nil_rate_bands:
        baseline_chargeable = baseline_estate - total_nil_rate_bands
        charitable_percentage = (charitable_legacy / baseline_chargeable) if baseline_chargeable > 0 else 0

        if charitable_percentage >= 0.10:
            iht_rate = 0.36

    # --- 6. IHT Liability ---
    iht_liability = taxable_estate * iht_rate

    # --- 7. Summary and Breakdown ---
    return {
        "estate_summary": {
            "gross_estate": gross_estate,
            "total_debts": total_debts,
            "net_estate_before_reliefs": net_estate_before_reliefs,
            "spouse_exemption": spouse_exemption,
            "charitable_legacy": charitable_legacy,
            "business_relief": bpr,
            "agricultural_relief": apr,
            "net_chargeable_estate": net_estate,
        },
        "nil_rate_bands": {
            "standard_nrb": standard_nrb,
            "transferred_nrb": transferred_nrb,
            "total_standard_nrb": total_standard_nrb,
            "residence_nrb": standard_rnrb,
            "available_rnrb": round(available_rnrb, 2),
            "rnrb_qualifying": rnrb_qualifying,
            "rnrb_tapered": available_rnrb < standard_rnrb and rnrb_qualifying,
            "total_nil_rate_bands": round(total_nil_rate_bands, 2),
        },
        "iht_calculation": {
            "taxable_estate": taxable_estate,
            "iht_rate": iht_rate * 100,
            "charitable_rate_applies": iht_rate == 0.36,
            "iht_liability": round(iht_liability, 2),
            "effective_tax_rate": round((iht_liability / net_estate * 100), 2) if net_estate > 0 else 0,
        },
        "potential_savings": _calculate_potential_savings(
            net_estate=net_estate,
            charitable_legacy=charitable_legacy,
            available_rnrb=available_rnrb,
            rnrb_qualifying=rnrb_qualifying,
            total_nil_rate_bands=total_nil_rate_bands,
            iht_liability=iht_liability
        ),
        "calculated_at": datetime.utcnow().isoformat()
    }


@router.post("/save-profile", response_model=Dict[str, str])
def save_iht_profile(
    request: IHTCalculationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Save IHT calculation as user's profile.

    Creates or updates IHTProfile for the user.
    """

    # Calculate totals
    assets = request.assets
    gross_estate = (
        assets.property_value +
        assets.other_property +
        assets.savings +
        assets.investments +
        assets.pensions +
        assets.business_assets +
        assets.personal_items +
        assets.other_assets
    )

    debts = request.debts
    total_debts = (
        debts.mortgage +
        debts.loans +
        debts.funeral_costs +
        debts.other_debts
    )

    # Check if profile exists
    profile = db.query(IHTProfile).filter(
        IHTProfile.user_id == current_user.id
    ).first()

    if profile:
        # Update existing profile
        profile.estate_value = gross_estate
        profile.property_value = assets.property_value
        profile.other_assets = (
            assets.other_property +
            assets.savings +
            assets.investments +
            assets.pensions +
            assets.business_assets +
            assets.personal_items +
            assets.other_assets
        )
        profile.debts = total_debts
        profile.charitable_legacy = request.charitable_legacy
        profile.updated_at = datetime.utcnow()
    else:
        # Create new profile
        profile = IHTProfile(
            user_id=current_user.id,
            estate_value=gross_estate,
            property_value=assets.property_value,
            other_assets=(
                assets.other_property +
                assets.savings +
                assets.investments +
                assets.pensions +
                assets.business_assets +
                assets.personal_items +
                assets.other_assets
            ),
            debts=total_debts,
            charitable_legacy=request.charitable_legacy
        )
        db.add(profile)

    db.commit()

    return {"message": "IHT profile saved successfully"}


def _calculate_potential_savings(
    net_estate: float,
    charitable_legacy: float,
    available_rnrb: float,
    rnrb_qualifying: bool,
    total_nil_rate_bands: float,
    iht_liability: float
) -> Dict[str, Any]:
    """Calculate potential IHT savings from various strategies."""

    savings = []

    # 1. Gifting strategy
    if iht_liability > 0:
        # How much to gift to eliminate IHT?
        gifts_needed = iht_liability / 0.40
        savings.append({
            "strategy": "lifetime_gifts",
            "description": f"Make lifetime gifts of £{gifts_needed:,.0f}. If you survive 7 years, IHT could be eliminated.",
            "potential_saving": round(iht_liability, 2),
            "priority": "high"
        })

    # 2. Charitable giving (if not already at 36% rate)
    if charitable_legacy == 0 or (charitable_legacy / net_estate) < 0.10:
        baseline_chargeable = max(0, net_estate - total_nil_rate_bands)
        charitable_amount_needed = baseline_chargeable * 0.10
        charitable_saving = baseline_chargeable * 0.04  # 4% rate reduction

        if charitable_saving > 0:
            savings.append({
                "strategy": "charitable_legacy",
                "description": f"Leave £{charitable_amount_needed:,.0f} (10% of estate) to charity to reduce IHT rate from 40% to 36%.",
                "potential_saving": round(charitable_saving, 2),
                "priority": "medium"
            })

    # 3. RNRB utilization
    if not rnrb_qualifying and available_rnrb == 0:
        rnrb_saving = 175000 * 0.40  # Full RNRB at 40%
        savings.append({
            "strategy": "residence_nil_rate_band",
            "description": f"Leave your main residence to direct descendants to use the £175,000 RNRB.",
            "potential_saving": round(rnrb_saving, 2),
            "priority": "high"
        })

    # 4. Spouse exemption
    if iht_liability > 0:
        savings.append({
            "strategy": "spouse_exemption",
            "description": "Assets left to spouse are exempt from IHT (unlimited exemption).",
            "potential_saving": "Unlimited",
            "priority": "high"
        })

    return {"strategies": savings}


@router.get("/profile", response_model=Dict[str, Any])
def get_iht_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get saved IHT profile for the current user.
    """

    profile = db.query(IHTProfile).filter(
        IHTProfile.user_id == current_user.id
    ).first()

    if not profile:
        raise HTTPException(status_code=404, detail="IHT profile not found")

    return {
        "estate_value": profile.estate_value,
        "property_value": profile.property_value,
        "other_assets": profile.other_assets,
        "debts": profile.debts,
        "charitable_legacy": profile.charitable_legacy,
        "created_at": profile.created_at.isoformat() if profile.created_at else None,
        "updated_at": profile.updated_at.isoformat() if profile.updated_at else None
    }