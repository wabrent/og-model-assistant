"""
Model Management Service - upload, version, manage models on OpenGradient
"""
import opengradient as og
from typing import List, Dict, Any, Optional
from loguru import logger
from core.config import settings


class ModelManagementService:
    """Service for managing models on OpenGradient Model Hub."""
    
    def __init__(self):
        self._hub = None
    
    @property
    def hub(self):
        if self._hub is None:
            try:
                # Initialize with credentials if available
                self._hub = og.ModelHub(
                    email=settings.og_email,
                    password=settings.og_password
                )
            except Exception as e:
                logger.error(f"Failed to initialize ModelHub: {e}")
        return self._hub
    
    async def create_model(self, model_name: str, model_desc: str) -> Dict[str, Any]:
        """Create a new model repository."""
        try:
            if not self.hub:
                return {"error": "ModelHub not initialized"}
            
            self.hub.create_model(model_name=model_name, model_desc=model_desc)
            return {"status": "created", "model_name": model_name}
        except Exception as e:
            logger.error(f"Create model error: {e}")
            return {"error": str(e)}
    
    async def create_version(self, model_name: str, notes: str) -> Dict[str, Any]:
        """Create a new version for a model."""
        try:
            if not self.hub:
                return {"error": "ModelHub not initialized"}
            
            version = self.hub.create_version(model_name=model_name, notes=notes)
            return {"status": "created", "version": version}
        except Exception as e:
            logger.error(f"Create version error: {e}")
            return {"error": str(e)}
    
    async def upload_file(self, model_path: str, model_name: str, version: str) -> Dict[str, Any]:
        """Upload a file to a model repository."""
        try:
            if not self.hub:
                return {"error": "ModelHub not initialized"}
            
            self.hub.upload(model_path=model_path, model_name=model_name, version=version)
            return {"status": "uploaded", "model_name": model_name, "version": version}
        except Exception as e:
            logger.error(f"Upload file error: {e}")
            return {"error": str(e)}
    
    async def list_files(self, model_name: str, version: str) -> List[str]:
        """List files in a model repository."""
        try:
            if not self.hub:
                return []
            
            files = self.hub.list_files(model_name=model_name, version=version)
            return files
        except Exception as e:
            logger.error(f"List files error: {e}")
            return []


model_management_service = ModelManagementService()
