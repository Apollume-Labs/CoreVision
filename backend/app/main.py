from tritonclient.utils import InferenceServerException
import tritonclient.grpc as grpcclient
from fastapi import FastAPI, HTTPException
from app.api.v1 import cameras
import os

TRITON_HOST = os.getenv("TRITON_HOST", "triton")
TRITON_GRPC_PORT = os.getenv("TRITON_GRPC_PORT", "8001")

app = FastAPI(
    title="CoreVision Backend API",
    description="API for CoreVision application backend services.",
    version="1.0.0",
)

app.include_router(cameras.router, prefix="/api/v1")

@app.get("/health")
async def health():
    """Backend health check"""
    return {
        "status": "healthy",
        "service": "corevision-backend",
        "version": "0.1.0"
    }

@app.get("/health/triton")
async def triton_health():
    """Check Triton inference server connectivity"""
    try:
        triton_client = grpcclient.InferenceServerClient(
            url=f"{TRITON_HOST}:{TRITON_GRPC_PORT}"
        )
        
        # Check if server is live
        if triton_client.is_server_live():
            # Get server metadata
            metadata = triton_client.get_server_metadata()
            
            return {
                "status": "healthy",
                "triton_host": TRITON_HOST,
                "triton_port": TRITON_GRPC_PORT,
                "server_name": metadata.name,
                "server_version": metadata.version,
                "connected": True
            }
        else:
            raise HTTPException(
                status_code=503,
                detail="Triton server is not live"
            )
            
    except InferenceServerException as e:
        raise HTTPException(
            status_code=503,
            detail=f"Triton connection failed: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {str(e)}"
        )