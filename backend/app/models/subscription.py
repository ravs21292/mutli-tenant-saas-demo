"""
Subscription model for Stripe subscription management
"""

from sqlalchemy import Column, String, DateTime, Boolean, Text, ForeignKey, Integer, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base
import uuid
from datetime import datetime


class Subscription(Base):
    """Subscription model for Stripe subscription management"""
    
    __tablename__ = "subscriptions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Tenant relationship
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, unique=True)
    tenant = relationship("Tenant", back_populates="subscription")
    
    # Stripe subscription information
    stripe_subscription_id = Column(String(255), unique=True, nullable=False)
    stripe_price_id = Column(String(255), nullable=True)
    stripe_product_id = Column(String(255), nullable=True)
    
    # Subscription details
    plan = Column(String(50), nullable=False)  # basic, pro, enterprise
    status = Column(String(50), nullable=False)  # active, canceled, past_due, incomplete, etc.
    
    # Limits and quotas
    seats = Column(Integer, default=5)
    storage_quota_bytes = Column(Integer, default=1073741824)  # 1GB default
    used_storage_bytes = Column(Integer, default=0)
    
    # Billing
    billing_cycle = Column(String(20), default="monthly")  # monthly, yearly
    currency = Column(String(3), default="usd")
    amount = Column(Integer, nullable=True)  # Amount in cents
    
    # Trial information
    trial_start = Column(DateTime, nullable=True)
    trial_end = Column(DateTime, nullable=True)
    is_trial = Column(Boolean, default=False)
    
    # Billing dates
    current_period_start = Column(DateTime, nullable=True)
    current_period_end = Column(DateTime, nullable=True)
    cancel_at_period_end = Column(Boolean, default=False)
    canceled_at = Column(DateTime, nullable=True)
    
    # Metadata
    subscription_metadata = Column(JSON, nullable=True)  # Additional subscription metadata
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Subscription(id={self.id}, tenant_id={self.tenant_id}, plan={self.plan}, status={self.status})>"
    
    @property
    def is_trial_active(self) -> bool:
        """Check if trial is currently active"""
        if not self.is_trial or not self.trial_end:
            return False
        return datetime.utcnow() < self.trial_end
    
    @property
    def days_until_renewal(self) -> int:
        """Get days until next billing cycle"""
        if not self.current_period_end:
            return 0
        delta = self.current_period_end - datetime.utcnow()
        return max(0, delta.days)
    
    @property
    def storage_usage_percentage(self) -> float:
        """Get storage usage as percentage"""
        if self.storage_quota_bytes == 0:
            return 0
        return (self.used_storage_bytes / self.storage_quota_bytes) * 100
