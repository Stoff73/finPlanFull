from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.models.iht import IHTProfile, Gift, Trust, Asset
from app.models.user import User
from app.api.auth.auth import get_current_user
from pydantic import BaseModel
from datetime import date, datetime
from decimal import Decimal

router = APIRouter(prefix="/iht", tags=["IHT"])


class AssetCreate(BaseModel):
    asset_type: str
    description: str
    value: float
    ownership_percentage: float = 100.0
    location: Optional[str] = None
    is_business_property: bool = False
    is_agricultural_property: bool = False
    relief_percentage: float = 0.0


class AssetResponse(AssetCreate):
    id: int
    iht_profile_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class GiftCreate(BaseModel):
    recipient_name: str
    recipient_relationship: str
    amount: float
    date_of_gift: date
    is_potentially_exempt: bool = True
    is_to_trust: bool = False
    trust_id: Optional[int] = None


class GiftResponse(GiftCreate):
    id: int
    iht_profile_id: int
    taper_relief_percentage: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TrustCreate(BaseModel):
    trust_type: str
    trust_name: str
    value: float
    date_created: date
    beneficiaries: str
    is_discretionary: bool = False
    is_interest_in_possession: bool = False


class TrustResponse(TrustCreate):
    id: int
    iht_profile_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class IHTProfileCreate(BaseModel):
    estate_value: float
    liabilities: float = 0.0
    nil_rate_band_used: float = 0.0
    residence_nil_rate_band_available: bool = False
    married_or_civil_partnership: bool = False
    spouse_nil_rate_band_available: float = 0.0


class IHTProfileResponse(IHTProfileCreate):
    id: int
    user_id: int
    effective_rate: float
    tax_due: float
    created_at: datetime
    updated_at: datetime
    assets: List[AssetResponse] = []
    gifts: List[GiftResponse] = []
    trusts: List[TrustResponse] = []

    class Config:
        from_attributes = True


class IHTCalculation(BaseModel):
    gross_estate: float
    deductible_liabilities: float
    net_estate: float
    nil_rate_band: float
    residence_nil_rate_band: float
    taxable_estate: float
    tax_due: float
    effective_rate: float
    business_property_relief: float
    agricultural_property_relief: float
    charitable_exemption: float
    spouse_exemption: float


@router.post("/profile", response_model=IHTProfileResponse)
async def create_or_update_iht_profile(
    profile: IHTProfileCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    existing_profile = db.query(IHTProfile).filter(
        IHTProfile.user_id == current_user.id
    ).first()

    if existing_profile:
        for key, value in profile.dict().items():
            setattr(existing_profile, key, value)
        db_profile = existing_profile
    else:
        db_profile = IHTProfile(
            **profile.dict(),
            user_id=current_user.id
        )
        db.add(db_profile)

    db_profile.tax_due = calculate_iht_tax(db_profile)
    db_profile.effective_rate = (db_profile.tax_due / db_profile.estate_value * 100) if db_profile.estate_value > 0 else 0

    db.commit()
    db.refresh(db_profile)
    return db_profile


@router.get("/profile", response_model=IHTProfileResponse)
async def get_iht_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(IHTProfile).filter(
        IHTProfile.user_id == current_user.id
    ).first()

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="IHT profile not found"
        )

    return profile


@router.post("/assets", response_model=AssetResponse)
async def add_asset(
    asset: AssetCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(IHTProfile).filter(
        IHTProfile.user_id == current_user.id
    ).first()

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="IHT profile not found. Please create a profile first."
        )

    db_asset = Asset(
        **asset.dict(),
        iht_profile_id=profile.id
    )
    db.add(db_asset)

    profile.estate_value += asset.value * (asset.ownership_percentage / 100)
    profile.tax_due = calculate_iht_tax(profile)
    profile.effective_rate = (profile.tax_due / profile.estate_value * 100) if profile.estate_value > 0 else 0

    db.commit()
    db.refresh(db_asset)
    return db_asset


@router.get("/assets", response_model=List[AssetResponse])
async def get_assets(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(IHTProfile).filter(
        IHTProfile.user_id == current_user.id
    ).first()

    if not profile:
        return []

    return profile.assets


@router.post("/gifts", response_model=GiftResponse)
async def add_gift(
    gift: GiftCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(IHTProfile).filter(
        IHTProfile.user_id == current_user.id
    ).first()

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="IHT profile not found. Please create a profile first."
        )

    taper_relief = calculate_taper_relief(gift.date_of_gift)

    db_gift = Gift(
        **gift.dict(),
        iht_profile_id=profile.id,
        taper_relief_percentage=taper_relief
    )
    db.add(db_gift)
    db.commit()
    db.refresh(db_gift)
    return db_gift


@router.get("/gifts", response_model=List[GiftResponse])
async def get_gifts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(IHTProfile).filter(
        IHTProfile.user_id == current_user.id
    ).first()

    if not profile:
        return []

    return profile.gifts


@router.post("/trusts", response_model=TrustResponse)
async def add_trust(
    trust: TrustCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(IHTProfile).filter(
        IHTProfile.user_id == current_user.id
    ).first()

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="IHT profile not found. Please create a profile first."
        )

    db_trust = Trust(
        **trust.dict(),
        iht_profile_id=profile.id
    )
    db.add(db_trust)
    db.commit()
    db.refresh(db_trust)
    return db_trust


@router.get("/trusts", response_model=List[TrustResponse])
async def get_trusts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(IHTProfile).filter(
        IHTProfile.user_id == current_user.id
    ).first()

    if not profile:
        return []

    return profile.trusts


@router.get("/calculate", response_model=IHTCalculation)
async def calculate_iht(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(IHTProfile).filter(
        IHTProfile.user_id == current_user.id
    ).first()

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="IHT profile not found"
        )

    nil_rate_band = 325000
    residence_nil_rate_band = 175000 if profile.residence_nil_rate_band_available else 0

    if profile.married_or_civil_partnership:
        nil_rate_band += profile.spouse_nil_rate_band_available

    business_relief = sum(
        asset.value * (asset.ownership_percentage / 100) * (asset.relief_percentage / 100)
        for asset in profile.assets if asset.is_business_property
    )

    agricultural_relief = sum(
        asset.value * (asset.ownership_percentage / 100) * (asset.relief_percentage / 100)
        for asset in profile.assets if asset.is_agricultural_property
    )

    net_estate = profile.estate_value - profile.liabilities
    total_allowances = nil_rate_band + residence_nil_rate_band
    total_reliefs = business_relief + agricultural_relief

    taxable_estate = max(0, net_estate - total_allowances - total_reliefs)
    tax_due = taxable_estate * 0.4
    effective_rate = (tax_due / net_estate * 100) if net_estate > 0 else 0

    return IHTCalculation(
        gross_estate=profile.estate_value,
        deductible_liabilities=profile.liabilities,
        net_estate=net_estate,
        nil_rate_band=nil_rate_band,
        residence_nil_rate_band=residence_nil_rate_band,
        taxable_estate=taxable_estate,
        tax_due=tax_due,
        effective_rate=effective_rate,
        business_property_relief=business_relief,
        agricultural_property_relief=agricultural_relief,
        charitable_exemption=0,
        spouse_exemption=0
    )


def calculate_iht_tax(profile: IHTProfile) -> float:
    nil_rate_band = 325000
    residence_nil_rate_band = 175000 if profile.residence_nil_rate_band_available else 0

    if profile.married_or_civil_partnership:
        nil_rate_band += profile.spouse_nil_rate_band_available

    net_estate = profile.estate_value - profile.liabilities
    total_allowances = nil_rate_band + residence_nil_rate_band - profile.nil_rate_band_used

    taxable_estate = max(0, net_estate - total_allowances)
    return taxable_estate * 0.4


def calculate_taper_relief(gift_date: date) -> float:
    years_since_gift = (date.today() - gift_date).days / 365.25

    if years_since_gift >= 7:
        return 100.0
    elif years_since_gift >= 6:
        return 80.0
    elif years_since_gift >= 5:
        return 60.0
    elif years_since_gift >= 4:
        return 40.0
    elif years_since_gift >= 3:
        return 20.0
    else:
        return 0.0