import os
from ar_processor import ARProcessor
from mesh_processor import MeshProcessor

def test_ar_processor():
    print("Testing AR Processor instantiation (Note: will download models if run)...")
    # Uncomment to actually run and download models
    # processor = ARProcessor()
    # 
    # with open("dummy_image.png", "rb") as f:
    #     image_data = f.read()
    # 
    # result = processor.process_image(image_data, "test_token_123")
    # print(result)

def test_mesh_processor():
    print("Testing Mesh Processor instantiation...")
    processor = MeshProcessor()
    
    print("Running Mode A pipeline (Height: 180, Weight: 75, Shape: slim)...")
    result = processor.process_full_pipeline(weight=75.0, height=180.0, body_shape="slim", garment_id="test_shirt_1")
    print(result)

if __name__ == "__main__":
    print("--- Digital Fitting Room Backend Tests ---")
    test_mesh_processor()
    print("------------------------------------------")
    test_ar_processor()
    print("Tests complete.")
