"""
Billing customer model for Stripe integration
"""

from sqlalchemy import Column, String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base
import uuid
from datetime import datetime


class BillingCustomer(Base):
    """Billing customer model for Stripe customer management"""
    
    __tablename__ = "billing_customers"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Tenant relationship
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, unique=True)
    tenant = relationship("Tenant", back_populates="billing_customer")
    
    # Stripe customer information
    stripe_customer_id = Column(String(255), unique=True, nullable=False)
    stripe_customer_email = Column(String(255), nullable=True)
    stripe_customer_name = Column(String(255), nullable=True)
    
    # Billing address
    billing_address_line1 = Column(String(255), nullable=True)
    billing_address_line2 = Column(String(255), nullable=True)
    billing_address_city = Column(String(100), nullable=True)
    billing_address_state = Column(String(100), nullable=True)
    billing_address_country = Column(String(100), nullable=True)
    billing_address_postal_code = Column(String(20), nullable=True)
    
    # Payment method
    default_payment_method_id = Column(String(255), nullable=True)
    payment_method_type = Column(String(50), nullable=True)  # card, bank_account, etc.
    
    # Tax information
    tax_id = Column(String(100), nullable=True)
    tax_exempt = Column(Boolean, default=False)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<BillingCustomer(id={self.id}, tenant_id={self.tenant_id}, stripe_customer_id={self.stripe_customer_id})>"
