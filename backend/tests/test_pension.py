import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.base import Base, get_db
from app.models.user import User
from app.models.pension import EnhancedPension, SchemeType, ReliefMethod, PensionType
from app.core.security import get_password_hash
import json

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_pension.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

# Test data
test_user_data = {
    "username": "testpension",
    "email": "pension@test.com",
    "password": "testpass123",
    "full_name": "Pension Tester"
}

@pytest.fixture
def test_user():
    db = TestingSessionLocal()
    hashed_password = get_password_hash(test_user_data["password"])
    user = User(
        username=test_user_data["username"],
        email=test_user_data["email"],
        hashed_password=hashed_password,
        full_name=test_user_data["full_name"]
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    yield user
    db.delete(user)
    db.commit()
    db.close()

@pytest.fixture
def auth_token(test_user):
    response = client.post(
        "/api/auth/token",
        data={
            "username": test_user_data["username"],
            "password": test_user_data["password"]
        }
    )
    return response.json()["access_token"]


class TestAnnualAllowance:
    """Test Annual Allowance calculations"""

    def test_standard_aa_calculation(self, auth_token):
        """Test standard Annual Allowance calculation"""
        response = client.post(
            "/api/pension/annual-allowance/calculate",
            json={
                "annual_income": 50000,
                "bonus_income": 5000,
                "other_income": 0,
                "personal_contribution_monthly": 500,
                "employer_contribution_monthly": 500,
                "mpaa_triggered": False,
                "tax_year": "2025/26"
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["standard_aa"] == 60000
        assert data["used_aa"] == 12000  # (500 + 500) * 12
        assert data["remaining_aa"] > 0
        assert data["is_tapered"] == False

    def test_tapered_aa_calculation(self, auth_token):
        """Test tapered Annual Allowance for high earners"""
        response = client.post(
            "/api/pension/annual-allowance/calculate",
            json={
                "annual_income": 250000,
                "bonus_income": 30000,
                "other_income": 0,
                "personal_contribution_monthly": 2000,
                "employer_contribution_monthly": 2000,
                "mpaa_triggered": False,
                "tax_year": "2025/26"
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["is_tapered"] == True
        assert data["tapered_aa"] is not None
        assert data["tapered_aa"] < 60000
        assert data["threshold_income"] > 200000
        assert data["adjusted_income"] > 260000

    def test_mpaa_restriction(self, auth_token):
        """Test Money Purchase Annual Allowance restriction"""
        response = client.post(
            "/api/pension/annual-allowance/calculate",
            json={
                "annual_income": 60000,
                "bonus_income": 0,
                "other_income": 0,
                "personal_contribution_monthly": 1000,
                "employer_contribution_monthly": 500,
                "mpaa_triggered": True,
                "tax_year": "2025/26"
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["mpaa_triggered"] == True
        assert data["mpaa_limit"] == 10000
        # Total input is 18000, which exceeds MPAA
        assert data["aa_charge"] is not None


class TestTaxRelief:
    """Test tax relief calculations"""

    def test_basic_rate_relief(self, auth_token):
        """Test basic rate tax relief"""
        response = client.post(
            "/api/pension/tax-relief/calculate",
            json={
                "gross_contribution_annual": 6000,
                "tax_rate": "basic",
                "contribution_method": "relief_at_source",
                "is_scottish_taxpayer": False
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["gross_contribution"] == 6000
        assert data["basic_rate_relief"] == 1200  # 20% of 6000
        assert data["higher_rate_relief"] == 0
        assert data["additional_rate_relief"] == 0
        assert data["total_relief"] == 1200
        assert data["net_cost"] == 4800

    def test_higher_rate_relief(self, auth_token):
        """Test higher rate tax relief"""
        response = client.post(
            "/api/pension/tax-relief/calculate",
            json={
                "gross_contribution_annual": 12000,
                "tax_rate": "higher",
                "contribution_method": "relief_at_source",
                "is_scottish_taxpayer": False
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["gross_contribution"] == 12000
        assert data["basic_rate_relief"] == 2400  # 20% of 12000
        assert data["higher_rate_relief"] == 2400  # Additional 20%
        assert data["total_relief"] == 4800  # 40% total
        assert data["net_cost"] == 7200

    def test_salary_sacrifice_ni_savings(self, auth_token):
        """Test salary sacrifice with NI savings"""
        response = client.post(
            "/api/pension/tax-relief/calculate",
            json={
                "gross_contribution_annual": 10000,
                "tax_rate": "higher",
                "contribution_method": "salary_sacrifice",
                "is_scottish_taxpayer": False
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["ni_savings"] is not None
        assert data["ni_savings"] > 0  # Should include NI savings


class TestCarryForward:
    """Test carry forward calculations"""

    def test_carry_forward_calculation(self, auth_token):
        """Test carry forward from previous years"""
        response = client.post(
            "/api/pension/carry-forward/calculate",
            json={
                "current_year_input": 70000,
                "previous_years_data": [
                    {
                        "tax_year": "2024/25",
                        "annual_allowance": 60000,
                        "amount_used": 40000
                    },
                    {
                        "tax_year": "2023/24",
                        "annual_allowance": 60000,
                        "amount_used": 30000
                    }
                ]
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total_carry_forward"] == 50000  # 20000 + 30000
        assert data["current_year_aa"] == 60000
        assert data["total_available_aa"] == 110000  # 60000 + 50000
        assert len(data["carry_forward_years"]) == 2


class TestAutoEnrolment:
    """Test auto-enrolment compliance"""

    def test_auto_enrolment_eligible(self, auth_token):
        """Test auto-enrolment eligibility check"""
        response = client.post(
            "/api/pension/auto-enrolment/check",
            json={
                "annual_earnings": 25000,
                "age": 30,
                "already_enrolled": False
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["eligible"] == True
        assert data["earnings_trigger"] == 10000
        assert data["qualifying_earnings_lower"] == 6240
        assert data["qualifying_earnings_upper"] == 50270
        assert data["qualifying_earnings"] > 0
        assert data["minimum_total_contribution"] > 0

    def test_auto_enrolment_not_eligible(self, auth_token):
        """Test auto-enrolment when not eligible"""
        response = client.post(
            "/api/pension/auto-enrolment/check",
            json={
                "annual_earnings": 8000,
                "age": 25,
                "already_enrolled": False
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["eligible"] == False


class TestPensionSchemes:
    """Test pension scheme management"""

    def test_create_pension_scheme(self, auth_token):
        """Test creating a new pension scheme"""
        response = client.post(
            "/api/pension/schemes/",
            json={
                "scheme_name": "Test Workplace Pension",
                "provider": "Test Provider",
                "scheme_type": "DC",
                "pension_type": "workplace",
                "relief_method": "net_pay",
                "current_value": 50000,
                "monthly_member_contribution": 500,
                "monthly_employer_contribution": 300,
                "annual_growth_rate": 5.0,
                "annual_management_charge": 0.75
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["scheme_name"] == "Test Workplace Pension"
        assert data["annual_input"] == 9600  # (500 + 300) * 12

    def test_get_all_schemes(self, auth_token):
        """Test retrieving all pension schemes"""
        # First create a scheme
        client.post(
            "/api/pension/schemes/",
            json={
                "scheme_name": "Test SIPP",
                "provider": "SIPP Provider",
                "scheme_type": "DC",
                "pension_type": "SIPP",
                "relief_method": "relief_at_source",
                "current_value": 100000,
                "monthly_member_contribution": 1000,
                "monthly_employer_contribution": 0
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        # Now get all schemes
        response = client.get(
            "/api/pension/schemes/",
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0


class TestOptimization:
    """Test pension optimization features"""

    def test_contribution_optimization(self, auth_token):
        """Test contribution optimization"""
        response = client.post(
            "/api/pension/optimization/optimize",
            json={
                "target_retirement_age": 65,
                "target_retirement_income": 40000,
                "current_age": 35,
                "current_income": 60000,
                "risk_tolerance": "moderate",
                "maximize_tax_relief": True,
                "use_salary_sacrifice": False
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "recommended_monthly_contribution" in data
        assert "projected_retirement_value" in data
        assert "total_tax_savings" in data
        assert data["years_to_retirement"] == 30

    def test_retirement_readiness_score(self, auth_token):
        """Test retirement readiness calculation"""
        response = client.get(
            "/api/pension/optimization/readiness-score?target_retirement_age=65",
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "overall_score" in data
        assert 0 <= data["overall_score"] <= 100
        assert "recommendations" in data
        assert isinstance(data["recommendations"], list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])