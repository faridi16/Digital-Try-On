import os
import time
from celery import Celery

from mesh_processor import MeshProcessor
from ar_processor import ARProcessor

# Configure Celery to connect to Redis
redis_url = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/0")
celery_app = Celery("gpu_tasks", broker=redis_url, backend=redis_url)

# Initialize the MeshProcessor (Simulating loading base mesh into VRAM)
mesh_processor = MeshProcessor()

# Initialize the ARProcessor
ar_processor = ARProcessor()

@celery_app.task(name="worker.process_mode_a")
def process_mode_a(weight: float, height: float, body_shape: str):
    """
    Mode A: Parametric 3D Avatar Generation
    Uses MeshProcessor to scale base mesh and map textures.
    """
    print(f"Starting Mode A for parameters: weight={weight}, height={height}, shape={body_shape}")
    
    # Simulate processing through our fake 3D pipeline
    garment_id = "wishlist_item_999" # In reality, this would be passed from the client
    optimized_payload = mesh_processor.process_full_pipeline(weight, height, body_shape, garment_id)
    
    result = {
        "status": "success",
        "mesh_url": optimized_payload["streaming_url"],
        "metadata": optimized_payload,
        "mode": "A"
    }
    
    print("Finished Mode A processing.")
    return result

@celery_app.task(name="worker.process_mode_b")
def process_mode_b(raw_image_data: bytes, session_token: str):
    """
    Mode B: Photo-Realistic AR Processing
    Simulates single-image silhouette warping in a stateless container.
    Crucially implements the Zero Retention Policy (purging memory).
    """
    print(f"Starting Mode B processing for image of size {len(raw_image_data)} bytes. Session: {session_token}")
    
    try:
        # Simulate check for session validity
        if not session_token:
            raise ValueError("Invalid or missing session token")
            
        result = ar_processor.process_image(raw_image_data, session_token)
        return result
        
    finally:
        # Strict Zero Retention Policy enforcement simulation
        # In a real environment, this ensures memory is freed and raw data isn't persisted
        del raw_image_data
        print("ZERO RETENTION POLICY ENFORCED: Raw image data purged from memory.")
