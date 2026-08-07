import stripe
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import os

from backend.models.database import get_db
from backend.models.orm import User, Organization
from backend.security.auth import get_current_user, get_current_admin
from backend.config import settings

# Usually these come from config, fallback to os.getenv or mock keys
stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "sk_test_mock")

router = APIRouter()

class CheckoutRequest(BaseModel):
    plan: str # "pro" or "enterprise"

@router.post("/checkout")
async def create_checkout_session(
    req: CheckoutRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not part of an organization")
        
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': f'DevShield AI X - {req.plan.capitalize()} Plan',
                    },
                    'unit_amount': 4900 if req.plan == "pro" else 19900,
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=f"{os.getenv('NEXT_PUBLIC_FRONTEND_URL', 'http://localhost:3000')}/billing?success=true",
            cancel_url=f"{os.getenv('NEXT_PUBLIC_FRONTEND_URL', 'http://localhost:3000')}/billing?canceled=true",
            client_reference_id=str(current_user.organization_id)
        )
        return {"checkout_url": session.url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/webhook")
async def stripe_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature', '')
    endpoint_secret = os.getenv('STRIPE_WEBHOOK_SECRET', 'whsec_mock')
    
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        # For local testing without valid signature
        if endpoint_secret == 'whsec_mock':
            import json
            event = json.loads(payload.decode('utf-8'))
        else:
            raise HTTPException(status_code=400, detail="Invalid signature")

    if event.get('type') == 'checkout.session.completed':
        session = event['data']['object']
        org_id = session.get('client_reference_id')
        
        if org_id:
            result = await db.execute(select(Organization).filter(Organization.id == int(org_id)))
            org = result.scalars().first()
            if org:
                org.subscription_tier = "pro"
                await db.commit()
            
    return {"status": "success"}

class AdminGrantRequest(BaseModel):
    organization_id: int
    plan: str

@router.post("/admin-grant")
async def admin_grant_subscription(
    req: AdminGrantRequest,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """Allow an admin to allocate a free subscription (pro or enterprise) to an organization"""
    result = await db.execute(select(Organization).filter(Organization.id == req.organization_id))
    org = result.scalars().first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
        
    org.subscription_tier = req.plan
    await db.commit()
    return {"status": "success", "message": f"Successfully granted {req.plan} subscription to {org.name}"}
