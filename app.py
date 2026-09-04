import streamlit as st
import time
from PIL import Image, ImageDraw
import io

st.set_page_config(
    page_title="Digital Fitting Room",
    page_icon="👕",
    layout="centered"
)

st.title("Myntra Digital Fitting Room 👕")
st.markdown("Welcome to the **Digital Fitting Room (MVP)**! Choose a mode below to generate your digital avatar or test AR Try-On.")

tab1, tab2 = st.tabs(["🧍 AI Avatar (Parametric)", "📸 AR Photo Try-On"])

def get_skin_color_rgb(skin_tone_name):
    # Hex approximations for common skin tones
    tones = {
        "Fair": (255, 224, 189),
        "Light": (255, 205, 148),
        "Medium": (224, 172, 105),
        "Olive": (198, 134, 66),
        "Tan": (141, 85, 36),
        "Dark": (104, 58, 20)
    }
    return tones.get(skin_tone_name, (224, 172, 105))

def generate_mock_mesh_image(height, shape, skin_tone):
    """Generates a mock 3D avatar silhouette filled with the selected skin tone."""
    # Create a nice studio background
    img = Image.new('RGB', (400, 600), color=(240, 245, 250))
    d = ImageDraw.Draw(img)
    
    skin_rgb = get_skin_color_rgb(skin_tone)
    
    # Calculate mock proportions
    h_scale = height / 170.0
    width = 160
    if shape == "broad":
        width = 190
    elif shape == "slim":
        width = 130
        
    box_height = 300 * h_scale
    
    # Center points
    cx, cy = 200, 350
    
    # Draw Head
    head_radius = 45
    d.ellipse([cx - head_radius, cy - box_height/2 - head_radius*2, cx + head_radius, cy - box_height/2], fill=skin_rgb)
    
    # Draw Torso
    d.rounded_rectangle([cx - width/2, cy - box_height/2 + 5, cx + width/2, cy + box_height/2], radius=40, fill=skin_rgb)
    
    # Add text overlay
    d.text((15, 15), f"Generated Avatar\\nHeight: {height}cm\\nShape: {shape.title()}\\nSkin Tone: {skin_tone}", fill=(50, 50, 50))
    
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
    st.markdown("Enter your measurements to generate your digital double.")
    
    col1, col2 = st.columns(2)
    with col1:
        height = st.slider("Height (cm)", min_value=130, max_value=220, value=170)
        shape = st.selectbox("Body Shape", ["hourglass", "pear", "apple", "rectangle", "broad", "slim"])
    with col2:
        skin_tone = st.selectbox("Skin Tone (Color Analysis)", ["Fair", "Light", "Medium", "Olive", "Tan", "Dark"], index=2)
        
    if st.button("Generate 3D Avatar", type="primary"):
        with st.spinner("Initializing GPU Clusters & Generating Mesh... (Simulating 3s process)"):
            time.sleep(3) # Simulate heavy ML workload
            mock_img = generate_mock_mesh_image(height, shape, skin_tone)
            
        st.success("Avatar Generated Successfully!")
        st.image(mock_img, caption="Parametric 3D Avatar (Mock)", use_container_width=True)


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
