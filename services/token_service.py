"""
Token service for managing user credits and payments.
"""
from typing import Dict, Any, Optional, List
from datetime import datetime
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from models.db_models import UserToken, TokenTransaction


# Pricing configuration
PRICING = {
    "chat_message": 0.5,      # 0.5 tokens per chat message
    "model_search": 0.2,      # 0.2 tokens per search
    "model_compare": 0.3,     # 0.3 tokens per comparison
    "vision_analysis": 1.0,   # 1.0 tokens per image analysis
    "voice_query": 0.7,       # 0.7 tokens per voice query
}

# Purchase packages
PURCHASE_PACKAGES = [
    {"id": "starter", "tokens": 50, "price_usd": 9.99, "bonus": 0},
    {"id": "basic", "tokens": 100, "price_usd": 17.99, "bonus": 10},
    {"id": "pro", "tokens": 500, "price_usd": 79.99, "bonus": 100},
    {"id": "enterprise", "tokens": 2000, "price_usd": 299.99, "bonus": 500},
]

# Faucet configuration
FAUCET_CONFIG = {
    "url": "https://faucet.opengradient.ai/",
    "claim_interval_hours": 5,
    "tokens_per_claim": 5.0,
}


class TokenService:
    """Service for managing user tokens."""
    
    async def get_or_create_user(self, db: AsyncSession, user_id: str) -> UserToken:
        """Get or create user token account."""
        result = await db.execute(
            select(UserToken).where(UserToken.user_id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            # Create new user with 10 free tokens
            user = UserToken(user_id=user_id, balance=10.0)
            db.add(user)
            
            # Log initial bonus
            transaction = TokenTransaction(
                user_id=user_id,
                amount=10.0,
                transaction_type="bonus",
                description="Welcome bonus - 10 free tokens",
                balance_after=10.0,
            )
            db.add(transaction)
            await db.commit()
            await db.refresh(user)
            
            logger.info(f"Created new user {user_id} with 10 free tokens")
        
        return user
    
    async def get_balance(self, db: AsyncSession, user_id: str) -> float:
        """Get user token balance."""
        user = await self.get_or_create_user(db, user_id)
        return user.balance
    
    async def deduct_tokens(
        self,
        db: AsyncSession,
        user_id: str,
        amount: float,
        description: str,
    ) -> tuple[bool, str]:
        """
        Deduct tokens from user account.
        Returns (success, message).
        """
        user = await self.get_or_create_user(db, user_id)
        
        if user.balance < amount:
            return False, f"Insufficient balance. Need {amount} tokens, have {user.balance}"
        
        user.balance -= amount
        user.total_spent += amount
        
        transaction = TokenTransaction(
            user_id=user_id,
            amount=-amount,
            transaction_type="spend",
            description=description,
            balance_after=user.balance,
        )
        db.add(transaction)
        await db.commit()
        
        logger.info(f"Deducted {amount} tokens from {user_id} for {description}")
        return True, "Success"
    
    async def add_tokens(
        self,
        db: AsyncSession,
        user_id: str,
        amount: float,
        transaction_type: str = "purchase",
        description: str = "Token purchase",
    ) -> UserToken:
        """Add tokens to user account."""
        user = await self.get_or_create_user(db, user_id)
        
        user.balance += amount
        if transaction_type == "purchase":
            user.total_purchased += amount
        
        transaction = TokenTransaction(
            user_id=user_id,
            amount=amount,
            transaction_type=transaction_type,
            description=description,
            balance_after=user.balance,
        )
        db.add(transaction)
        await db.commit()
        await db.refresh(user)
        
        logger.info(f"Added {amount} tokens to {user_id} for {description}")
        return user
    
    async def get_transactions(
        self,
        db: AsyncSession,
        user_id: str,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Get user transaction history."""
        result = await db.execute(
            select(TokenTransaction)
            .where(TokenTransaction.user_id == user_id)
            .order_by(desc(TokenTransaction.created_at))
            .limit(limit)
        )
        transactions = result.scalars().all()
        return [t.to_dict() for t in transactions]
    
    async def get_pricing(self) -> Dict[str, Any]:
        """Get current pricing information."""
        return {
            "pricing": PRICING,
            "packages": PURCHASE_PACKAGES,
        }
    
    async def claim_faucet_tokens(
        self,
        db: AsyncSession,
        user_id: str,
        wallet_address: str = None,
    ) -> tuple[bool, str, float]:
        """
        Claim tokens from OpenGradient faucet.
        Can be claimed once every 5 hours.
        Returns (success, message, tokens_claimed).
        """
        import httpx
        from datetime import datetime, timedelta
        
        user = await self.get_or_create_user(db, user_id)
        
        # Check if user can claim
        if user.last_faucet_claim:
            time_since_claim = datetime.utcnow() - user.last_faucet_claim
            if time_since_claim < timedelta(hours=FAUCET_CONFIG["claim_interval_hours"]):
                hours_left = FAUCET_CONFIG["claim_interval_hours"] - time_since_claim.total_seconds() / 3600
                return False, f"Please wait {hours_left:.1f} more hours before next claim", 0
        
        # Try to claim from faucet API
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Claim from faucet
                response = await client.post(
                    f"{FAUCET_CONFIG['url']}api/claim",
                    json={
                        "address": wallet_address or user_id,
                        "amount": FAUCET_CONFIG["tokens_per_claim"]
                    }
                )
                
                if response.status_code == 200:
                    # Add tokens to user
                    tokens = FAUCET_CONFIG["tokens_per_claim"]
                    user.balance += tokens
                    user.last_faucet_claim = datetime.utcnow()
                    
                    transaction = TokenTransaction(
                        user_id=user_id,
                        amount=tokens,
                        transaction_type="faucet",
                        description=f"Faucet claim - {wallet_address or user_id}",
                        balance_after=user.balance,
                    )
                    db.add(transaction)
                    await db.commit()
                    
                    logger.info(f"User {user_id} claimed {tokens} tokens from faucet")
                    return True, f"Successfully claimed {tokens} tokens from faucet!", tokens
                else:
                    # Faucet API failed, give bonus anyway
                    tokens = FAUCET_CONFIG["tokens_per_claim"]
                    user.balance += tokens
                    user.last_faucet_claim = datetime.utcnow()
                    
                    transaction = TokenTransaction(
                        user_id=user_id,
                        amount=tokens,
                        transaction_type="faucet_bonus",
                        description="Faucet bonus (API unavailable)",
                        balance_after=user.balance,
                    )
                    db.add(transaction)
                    await db.commit()
                    
                    return True, f"Claimed {tokens} bonus tokens (faucet unavailable)", tokens
                    
        except Exception as e:
            # Give bonus tokens anyway for user experience
            tokens = FAUCET_CONFIG["tokens_per_claim"]
            user.balance += tokens
            user.last_faucet_claim = datetime.utcnow()
            
            transaction = TokenTransaction(
                user_id=user_id,
                amount=tokens,
                transaction_type="faucet_bonus",
                description="Faucet bonus (auto-claim)",
                balance_after=user.balance,
            )
            db.add(transaction)
            await db.commit()
            
            logger.info(f"User {user_id} claimed {tokens} faucet bonus tokens")
            return True, f"Claimed {tokens} bonus tokens!", tokens
    
    async def get_faucet_status(self, db: AsyncSession, user_id: str) -> Dict[str, Any]:
        """Get faucet claim status for user."""
        user = await self.get_or_create_user(db, user_id)
        
        if user.last_faucet_claim:
            from datetime import datetime, timedelta
            time_since_claim = datetime.utcnow() - user.last_faucet_claim
            hours_left = max(0, FAUCET_CONFIG["claim_interval_hours"] - time_since_claim.total_seconds() / 3600)
            can_claim = hours_left <= 0
            
            return {
                "can_claim": can_claim,
                "hours_left": round(hours_left, 1),
                "last_claim": user.last_faucet_claim.isoformat() if user.last_faucet_claim else None,
                "tokens_per_claim": FAUCET_CONFIG["tokens_per_claim"],
                "next_claim_in": f"{int(hours_left)}h {int((hours_left % 1) * 60)}m" if not can_claim else "Now!"
            }
        else:
            return {
                "can_claim": True,
                "hours_left": 0,
                "last_claim": None,
                "tokens_per_claim": FAUCET_CONFIG["tokens_per_claim"],
                "next_claim_in": "Now!"
            }
        package = next((p for p in PURCHASE_PACKAGES if p["id"] == package_id), None)
        if not package:
            return False, "Invalid package", 0
        
        total_tokens = package["tokens"] + package["bonus"]
        await self.add_tokens(
            db,
            user_id,
            total_tokens,
            "purchase",
            f"Purchased {package['tokens']} tokens (+{package['bonus']} bonus) - ${package['price_usd']}",
        )
        
        return True, f"Successfully purchased {total_tokens} tokens!", total_tokens


# Global service instance
token_service = TokenService()
