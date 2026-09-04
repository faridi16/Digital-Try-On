import io
from PIL import Image
from rembg import remove
from transformers import pipeline

# Initialize MiDaS for depth estimation
# Note: For production, we'd load this once at startup and use a GPU model.
depth_estimator = pipeline("depth-estimation", model="Intel/dpt-large")

def process_image(image_bytes: bytes) -> dict:
    """
    Processes the raw image:
    1. Removes background (creates alpha mask).
    2. Normalizes dimensions (e.g., 512x512 max).
    3. Generates a depth map.
    Returns a dictionary with 'standardized_image' and 'depth_map' as bytes.
    """
    # 1. Background Removal
    no_bg_bytes = remove(image_bytes)
    
    # 2. Normalization
    img = Image.open(io.BytesIO(no_bg_bytes)).convert("RGBA")
    img.thumbnail((512, 512), Image.Resampling.LANCZOS)
    
    # Convert back to bytes for caching
    out_img_io = io.BytesIO()
    img.save(out_img_io, format="PNG")
    processed_image_bytes = out_img_io.getvalue()
    
    # 3. Depth Map Generation
    # MiDaS requires RGB image
    rgb_img = img.convert("RGB")
    depth_result = depth_estimator(rgb_img)
    depth_map = depth_result["depth"]
    
    # Convert depth map to bytes
    depth_io = io.BytesIO()
    depth_map.save(depth_io, format="PNG")
    depth_bytes = depth_io.getvalue()
    
    return {
        "standardized_image": processed_image_bytes,
        "depth_map": depth_bytes
    }
