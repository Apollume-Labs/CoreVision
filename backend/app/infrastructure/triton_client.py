from tritonclient.grpc import InferenceServerClient
from tritonclient.utils import InferenceServerException
from typing import List, Optional
import os

class TritonClient:
    """Helper class for Triton Inference Server interactions"""
    
    def __init__(self):
        self.host = os.getenv("TRITON_HOST", "triton")
        self.port = os.getenv("TRITON_GRPC_PORT", "8001")
        self.url = f"{self.host}:{self.port}"
    
    def _get_client(self) -> InferenceServerClient:
        """Get Triton gRPC client"""
        return InferenceServerClient(url=self.url)

    
    def is_server_live(self) -> bool:
        """Check if Triton server is live"""
        try:
            client = self._get_client()
            return client.is_server_live()
        except Exception:
            return False

    
    def is_server_ready(self) -> bool:
        """Check if Triton server is ready"""
        try:
            client = self._get_client()
            return client.is_server_ready()
        except Exception:
            return False
    
    def list_models(self) -> List[str]:
        """
        List all available models in Triton.
        
        Returns:
            List of model names
        """
        try:
            client = self._get_client()
            model_repo = client.get_model_repository_index()
            return [model.name for model in model_repo.models]
        except InferenceServerException as e:
            raise Exception(f"Failed to list Triton models: {str(e)}")
    
    def model_exists(self, model_name: str, model_version: str = "1") -> bool:
        """
        Check if a model exists in Triton.
        
        Args:
            model_name: Name of the model
            model_version: Version of the model
            
        Returns:
            True if model exists and is ready
        """
        try:
            client = self._get_client()
            return client.is_model_ready(model_name, model_version)
        except InferenceServerException:
            return False
    
    def get_model_metadata(self, model_name: str, model_version: str = "1") -> dict:
        """
        Get model metadata from Triton.
        
        Args:
            model_name: Name of the model
            model_version: Version of the model
            
        Returns:
            Model metadata as dict
        """
        try:
            client = self._get_client()
            metadata = client.get_model_metadata(model_name, model_version)
            return {
                "name": metadata.name,
                "versions": metadata.versions,
                "platform": metadata.platform,
                "inputs": [
                    {
                        "name": inp.name,
                        "datatype": inp.datatype,
                        "shape": inp.shape
                    }
                    for inp in metadata.inputs
                ],
                "outputs": [
                    {
                        "name": out.name,
                        "datatype": out.datatype,
                        "shape": out.shape
                    }
                    for out in metadata.outputs
                ]
            }
        except InferenceServerException as e:
            raise Exception(f"Failed to get model metadata: {str(e)}")