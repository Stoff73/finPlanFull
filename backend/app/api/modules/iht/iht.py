"""
IHT Planning Module API Router

Provides dashboard and summary endpoints for the IHT Planning module.
Aggregates estate data, IHT calculations, gifts, and planning recommendations.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any, List
from datetime import datetime, timedelta

from app.database import get_db
from app.api.auth.auth import get_current_user
from app.models.user import User
from app.models.iht import IHTProfile, Gift, Trust

router = APIRouter()


@router.get("/dashboard", response_model=Dict[str, Any])
def get_iht_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive IHT planning dashboard data for the current user.

    Returns:
    - Estate valuation
    - IHT liability calculation
    - Nil-rate bands utilization
    - Gift tracking (7-year rule)
    - Trust summary
    - Planning recommendations
    """

    # Get IHT profile
    iht_profile = db.query(IHTProfile).filter(
        IHTProfile.user_id == current_user.id
    ).first()

    # Get all gifts (linked to IHT profile)
    if iht_profile:
        gifts = db.query(Gift).filter(
            Gift.iht_profile_id == iht_profile.id
        ).all()

        # Get all trusts (linked to IHT profile)
        trusts = db.query(Trust).filter(
            Trust.iht_profile_id == iht_profile.id
        ).all()
    else:
        gifts = []
        trusts = []

    # --- Estate Valuation ---
    if iht_profile:
        estate_value = (iht_profile.estate_value or 0)
        liabilities = (iht_profile.liabilities or 0)
        net_estate = (iht_profile.net_estate or estate_value - liabilities)
    else:
        estate_value = 0
        liabilities = 0
        net_estate = 0

    # --- Nil-Rate Bands (2024/25) ---
    nil_rate_band = 325000  # Standard NRB
    residence_nil_rate_band = 175000  # RNRB for main residence

    # Check if RNRB applies (main residence passed to direct descendants)
    rnrb_applies = False
    if iht_profile:
        rnrb_applies = getattr(iht_profile, 'main_residence_to_descendants', False)

    # Calculate available nil-rate bands
    available_nrb = nil_rate_band
    available_rnrb = residence_nil_rate_band if rnrb_applies else 0

    # RNRB taper (reduces by £1 for every £2 over £2m estate)
    rnrb_taper_threshold = 2000000
    if net_estate > rnrb_taper_threshold and available_rnrb > 0:
        excess = net_estate - rnrb_taper_threshold
        taper_reduction = excess / 2
        available_rnrb = max(0, available_rnrb - taper_reduction)

    total_nil_rate_bands = available_nrb + available_rnrb

    # --- IHT Calculation ---
    taxable_estate = max(0, net_estate - total_nil_rate_bands)

    # Standard IHT rate: 40%
    iht_rate = 0.40

    # Charitable giving reduces rate to 36% if 10%+ of net estate left to charity
    charitable_legacy = 0
    if iht_profile:
        charitable_legacy = getattr(iht_profile, 'charitable_legacy', 0)

    charitable_rate_applies = (charitable_legacy / net_estate) >= 0.10 if net_estate > 0 else False
    if charitable_rate_applies:
        iht_rate = 0.36

    iht_liability = taxable_estate * iht_rate

    # --- Gift Analysis (7-year rule) ---
    today = datetime.utcnow().date()
    seven_years_ago = today - timedelta(days=7*365)

    # Count gifts within 7 years
    gifts_within_7_years = [g for g in gifts if g.date and g.date >= seven_years_ago]
    total_gifts_within_7_years = sum(g.amount or 0 for g in gifts_within_7_years)

    # Gifts outside 7 years (exempt)
    gifts_outside_7_years = [g for g in gifts if g.date and g.date < seven_years_ago]

    # Potentially Exempt Transfers (PETs) still in 7-year period
    pets_at_risk = len([g for g in gifts_within_7_years if g.is_pet])

    # --- Trust Summary ---
    trust_count = len(trusts)
    total_trust_value = sum(t.trust_value or 0 for t in trusts)

    # --- Status Assessment ---
    if net_estate == 0:
        status = "not_started"
        message = "Add your estate details to start IHT planning."
    elif iht_liability == 0:
        status = "no_liability"
        message = f"No IHT liability! Your estate of £{net_estate:,.0f} is within the nil-rate bands."
    elif iht_liability < 50000:
        status = "low_liability"
        message = f"Low IHT liability of £{iht_liability:,.0f}. Some simple planning could eliminate this."
    elif iht_liability < 200000:
        status = "moderate_liability"
        message = f"Moderate IHT liability of £{iht_liability:,.0f}. Estate planning recommended."
    else:
        status = "high_liability"
        message = f"Significant IHT liability of £{iht_liability:,.0f}. Comprehensive estate planning strongly advised."

    # --- Recommendations ---
    recommendations = []

    if iht_liability > 0:
        recommendations.append({
            "priority": "high",
            "category": "gifting",
            "message": f"Consider making lifetime gifts. £{iht_liability / 0.40:,.0f} in gifts now could eliminate IHT if you survive 7 years."
        })

    if not rnrb_applies and estate_value > 0:
        recommendations.append({
            "priority": "high",
            "category": "rnrb",
            "message": f"Consider leaving your main residence to direct descendants to use the £{residence_nil_rate_band:,.0f} RNRB."
        })

    if not charitable_rate_applies and iht_liability > 0:
        potential_saving = taxable_estate * 0.04  # 4% reduction (40% to 36%)
        recommendations.append({
            "priority": "medium",
            "category": "charity",
            "message": f"Leave 10% to charity to reduce IHT rate from 40% to 36%, saving £{potential_saving:,.0f}."
        })

    if pets_at_risk > 0:
        recommendations.append({
            "priority": "medium",
            "category": "gift_tracking",
            "message": f"You have {pets_at_risk} PETs within the 7-year period. Monitor survival dates carefully."
        })

    if trust_count == 0 and net_estate > 500000:
        recommendations.append({
            "priority": "low",
            "category": "trusts",
            "message": "Consider setting up trusts for tax-efficient wealth transfer to future generations."
        })

    return {
        "estate_valuation": {
            "gross_estate": estate_value,
            "liabilities": liabilities,
            "net_estate": net_estate,
        },
        "nil_rate_bands": {
            "standard_nrb": nil_rate_band,
            "available_nrb": available_nrb,
            "residence_nrb": residence_nil_rate_band,
            "available_rnrb": round(available_rnrb, 2),
            "rnrb_applies": rnrb_applies,
            "rnrb_tapered": net_estate > rnrb_taper_threshold and rnrb_applies,
            "total_nil_rate_bands": round(total_nil_rate_bands, 2),
        },
        "iht_calculation": {
            "taxable_estate": taxable_estate,
            "iht_rate": iht_rate * 100,
            "charitable_rate_applies": charitable_rate_applies,
            "charitable_legacy": charitable_legacy,
            "iht_liability": round(iht_liability, 2),
        },
        "gifts": {
            "total_gifts_7_years": total_gifts_within_7_years,
            "gift_count_7_years": len(gifts_within_7_years),
            "pets_at_risk": pets_at_risk,
            "exempt_gifts": len(gifts_outside_7_years),
        },
        "trusts": {
            "trust_count": trust_count,
            "total_trust_value": total_trust_value,
        },
        "status": status,
        "message": message,
        "recommendations": recommendations,
        "last_updated": datetime.utcnow().isoformat()
    }


@router.get("/summary", response_model=Dict[str, Any])
def get_iht_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get quick IHT planning summary for main dashboard card.

    Returns key metrics only:
    - Net estate value
    - IHT liability
    - Status
    """

    # Get IHT profile
    iht_profile = db.query(IHTProfile).filter(
        IHTProfile.user_id == current_user.id
    ).first()

    if not iht_profile:
        return {
            "net_estate": 0,
            "iht_liability": 0,
            "status": "not_started"
        }

    # Calculate net estate
    estate_value = (iht_profile.estate_value or 0)
    liabilities = (iht_profile.liabilities or 0)
    net_estate = (iht_profile.net_estate or estate_value - liabilities)

    # Simple IHT calculation
    nil_rate_band = 325000
    residence_nil_rate_band = 175000
    rnrb_applies = getattr(iht_profile, 'main_residence_to_descendants', False)

    total_nrb = nil_rate_band + (residence_nil_rate_band if rnrb_applies else 0)
    taxable_estate = max(0, net_estate - total_nrb)
    iht_liability = taxable_estate * 0.40

    # Quick status
    if iht_liability == 0:
        status = "no_liability"
    elif iht_liability < 100000:
        status = "low_liability"
    elif iht_liability < 300000:
        status = "moderate_liability"
    else:
        status = "high_liability"

    return {
        "net_estate": net_estate,
        "iht_liability": round(iht_liability, 2),
        "status": status
    }