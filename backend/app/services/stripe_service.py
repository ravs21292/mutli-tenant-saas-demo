"""
Stripe integration service
"""

import stripe
from app.core.config import settings
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

# Configure Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


class StripeService:
    """Service for Stripe operations"""
    
    def __init__(self):
        self.webhook_secret = settings.STRIPE_WEBHOOK_SECRET
    
    async def create_checkout_session(
        self,
        tenant_id: str,
        plan: str,
        customer_email: str
    ) -> Dict[str, Any]:
        """Create Stripe checkout session"""
        try:
            # Define pricing based on plan
            pricing_map = {
                "basic": {
                    "price_id": "price_basic_monthly",  # Replace with actual price ID
                    "amount": 2900,  # $29.00
                    "currency": "usd"
                },
                "pro": {
                    "price_id": "price_pro_monthly",  # Replace with actual price ID
                    "amount": 9900,  # $99.00
                    "currency": "usd"
                }
            }
            
            if plan not in pricing_map:
                raise ValueError(f"Invalid plan: {plan}")
            
            pricing = pricing_map[plan]
            
            # Create checkout session
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price': pricing['price_id'],
                    'quantity': 1,
                }],
                mode='subscription',
                success_url=f"{settings.FRONTEND_URL}/dashboard?success=true",
                cancel_url=f"{settings.FRONTEND_URL}/pricing?canceled=true",
                customer_email=customer_email,
                metadata={
                    'tenant_id': tenant_id,
                    'plan': plan
                }
            )
            
            return {
                "id": session.id,
                "url": session.url
            }
            
        except Exception as e:
            logger.error(f"Error creating checkout session: {e}")
            raise
    
    async def cancel_subscription(self, subscription_id: str) -> bool:
        """Cancel Stripe subscription"""
        try:
            stripe.Subscription.delete(subscription_id)
            return True
        except Exception as e:
            logger.error(f"Error canceling subscription: {e}")
            raise
    
    async def handle_webhook(self, request) -> Dict[str, Any]:
        """Handle Stripe webhook events"""
        try:
            payload = await request.body()
            sig_header = request.headers.get('stripe-signature')
            
            event = stripe.Webhook.construct_event(
                payload, sig_header, self.webhook_secret
            )
            
            return event
            
        except Exception as e:
            logger.error(f"Error handling webhook: {e}")
            raise
    
    async def get_subscription(self, subscription_id: str) -> Dict[str, Any]:
        """Get Stripe subscription details"""
        try:
            subscription = stripe.Subscription.retrieve(subscription_id)
            return subscription
        except Exception as e:
            logger.error(f"Error getting subscription: {e}")
            raise
    
    async def update_subscription(
        self,
        subscription_id: str,
        new_plan: str
    ) -> Dict[str, Any]:
        """Update Stripe subscription plan"""
        try:
            # Get current subscription
            subscription = stripe.Subscription.retrieve(subscription_id)
            
            # Update subscription with new price
            updated_subscription = stripe.Subscription.modify(
                subscription_id,
                items=[{
                    'id': subscription['items']['data'][0]['id'],
                    'price': f"price_{new_plan}_monthly"
                }],
                proration_behavior='create_prorations'
            )
            
            return updated_subscription
            
        except Exception as e:
            logger.error(f"Error updating subscription: {e}")
            raise


# Global Stripe service instance
stripe_service = StripeService()
