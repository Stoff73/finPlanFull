from sqlalchemy import Column, Integer, String, Numeric, Date, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class ModuleGoal(Base):
    """
    User goals for each financial planning module.
    Tracks targets, progress, and status for module-specific goals.
    """
    __tablename__ = "module_goals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # Module identification
    module = Column(String(50), nullable=False, index=True)  # protection, savings, investment, retirement, iht
    goal_type = Column(String(100), nullable=False)  # e.g., "emergency_fund", "retirement_income", "coverage_target"

    # Goal targets
    target_amount = Column(Numeric(15, 2))
    target_date = Column(Date)

    # Progress tracking
    current_amount = Column(Numeric(15, 2))

    # Status
    status = Column(String(50), default='active')  # active, achieved, paused, archived

    # Additional context
    notes = Column(Text)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="module_goals")

    def __repr__(self):
        return f"<ModuleGoal(module='{self.module}', goal_type='{self.goal_type}', status='{self.status}')>"

    @property
    def progress_percentage(self):
        """Calculate progress as a percentage"""
        if not self.target_amount or not self.current_amount:
            return 0.0
        if float(self.target_amount) == 0:
            return 0.0
        return min(100.0, (float(self.current_amount) / float(self.target_amount)) * 100)