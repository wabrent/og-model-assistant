"""
ML Inference API Router
"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any, Optional
from services.ml_inference_service import ml_inference_service

router = APIRouter(prefix="/api/ml", tags=["ML Inference"])


class InferenceRequest(BaseModel):
    model_cid: str
    model_input: Dict[str, Any]
    inference_mode: str = "TEE"


class WorkflowRequest(BaseModel):
    workflow_id: str


@router.get("/workflows")
async def list_workflows():
    """Get available ML workflows."""
    return {"workflows": ml_inference_service.get_available_workflows()}


@router.post("/infer")
async def run_inference(request: InferenceRequest):
    """Run ML inference on a model."""
    result = await ml_inference_service.run_inference(
        model_cid=request.model_cid,
        model_input=request.model_input,
        inference_mode=request.inference_mode
    )
    return result


@router.post("/workflow/run")
async def run_workflow(request: WorkflowRequest):
    """Run a workflow manually."""
    result = await ml_inference_service.run_workflow(request.workflow_id)
    return result


@router.get("/workflow/{workflow_id}/result")
async def get_workflow_result(workflow_id: str):
    """Get the latest workflow result."""
    result = await ml_inference_service.read_workflow_result(workflow_id)
    return result


# Price prediction shortcuts
@router.get("/predict/eth/volatility")
async def predict_eth_volatility():
    """Get ETH 1h volatility prediction."""
    result = await ml_inference_service.read_workflow_result("eth-1h-volatility")
    return {
        "pair": "ETH/USDT",
        "prediction_type": "1h_volatility",
        "explorer_url": f"https://explorer.opengradient.ai/address/{ml_inference_service.WORKFLOWS['eth-1h-volatility']['contract_address']}",
        **result
    }


@router.get("/predict/sui/30min")
async def predict_sui_30min():
    """Get SUI 30min return prediction."""
    result = await ml_inference_service.read_workflow_result("sui-30min-return")
    return {
        "pair": "SUI/USDT",
        "prediction_type": "30min_return",
        "explorer_url": f"https://explorer.opengradient.ai/address/{ml_inference_service.WORKFLOWS['sui-30min-return']['contract_address']}",
        **result
    }


@router.get("/predict/sui/6h")
async def predict_sui_6h():
    """Get SUI 6h return prediction."""
    result = await ml_inference_service.read_workflow_result("sui-6h-return")
    return {
        "pair": "SUI/USDT",
        "prediction_type": "6h_return",
        "explorer_url": f"https://explorer.opengradient.ai/address/{ml_inference_service.WORKFLOWS['sui-6h-return']['contract_address']}",
        **result
    }
