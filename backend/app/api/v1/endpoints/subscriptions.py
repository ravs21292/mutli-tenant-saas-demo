"""
Subscription management endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user, require_owner
from app.models.user import User
from app.models.tenant import Tenant
from app.schemas.subscription import SubscriptionResponse, SubscriptionUpdate
from app.services.audit import log_user_action
from app.services.stripe_service import stripe_service

router = APIRouter()


@router.get("/", response_model=SubscriptionResponse)
async def get_subscription(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current subscription information"""
    tenant = db.query(Tenant).filter(Tenant.id == current_user.tenant_id).first()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    
    return {
        "plan": tenant.subscription_plan,
        "status": tenant.subscription_status,
        "max_seats": tenant.max_seats,
        "max_storage_bytes": tenant.max_storage_bytes,
        "used_storage_bytes": tenant.used_storage_bytes,
        "stripe_customer_id": tenant.stripe_customer_id,
        "stripe_subscription_id": tenant.stripe_subscription_id
    }


@router.post("/create-checkout-session")
async def create_checkout_session(
    plan: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create Stripe checkout session for subscription"""
    if plan not in ["basic", "pro"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid plan. Must be 'basic' or 'pro'"
        )
    
    tenant = db.query(Tenant).filter(Tenant.id == current_user.tenant_id).first()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    
    try:
        checkout_session = await stripe_service.create_checkout_session(
            tenant_id=tenant.id,
            plan=plan,
            customer_email=current_user.email
        )
        
        return {"checkout_url": checkout_session["url"]}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create checkout session: {str(e)}"
        )


@router.post("/cancel")
async def cancel_subscription(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cancel current subscription"""
    tenant = db.query(Tenant).filter(Tenant.id == current_user.tenant_id).first()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    
    if not tenant.stripe_subscription_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No active subscription found"
        )
    
    try:
        await stripe_service.cancel_subscription(tenant.stripe_subscription_id)
        
        # Update tenant subscription status
        tenant.subscription_status = "canceled"
        db.commit()
        
        # Log subscription cancellation
        await log_user_action(
            db=db,
            action_type="subscription.cancel",
            user=current_user,
            description="Subscription canceled",
            metadata={"plan": tenant.subscription_plan}
        )
        
        return {"message": "Subscription canceled successfully"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel subscription: {str(e)}"
        )


@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """Handle Stripe webhook events"""
    try:
        event = await stripe_service.handle_webhook(request)
        
        if event["type"] == "checkout.session.completed":
            # Handle successful checkout
            session = event["data"]["object"]
            tenant_id = session["metadata"]["tenant_id"]
            plan = session["metadata"]["plan"]
            
            # Update tenant subscription
            tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
            if tenant:
                tenant.subscription_plan = plan
                tenant.subscription_status = "active"
                tenant.stripe_customer_id = session["customer"]
                tenant.stripe_subscription_id = session["subscription"]
                
                # Update limits based on plan
                if plan == "basic":
                    tenant.max_seats = 5
                    tenant.max_storage_bytes = 1073741824  # 1GB
                elif plan == "pro":
                    tenant.max_seats = 50
                    tenant.max_storage_bytes = 53687091200  # 50GB
                
                db.commit()
        
        elif event["type"] == "customer.subscription.deleted":
            # Handle subscription cancellation
            subscription = event["data"]["object"]
            tenant = db.query(Tenant).filter(
                Tenant.stripe_subscription_id == subscription["id"]
            ).first()
            
            if tenant:
                tenant.subscription_status = "canceled"
                db.commit()
        
        return {"status": "success"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Webhook error: {str(e)}"
        )