from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import uvicorn
from pipeline import process_image
from cache import save_to_cache

app = FastAPI(title="Asset Preprocessing Microservice")

@app.post("/preprocess")
async def preprocess_asset(file: UploadFile = File(...)):
    try:
        # Read the raw image
        raw_bytes = await file.read()
        
        # Process image pipeline
        processed_data = process_image(raw_bytes)
        
        # Save to mock user-facing cache
        img_path = save_to_cache(processed_data["standardized_image"], prefix="standardized")
        depth_path = save_to_cache(processed_data["depth_map"], prefix="depth")
        
        return JSONResponse({
            "status": "success",
            "message": "Asset successfully standardized and cached.",
            "data": {
                "standardized_image_path": img_path,
                "depth_map_path": depth_path
            }
        })
        
    except Exception as e:
        return JSONResponse({
            "status": "error",
            "message": str(e)
        }, status_code=500)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
