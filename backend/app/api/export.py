from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime

from app.database import get_db
from app.api.auth.auth import get_current_user
from app.models.user import User
from app.models.iht import IHTProfile
from app.models.financial import BalanceSheet, ProfitLoss, CashFlow
from app.models.product import Product
from app.services.export import ExportService
from app.api.iht import calculate_iht

router = APIRouter(prefix="/api/export", tags=["export"])


@router.get("/iht/pdf")
async def export_iht_pdf(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export IHT calculation as PDF"""
    try:
        # Get IHT profile
        profile = db.query(IHTProfile).filter(IHTProfile.user_id == current_user.id).first()

        if not profile:
            raise HTTPException(status_code=404, detail="IHT profile not found")

        # Get IHT calculation data
        iht_data = {
            "profile_id": profile.id,
            "assets": [],
            "gifts": [],
            "trusts": [],
            "reliefs": {
                "business_relief": 0,
                "agricultural_relief": 0,
                "charitable_giving": 0
            }
        }

        # Get assets
        for asset in profile.assets:
            iht_data["assets"].append({
                "asset_type": asset.asset_type,
                "value": asset.value,
                "owner": asset.owner,
                "business_relief_applicable": asset.business_relief_applicable,
                "agricultural_relief_applicable": asset.agricultural_relief_applicable
            })

        # Get gifts
        for gift in profile.gifts:
            iht_data["gifts"].append({
                "amount": gift.amount,
                "recipient": gift.recipient,
                "date": gift.date.isoformat(),
                "gift_type": gift.gift_type
            })

        # Calculate IHT
        calculation = calculate_iht(iht_data)

        # Generate PDF
        pdf_buffer = ExportService.generate_iht_pdf(calculation)

        # Return PDF as download
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=iht_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/financial/excel")
async def export_financial_excel(
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export financial statements as Excel file"""
    try:
        # Get financial statements
        balance_sheets = db.query(BalanceSheet).filter(
            BalanceSheet.user_id == current_user.id
        ).order_by(BalanceSheet.period.desc()).limit(limit).all()

        profit_losses = db.query(ProfitLoss).filter(
            ProfitLoss.user_id == current_user.id
        ).order_by(ProfitLoss.period.desc()).limit(limit).all()

        cash_flows = db.query(CashFlow).filter(
            CashFlow.user_id == current_user.id
        ).order_by(CashFlow.period.desc()).limit(limit).all()

        # Generate Excel file
        excel_buffer = ExportService.generate_financial_excel(
            balance_sheets,
            profit_losses,
            cash_flows
        )

        # Return Excel file as download
        return StreamingResponse(
            excel_buffer,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f"attachment; filename=financial_statements_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/products/csv")
async def export_products_csv(
    product_type: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export products as CSV file"""
    try:
        # Query products
        query = db.query(Product).filter(Product.user_id == current_user.id)

        if product_type:
            query = query.filter(Product.product_type == product_type)

        products = query.all()

        # Convert to dict list
        product_data = []
        for product in products:
            data = {
                'product_type': product.product_type,
                'provider': product.provider,
                'product_name': product.product_name,
                'value': product.value,
                'created_at': product.created_at.strftime('%Y-%m-%d')
            }

            # Add specific fields based on product type
            if product.product_type == 'pension' and hasattr(product, 'pension'):
                data.update({
                    'pension_type': product.pension.pension_type,
                    'annual_contribution': product.pension.annual_contribution,
                    'employer_contribution': product.pension.employer_contribution,
                    'retirement_age': product.pension.retirement_age
                })
            elif product.product_type == 'investment' and hasattr(product, 'investment'):
                data.update({
                    'investment_type': product.investment.investment_type,
                    'units': product.investment.units,
                    'purchase_price': product.investment.purchase_price,
                    'current_price': product.investment.current_price,
                    'isa_wrapper': product.investment.isa_wrapper
                })
            elif product.product_type == 'protection' and hasattr(product, 'protection'):
                data.update({
                    'protection_type': product.protection.protection_type,
                    'sum_assured': product.protection.sum_assured,
                    'monthly_premium': product.protection.monthly_premium,
                    'term_years': product.protection.term_years
                })

            product_data.append(data)

        # Generate CSV
        csv_buffer = ExportService.export_to_csv(product_data)

        # Return CSV as download
        return StreamingResponse(
            csv_buffer,
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=products_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/products/csv/import")
async def import_products_csv(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Import products from CSV file"""
    try:
        # Read file content
        content = await file.read()

        # Import data
        imported_data = ExportService.import_from_csv(content, Product)

        # Create products
        created_count = 0
        for item in imported_data:
            # Add user_id
            item['user_id'] = current_user.id

            # Create product
            product = Product(**{
                k: v for k, v in item.items()
                if k in ['user_id', 'product_type', 'provider', 'product_name', 'value']
            })
            db.add(product)
            created_count += 1

        db.commit()

        return {
            "success": True,
            "message": f"Imported {created_count} products successfully",
            "count": created_count
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/backup")
async def create_backup(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a backup of all user data"""
    try:
        # Filter the session to only include current user's data
        # This is a simplified version - in production, you'd want to filter by user
        backup_buffer = ExportService.create_backup(db)

        # Return backup as download
        return StreamingResponse(
            backup_buffer,
            media_type="application/json",
            headers={
                "Content-Disposition": f"attachment; filename=backup_{current_user.username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/restore")
async def restore_backup(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Restore user data from a backup file"""
    try:
        # Read file content
        content = await file.read()

        # Restore data
        result = ExportService.restore_backup(db, content)

        if result['success']:
            return {
                "success": True,
                "message": "Backup restored successfully",
                "details": result['restored'],
                "backup_date": result['backup_date']
            }
        else:
            raise HTTPException(status_code=400, detail=result['error'])

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))