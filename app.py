import streamlit as st
import time
from PIL import Image, ImageDraw, ImageFont
import io

st.set_page_config(
    page_title="Digital Fitting Room",
    page_icon="👕",
    layout="centered"
)

st.title("Myntra Digital Fitting Room 👕")
st.markdown("Welcome to the **Digital Fitting Room (MVP)**! Choose a mode below to generate your digital avatar or test AR Try-On.")

tab1, tab2 = st.tabs(["🧍 AI Avatar (Parametric)", "📸 AR Photo Try-On"])

def generate_mock_mesh_image(weight, height, shape):
    """Generates a simple mock visualization of a 3D bounding box for the avatar."""
    img = Image.new('RGB', (400, 600), color = (40, 44, 52))
    d = ImageDraw.Draw(img)
    
    # Calculate mock proportions
    h_scale = height / 170.0
    w_scale = weight / 65.0
    
    width = 150 * w_scale
    if shape == "broad":
        width *= 1.2
    elif shape == "slim":
        width *= 0.8
        
    box_height = 400 * h_scale
    
    # Draw simple bounding box wireframe
    x1 = 200 - (width/2)
    x2 = 200 + (width/2)
    y1 = 300 - (box_height/2)
    y2 = 300 + (box_height/2)
    
    d.rectangle([x1, y1, x2, y2], outline=(100, 200, 255), width=3)
    d.line([x1, y1, x2, y2], fill=(100, 200, 255), width=1)
    d.line([x2, y1, x1, y2], fill=(100, 200, 255), width=1)
    
    d.text((10, 10), f"Generated Mesh:\\nHeight: {height}cm\\nWeight: {weight}kg\\nShape: {shape.title()}", fill=(255,255,255))
    return img

def mock_warp_image(uploaded_file):
    """Simulates background removal and clothing warp"""
    try:
        original = Image.open(uploaded_file).convert("RGBA")
        
        # Create a mock green overlay to simulate clothing warp mask
        overlay = Image.new("RGBA", original.size, (0, 255, 100, 100))
        result = Image.alpha_composite(original, overlay)
        
        # Add text
        d = ImageDraw.Draw(result)
        d.text((20, 20), "AR Warp Applied (MVP Mock)", fill=(255, 255, 255, 255))
        return result
    except Exception as e:
        st.error(f"Error processing image: {e}")
        return None

# --- MODE A: AI AVATAR ---
with tab1:
    st.subheader("Generate your Parametric Avatar")
    st.markdown("Enter your measurements to generate a structural 3D bounding mesh.")
    
    col1, col2 = st.columns(2)
    with col1:
        height = st.slider("Height (cm)", min_value=130, max_value=220, value=170)
        shape = st.selectbox("Body Shape", ["hourglass", "pear", "apple", "rectangle", "broad", "slim"])
    with col2:
        weight = st.slider("Weight (kg)", min_value=40, max_value=140, value=65)
        
    if st.button("Generate 3D Avatar", type="primary"):
        with st.spinner("Initializing GPU Clusters & Generating Mesh... (Simulating 3s process)"):
            time.sleep(3) # Simulate heavy ML workload
            mock_img = generate_mock_mesh_image(weight, height, shape)
            
        st.success("Avatar Generated Successfully!")
        st.image(mock_img, caption="Parametric 3D Bounding Box (Mock)", use_container_width=True)


# --- MODE B: AR PHOTO ---
with tab2:
    st.subheader("AR Photo Try-On")
    st.markdown("Upload a full-body photo to simulate high-fidelity AR clothing drape.")
    
    uploaded_file = st.file_uploader("Upload a full-body photo", type=["png", "jpg", "jpeg"])
    
    if uploaded_file is not None:
        st.image(uploaded_file, caption="Original Photo", width=300)
        
        if st.button("Process AR Try-On", type="primary"):
            with st.spinner("Segmenting body and computing depth warp... (Simulating 3s process)"):
                time.sleep(3) # Simulate heavy ML workload
                result_img = mock_warp_image(uploaded_file)
                
            if result_img:
                st.success("AR Warp Applied Successfully!")
                st.image(result_img, caption="Warped Result (Mock)", use_container_width=True)
