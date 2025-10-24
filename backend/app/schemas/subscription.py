"""
Subscription schemas
"""

from pydantic import BaseModel
from typing import Optional
from uuid import UUID


class SubscriptionResponse(BaseModel):
    """Subscription response schema"""
    plan: str
    status: str
    max_seats: int
    max_storage_bytes: int
    used_storage_bytes: int
    stripe_customer_id: Optional[str] = None
    stripe_subscription_id: Optional[str] = None


class SubscriptionUpdate(BaseModel):
    """Subscription update schema"""
    plan: Optional[str] = None
    status: Optional[str] = None
