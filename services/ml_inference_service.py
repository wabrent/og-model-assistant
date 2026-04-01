"""
ML Inference Service - ZKML, TEE, VANILLA inference modes
"""
import opengradient as og
from typing import Dict, Any, Optional
from loguru import logger
from core.config import settings


class MLInferenceService:
    """Service for ML inference using OpenGradient."""
    
    # Official OG-ML Workflows
    WORKFLOWS = {
        "eth-1h-volatility": {
            "model_cid": "QmRhcpDXfYCKsimTmJYrAVM4Bbvck59Zb2onj3MHv9Kw5N",
            "contract_address": "0xD5629A5b95dde11e4B5772B5Ad8a13B933e33845",
            "name": "ETH 1h Volatility",
            "description": "Standard deviation of 1min returns over next hour",
            "base": "ETH",
            "quote": "USDT",
            "frequency": 3600
        },
        "sui-30min-return": {
            "model_cid": "QmY1RjD3s4XPbSeKi5TqMwbxegumenZ49t2q7TrK7Xdga4",
            "contract_address": "0xD85BA71f5701dc4C5BDf9780189Db49C6F3708D2",
            "name": "SUI 30min Return",
            "description": "30 minute price return prediction",
            "base": "SUI",
            "quote": "USDT",
            "frequency": 1800
        },
        "sui-6h-return": {
            "model_cid": "QmP4BeRjycVxfKBkFtwj5xAa7sCWyffMQznNsZnXgYHpFX",
            "contract_address": "0x3C2E4DbD653Bd30F1333d456480c1b7aB122e946",
            "name": "SUI 6h Return",
            "description": "6 hour price return prediction",
            "base": "SUI",
            "quote": "USDT",
            "frequency": 21600
        }
    }
    
    def __init__(self):
        self._alpha = None
    
    @property
    def alpha(self):
        if self._alpha is None and settings.private_key:
            try:
                self._alpha = og.Alpha(private_key=settings.private_key)
            except Exception as e:
                logger.error(f"Failed to initialize Alpha: {e}")
        return self._alpha
    
    async def run_inference(
        self,
        model_cid: str,
        model_input: Dict[str, Any],
        inference_mode: str = "TEE"
    ) -> Dict[str, Any]:
        """Run ML inference on a model."""
        try:
            if not self.alpha:
                return {"error": "Alpha not initialized - private key required"}
            
            mode_map = {
                "VANILLA": og.InferenceMode.VANILLA,
                "TEE": og.InferenceMode.TEE,
                "ZKML": og.InferenceMode.ZKML
            }
            
            mode = mode_map.get(inference_mode.upper(), og.InferenceMode.TEE)
            
            result = self.alpha.infer(
                model_cid=model_cid,
                model_input=model_input,
                inference_mode=mode
            )
            
            return {
                "status": "success",
                "model_cid": model_cid,
                "inference_mode": inference_mode,
                "output": str(result.model_output)
            }
        except Exception as e:
            logger.error(f"Inference error: {e}")
            return {"error": str(e)}
    
    async def run_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Run a workflow manually."""
        try:
            if not self.alpha:
                return {"error": "Alpha not initialized"}
            
            if workflow_id not in self.WORKFLOWS:
                return {"error": "Workflow not found"}
            
            workflow = self.WORKFLOWS[workflow_id]
            contract_address = workflow["contract_address"]
            
            self.alpha.run_workflow(contract_address)
            
            return {
                "status": "executed",
                "workflow_id": workflow_id,
                "name": workflow["name"]
            }
        except Exception as e:
            logger.error(f"Workflow run error: {e}")
            return {"error": str(e)}
    
    async def read_workflow_result(self, workflow_id: str) -> Dict[str, Any]:
        """Read the latest workflow result."""
        try:
            if not self.alpha:
                return {"error": "Alpha not initialized"}
            
            if workflow_id not in self.WORKFLOWS:
                return {"error": "Workflow not found"}
            
            workflow = self.WORKFLOWS[workflow_id]
            contract_address = workflow["contract_address"]
            
            result = self.alpha.read_workflow_result(contract_address)
            
            return {
                "workflow_id": workflow_id,
                "name": workflow["name"],
                "result": str(result),
                "contract_address": contract_address
            }
        except Exception as e:
            logger.error(f"Read workflow result error: {e}")
            return {"error": str(e)}
    
    def get_available_workflows(self) -> list:
        """Get list of available workflows."""
        return [
            {
                "id": wid,
                **wdata
            }
            for wid, wdata in self.WORKFLOWS.items()
        ]


ml_inference_service = MLInferenceService()
