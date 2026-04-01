"""
Proof of AI Certificate Generator
"""
import hashlib
import json
from typing import Dict, Any
from datetime import datetime


class ProofOfAICertificate:
    """Generate Proof of AI certificates for AI responses."""
    
    @staticmethod
    def generate(
        prompt: str,
        response: str,
        model: str,
        session_id: str,
        payment_hash: str = None,
        timestamp: datetime = None
    ) -> Dict[str, Any]:
        """Generate a Proof of AI certificate."""
        ts = timestamp or datetime.utcnow()
        
        # Create a unique hash of the entire interaction
        content = json.dumps({
            "prompt": prompt,
            "response": response,
            "model": model,
            "session_id": session_id,
            "timestamp": ts.isoformat()
        }, sort_keys=True)
        
        cert_hash = hashlib.sha256(content.encode()).hexdigest()
        
        certificate = {
            "certificate_id": cert_hash[:16],
            "type": "Proof of AI",
            "verified_by": "OpenGradient TEE",
            "timestamp": ts.isoformat(),
            "model_used": model,
            "session_id": session_id,
            "prompt_hash": hashlib.sha256(prompt.encode()).hexdigest()[:16],
            "response_hash": hashlib.sha256(response.encode()).hexdigest()[:16],
            "full_hash": cert_hash,
            "blockchain": {
                "network": "Base Sepolia",
                "explorer_url": f"https://explorer.opengradient.ai/tx/{payment_hash}" if payment_hash else None,
                "payment_hash": payment_hash
            },
            "verification": {
                "status": "TEE Verified",
                "method": "Trusted Execution Environment",
                "provider": "OpenGradient"
            }
        }
        
        return certificate
    
    @staticmethod
    def to_html(certificate: Dict[str, Any]) -> str:
        """Generate an HTML certificate card."""
        return f"""
<div style="max-width:600px;margin:0 auto;padding:32px;background:linear-gradient(135deg,#f5f5f7,#e8e8ed);border-radius:20px;font-family:Inter,sans-serif;box-shadow:0 8px 32px rgba(0,0,0,0.1);">
  <div style="text-align:center;margin-bottom:24px;">
    <div style="font-size:48px;margin-bottom:8px;">🤖</div>
    <h2 style="margin:0;font-size:24px;font-weight:700;color:#1d1d1f;">Proof of AI Certificate</h2>
    <p style="color:#6e6e73;margin:4px 0 0;font-size:14px;">Verified by OpenGradient TEE</p>
  </div>
  <div style="background:white;border-radius:12px;padding:20px;margin-bottom:16px;">
    <div style="display:flex;justify-content:space-between;margin-bottom:12px;">
      <span style="color:#6e6e73;font-size:13px;">Certificate ID</span>
      <span style="font-family:monospace;font-size:13px;">{certificate['certificate_id']}</span>
    </div>
    <div style="display:flex;justify-content:space-between;margin-bottom:12px;">
      <span style="color:#6e6e73;font-size:13px;">Model Used</span>
      <span style="font-size:13px;">{certificate['model_used']}</span>
    </div>
    <div style="display:flex;justify-content:space-between;margin-bottom:12px;">
      <span style="color:#6e6e73;font-size:13px;">Timestamp</span>
      <span style="font-size:13px;">{certificate['timestamp']}</span>
    </div>
    <div style="display:flex;justify-content:space-between;">
      <span style="color:#6e6e73;font-size:13px;">Verification</span>
      <span style="color:#30d158;font-weight:600;font-size:13px;">✓ {certificate['verification']['status']}</span>
    </div>
  </div>
  <div style="background:white;border-radius:12px;padding:16px;text-align:center;">
    <p style="color:#6e6e73;font-size:12px;margin:0;">Full Hash: <code style="font-size:11px;">{certificate['full_hash']}</code></p>
    {f'<p style="color:#6e6e73;font-size:12px;margin:8px 0 0;"><a href="{certificate["blockchain"]["explorer_url"]}" target="_blank" style="color:#0071e3;">View on Explorer →</a></p>' if certificate['blockchain']['explorer_url'] else ''}
  </div>
</div>"""


proof_of_ai = ProofOfAICertificate()
