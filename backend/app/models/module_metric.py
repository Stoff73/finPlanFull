from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class ModuleMetric(Base):
    """
    Calculated metrics for each financial planning module.
    Stores dashboard metrics and analytics data for each module.
    """
    __tablename__ = "module_metrics"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # Module identification
    module = Column(String(50), nullable=False, index=True)  # protection, savings, investment, retirement, iht

    # Metric details
    metric_type = Column(String(100), nullable=False)  # e.g., "total_coverage", "emergency_fund_months", "portfolio_value"
    metric_value = Column(Numeric(15, 2))

    # Additional context stored as JSON
    metric_metadata = Column(JSON)  # Additional context data (e.g., breakdowns, trends, comparisons)

    # Timestamp
    calculated_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Relationships
    user = relationship("User", back_populates="module_metrics")

    def __repr__(self):
        return f"<ModuleMetric(module='{self.module}', metric_type='{self.metric_type}', value={self.metric_value})>"