"""Savings Goals API

Manages savings goals tracking (emergency fund, vacation, house deposit, etc.)
Uses ModuleGoal model for goal tracking.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from pydantic import BaseModel, Field

from app.database import get_db
from app.api.auth.auth import get_current_user
from app.models.user import User
from app.models.module_goal import ModuleGoal
from app.models import BankAccount

router = APIRouter()


# Pydantic schemas
class SavingsGoalCreate(BaseModel):
    goal_type: str = Field(..., description="emergency_fund, vacation, house_deposit, car, education, other")
    target_amount: float = Field(..., gt=0)
    target_date: Optional[date] = None
    current_amount: float = Field(default=0, ge=0)
    notes: Optional[str] = None


class SavingsGoalUpdate(BaseModel):
    goal_type: Optional[str] = None
    target_amount: Optional[float] = Field(None, gt=0)
    target_date: Optional[date] = None
    current_amount: Optional[float] = Field(None, ge=0)
    status: Optional[str] = Field(None, pattern="^(active|achieved|paused|cancelled)$")
    notes: Optional[str] = None


@router.get("")
async def list_savings_goals(
    include_inactive: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all savings goals for the current user

    Query params:
        - include_inactive: Include achieved/paused/cancelled goals (default: false)
    """
    query = db.query(ModuleGoal).filter(
        ModuleGoal.user_id == current_user.id,
        ModuleGoal.module == "savings"
    )

    if not include_inactive:
        query = query.filter(ModuleGoal.status == "active")

    goals = query.order_by(ModuleGoal.target_date.asc()).all()

    # Calculate overall progress
    total_target = sum(g.target_amount for g in goals if g.status == "active")
    total_current = sum(g.current_amount for g in goals if g.status == "active")
    overall_progress = (total_current / total_target * 100) if total_target > 0 else 0

    return {
        "goal_count": len(goals),
        "active_goals": len([g for g in goals if g.status == "active"]),
        "total_target": total_target,
        "total_current": total_current,
        "overall_progress": round(overall_progress, 1),
        "goals": [
            {
                "id": g.id,
                "goal_type": g.goal_type,
                "target_amount": g.target_amount,
                "current_amount": g.current_amount,
                "progress_percentage": g.progress_percentage,
                "target_date": g.target_date.isoformat() if g.target_date else None,
                "status": g.status,
                "notes": g.notes,
                "created_at": g.created_at.isoformat() if g.created_at else None
            }
            for g in goals
        ]
    }


@router.post("")
async def create_savings_goal(
    goal_data: SavingsGoalCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new savings goal

    Body:
        - goal_type: Type of goal (required)
        - target_amount: Target amount to save (required)
        - target_date: Target completion date (optional)
        - current_amount: Current progress (default: 0)
        - notes: Additional notes (optional)
    """
    new_goal = ModuleGoal(
        user_id=current_user.id,
        module="savings",
        goal_type=goal_data.goal_type,
        target_amount=goal_data.target_amount,
        target_date=goal_data.target_date,
        current_amount=goal_data.current_amount,
        status="active",
        notes=goal_data.notes,
        created_at=datetime.utcnow()
    )

    db.add(new_goal)
    db.commit()
    db.refresh(new_goal)

    return {
        "id": new_goal.id,
        "goal_type": new_goal.goal_type,
        "target_amount": new_goal.target_amount,
        "progress_percentage": new_goal.progress_percentage,
        "message": "Savings goal created successfully"
    }


@router.get("/{goal_id}")
async def get_savings_goal(
    goal_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific savings goal by ID"""
    goal = db.query(ModuleGoal).filter(
        ModuleGoal.id == goal_id,
        ModuleGoal.user_id == current_user.id,
        ModuleGoal.module == "savings"
    ).first()

    if not goal:
        raise HTTPException(status_code=404, detail="Savings goal not found")

    # Calculate days remaining if target date exists
    days_remaining = None
    if goal.target_date:
        delta = (goal.target_date - date.today()).days
        days_remaining = delta if delta >= 0 else 0

    # Calculate required monthly savings to reach goal
    monthly_required = None
    if goal.target_date and days_remaining and days_remaining > 0:
        months_remaining = days_remaining / 30
        amount_remaining = goal.target_amount - goal.current_amount
        if months_remaining > 0 and amount_remaining > 0:
            monthly_required = amount_remaining / months_remaining

    return {
        "id": goal.id,
        "goal_type": goal.goal_type,
        "target_amount": goal.target_amount,
        "current_amount": goal.current_amount,
        "progress_percentage": goal.progress_percentage,
        "amount_remaining": goal.target_amount - goal.current_amount,
        "target_date": goal.target_date.isoformat() if goal.target_date else None,
        "days_remaining": days_remaining,
        "monthly_required": round(monthly_required, 2) if monthly_required else None,
        "status": goal.status,
        "notes": goal.notes,
        "created_at": goal.created_at.isoformat() if goal.created_at else None,
        "updated_at": goal.updated_at.isoformat() if goal.updated_at else None
    }


@router.put("/{goal_id}")
async def update_savings_goal(
    goal_id: int,
    goal_data: SavingsGoalUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a savings goal

    Only fields provided in the request body will be updated
    """
    # Verify ownership
    goal = db.query(ModuleGoal).filter(
        ModuleGoal.id == goal_id,
        ModuleGoal.user_id == current_user.id,
        ModuleGoal.module == "savings"
    ).first()

    if not goal:
        raise HTTPException(status_code=404, detail="Savings goal not found")

    # Update fields
    update_data = goal_data.dict(exclude_unset=True)

    for field, value in update_data.items():
        setattr(goal, field, value)

    # Auto-mark as achieved if current >= target
    if goal.current_amount >= goal.target_amount and goal.status == "active":
        goal.status = "achieved"

    goal.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(goal)

    return {
        "id": goal.id,
        "goal_type": goal.goal_type,
        "progress_percentage": goal.progress_percentage,
        "status": goal.status,
        "message": "Savings goal updated successfully"
    }


@router.delete("/{goal_id}")
async def delete_savings_goal(
    goal_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mark a savings goal as cancelled

    Sets status to 'cancelled' rather than hard deleting
    """
    # Verify ownership
    goal = db.query(ModuleGoal).filter(
        ModuleGoal.id == goal_id,
        ModuleGoal.user_id == current_user.id,
        ModuleGoal.module == "savings"
    ).first()

    if not goal:
        raise HTTPException(status_code=404, detail="Savings goal not found")

    # Mark as cancelled
    goal.status = "cancelled"
    goal.updated_at = datetime.utcnow()

    db.commit()

    return {
        "message": "Savings goal cancelled successfully",
        "id": goal_id
    }


class ProgressUpdate(BaseModel):
    amount: float = Field(..., description="Amount to add to current progress")


@router.post("/{goal_id}/progress")
async def update_goal_progress(
    goal_id: int,
    progress_data: ProgressUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add progress to a savings goal

    Body:
        - amount: Amount to add to current progress (can be negative to decrease)
    """
    amount = progress_data.amount
    # Verify ownership
    goal = db.query(ModuleGoal).filter(
        ModuleGoal.id == goal_id,
        ModuleGoal.user_id == current_user.id,
        ModuleGoal.module == "savings"
    ).first()

    if not goal:
        raise HTTPException(status_code=404, detail="Savings goal not found")

    # Update progress
    goal.current_amount += amount

    # Ensure current_amount doesn't go negative
    if goal.current_amount < 0:
        goal.current_amount = 0

    # Auto-mark as achieved if reached target
    if goal.current_amount >= goal.target_amount and goal.status == "active":
        goal.status = "achieved"

    goal.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(goal)

    return {
        "id": goal.id,
        "current_amount": goal.current_amount,
        "progress_percentage": goal.progress_percentage,
        "status": goal.status,
        "message": f"Progress updated: {'Goal achieved!' if goal.status == 'achieved' else f'{goal.progress_percentage:.1f}% complete'}"
    }