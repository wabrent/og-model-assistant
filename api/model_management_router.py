"""
Model Management API Router
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import Optional
from services.model_management_service import model_management_service

router = APIRouter(prefix="/api/models/manage", tags=["Model Management"])


class CreateModelRequest(BaseModel):
    model_name: str
    model_desc: str


class CreateVersionRequest(BaseModel):
    model_name: str
    notes: str


@router.post("/create")
async def create_model(request: CreateModelRequest):
    """Create a new model repository on OpenGradient."""
    result = await model_management_service.create_model(
        model_name=request.model_name,
        model_desc=request.model_desc
    )
    return result


@router.post("/version")
async def create_version(request: CreateVersionRequest):
    """Create a new version for a model."""
    result = await model_management_service.create_version(
        model_name=request.model_name,
        notes=request.notes
    )
    return result


@router.post("/upload/{model_name}/{version}")
async def upload_file(
    model_name: str,
    version: str,
    file: UploadFile = File(...)
):
    """Upload a file to a model repository."""
    # Validate file size (max 100 MB)
    MAX_UPLOAD_SIZE = 100 * 1024 * 1024  # 100 MB
    content = await file.read(MAX_UPLOAD_SIZE + 1)
    if len(content) > MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"File size exceeds maximum allowed size of {MAX_UPLOAD_SIZE // (1024*1024)} MB"
        )
    
    # Save file temporarily
    import tempfile
    import os
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
        tmp.write(content)
        tmp_path = tmp.name
    
    try:
        result = await model_management_service.upload_file(
            model_path=tmp_path,
            model_name=model_name,
            version=version
        )
        return result
    finally:
        os.unlink(tmp_path)


@router.get("/files/{model_name}/{version}")
async def list_files(model_name: str, version: str):
    """List files in a model repository."""
    files = await model_management_service.list_files(model_name, version)
    return {"files": files, "model_name": model_name, "version": version}
