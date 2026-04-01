"""
Proof of AI Certificate API Router
"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from services.proof_of_ai import proof_of_ai

router = APIRouter(prefix="/api/certificate", tags=["Proof of AI"])


class CertificateRequest(BaseModel):
    prompt: str
    response: str
    model: str
    session_id: str
    payment_hash: Optional[str] = None


@router.post("/generate")
async def generate_certificate(request: CertificateRequest):
    """Generate a Proof of AI certificate."""
    cert = proof_of_ai.generate(
        prompt=request.prompt,
        response=request.response,
        model=request.model,
        session_id=request.session_id,
        payment_hash=request.payment_hash
    )
    return cert


@router.post("/html")
async def generate_html_certificate(request: CertificateRequest):
    """Generate an HTML certificate card."""
    cert = proof_of_ai.generate(
        prompt=request.prompt,
        response=request.response,
        model=request.model,
        session_id=request.session_id,
        payment_hash=request.payment_hash
    )
    return {"html": proof_of_ai.to_html(cert), "certificate": cert}
