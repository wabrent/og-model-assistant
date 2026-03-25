"""
API Router for token operations.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any

from core.database import get_db
from models.schemas import BaseModel
from services.token_service import token_service, PRICING, PURCHASE_PACKAGES

router = APIRouter(prefix="/api/tokens", tags=["Tokens"])


class TokenBalanceResponse(BaseModel):
    user_id: str
    balance: float
    total_purchased: float
    total_spent: float


class TokenPurchaseRequest(BaseModel):
    package_id: str


class TokenPurchaseResponse(BaseModel):
    success: bool
    message: str
    total_tokens: float
    new_balance: float


@router.get("/balance")
async def get_balance(
    user_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get user token balance."""
    try:
        user = await token_service.get_or_create_user(db, user_id)
        return {
            "user_id": user.user_id,
            "balance": user.balance,
            "total_purchased": user.total_purchased,
            "total_spent": user.total_spent,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pricing")
async def get_pricing():
    """Get current pricing and packages."""
    return {
        "pricing": PRICING,
        "packages": PURCHASE_PACKAGES,
    }


@router.get("/transactions")
async def get_transactions(
    user_id: str,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
):
    """Get user transaction history."""
    try:
        transactions = await token_service.get_transactions(db, user_id, limit)
        return {"transactions": transactions, "total": len(transactions)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/purchase", response_model=TokenPurchaseResponse)
async def purchase_tokens(
    request: TokenPurchaseRequest,
    user_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Purchase a token package."""
    try:
        success, message, total_tokens = await token_service.purchase_package(
            db, user_id, request.package_id
        )
        
        if not success:
            raise HTTPException(status_code=400, detail=message)
        
        # Get updated balance
        user = await token_service.get_or_create_user(db, user_id)
        
        return {
            "success": success,
            "message": message,
            "total_tokens": total_tokens,
            "new_balance": user.balance,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/add-bonus")
async def add_bonus_tokens(
    user_id: str,
    amount: float = 10.0,
    description: str = "Bonus tokens",
    db: AsyncSession = Depends(get_db),
):
    """Add bonus tokens (for promotions, rewards, etc.)."""
    try:
        user = await token_service.add_tokens(
            db, user_id, amount, "bonus", description
        )
        return {
            "success": True,
            "message": f"Added {amount} bonus tokens",
            "new_balance": user.balance,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/faucet/claim")
async def claim_faucet(
    user_id: str,
    wallet_address: str = "0xfa13a15a2fb420e2313918496b5b05427ed8e31a",
    db: AsyncSession = Depends(get_db),
):
    """Claim tokens from OpenGradient faucet (every 5 hours)."""
    try:
        success, message, tokens = await token_service.claim_faucet_tokens(
            db, user_id, wallet_address
        )
        
        if not success:
            raise HTTPException(status_code=429, detail=message)
        
        return {
            "success": success,
            "message": message,
            "tokens_claimed": tokens,
            "wallet": wallet_address,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/faucet/status")
async def get_faucet_status(
    user_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get faucet claim status."""
    try:
        status = await token_service.get_faucet_status(db, user_id)
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
