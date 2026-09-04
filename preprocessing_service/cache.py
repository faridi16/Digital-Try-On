import os
import uuid
from pathlib import Path

CACHE_DIR = Path("cache")
CACHE_DIR.mkdir(exist_ok=True)

def save_to_cache(image_bytes: bytes, prefix: str = "asset") -> str:
    """
    Saves the processed asset to a local cache directory (mocking a distributed cache).
    Returns the cache key/path.
    """
    asset_id = str(uuid.uuid4())
    filename = f"{prefix}_{asset_id}.png"
    filepath = CACHE_DIR / filename
    
    with open(filepath, "wb") as f:
        f.write(image_bytes)
        
    return str(filepath)
