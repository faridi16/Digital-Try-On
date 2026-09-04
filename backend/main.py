from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image, ImageDraw
import io
import base64
import time

app = FastAPI(title="Digital Fitting Room Mock API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory mock task store
TASKS = {}

def get_skin_color_rgb(skin_tone_name):
    tones = {
        "Fair": (255, 224, 189),
        "Light": (255, 205, 148),
        "Medium": (224, 172, 105),
        "Olive": (198, 134, 66),
        "Tan": (141, 85, 36),
        "Dark": (104, 58, 20)
    }
    return tones.get(skin_tone_name, (224, 172, 105))

def generate_mock_mesh_b64(height, shape, skin_tone):
    img = Image.new('RGB', (400, 600), color=(240, 245, 250))
    d = ImageDraw.Draw(img)
    skin_rgb = get_skin_color_rgb(skin_tone)
    
    h_scale = height / 170.0
    width = 160
    if shape == "broad": width = 190
    elif shape == "slim": width = 130
        
    box_height = 300 * h_scale
    cx, cy = 200, 350
    
    head_radius = 45
    d.ellipse([cx - head_radius, cy - box_height/2 - head_radius*2, cx + head_radius, cy - box_height/2], fill=skin_rgb)
    d.rounded_rectangle([cx - width/2, cy - box_height/2 + 5, cx + width/2, cy + box_height/2], radius=40, fill=skin_rgb)
    d.text((15, 15), f"Generated Avatar\\nHeight: {height}cm\\nShape: {shape.title()}\\nSkin Tone: {skin_tone}", fill=(50, 50, 50))
    
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return f"data:image/png;base64,{img_str}"

def mock_warp_b64():
    # Return a static blue mock image for the warp
    img = Image.new("RGBA", (300, 400), (0, 114, 178, 120))
    d = ImageDraw.Draw(img)
    d.text((20, 20), "AR Warp Applied (Mock)", fill=(255, 255, 255, 255))
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return f"data:image/png;base64,{img_str}"

@app.post("/mode-a/generate")
async def generate_avatar(
    height: float = Form(170.0), 
    body_shape: str = Form("medium"), 
    weight: str = Form("Medium") 
):
    task_id = f"task_{int(time.time())}"
    b64_img = generate_mock_mesh_b64(height, body_shape, weight)
    TASKS[task_id] = {"status": "SUCCESS", "result": {"mesh_url": b64_img}}
    return {"task_id": task_id, "status": "QUEUED"}

@app.post("/mode-b/warp")
async def warp_photo(file: UploadFile = File(...)):
    task_id = f"task_{int(time.time())}"
    b64_img = mock_warp_b64()
    TASKS[task_id] = {"status": "SUCCESS", "result": {"asset_url": b64_img}}
    return {"task_id": task_id, "status": "QUEUED"}

@app.get("/tasks/{task_id}")
def get_task(task_id: str):
    # Simulate a 3-second delay on the first poll
    # In a real async system, the worker handles this. Here we just return SUCCESS instantly since polling handles delay.
    task = TASKS.get(task_id)
    if task:
        return task
    return {"status": "FAILURE", "error": "Task not found"}
