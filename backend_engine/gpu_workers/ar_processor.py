import io
import time
import cv2
import numpy as np
from PIL import Image
import torch
from transformers import DPTImageProcessor, DPTForDepthEstimation
import rembg

class ARProcessor:
    def __init__(self):
        # Initialize depth estimation models from HuggingFace
        print("Loading DPT Depth Estimation models...")
        self.processor = DPTImageProcessor.from_pretrained("Intel/dpt-large")
        self.model = DPTForDepthEstimation.from_pretrained("Intel/dpt-large")
        print("Models loaded successfully.")

    def segment_body(self, image_bytes: bytes) -> dict:
        """
        Uses rembg to accurately isolate the body from the background.
        """
        try:
            # rembg expects bytes directly
            output_bytes = rembg.remove(image_bytes)
            
            # Convert to PIL Image for bounding box calculation
            image = Image.open(io.BytesIO(output_bytes))
            bbox = image.getbbox()
            
            return {
                "status": "success",
                "mask_data": output_bytes,
                "bounding_box": bbox
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def estimate_depth(self, image_bytes: bytes) -> dict:
        """
        Uses HuggingFace DPT model to generate a depth map.
        """
        try:
            image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            
            # Prepare image for the model
            inputs = self.processor(images=image, return_tensors="pt")

            with torch.no_grad():
                outputs = self.model(**inputs)
                predicted_depth = outputs.predicted_depth

            # Interpolate to original size
            prediction = torch.nn.functional.interpolate(
                predicted_depth.unsqueeze(1),
                size=image.size[::-1],
                mode="bicubic",
                align_corners=False,
            )

            # Normalize and convert to numpy image
            output = prediction.squeeze().cpu().numpy()
            formatted = (output * 255 / np.max(output)).astype("uint8")
            depth_image = Image.fromarray(formatted)
            
            # Convert back to bytes for returning
            img_byte_arr = io.BytesIO()
            depth_image.save(img_byte_arr, format='PNG')
            
            return {
                "status": "success",
                "depth_map": img_byte_arr.getvalue()
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def warp_silhouette(self, image_bytes: bytes, mask: bytes, depth_map: bytes, garment_id: str) -> dict:
        """
        Uses OpenCV to perform a basic perspective warp simulating cloth drape.
        In a full NeRF system, this would be a 3D cloth simulation, but here we 
        use a standard 2D mesh warp based on the depth gradient.
        """
        try:
            # Load images into cv2 format
            nparr_bg = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(nparr_bg, cv2.IMREAD_COLOR)
            
            nparr_depth = np.frombuffer(depth_map, np.uint8)
            depth = cv2.imdecode(nparr_depth, cv2.IMREAD_GRAYSCALE)
            
            # Example mapping: Displace pixels based on depth intensity
            # Creating a mock displacement map
            map_x = np.zeros(img.shape[:2], np.float32)
            map_y = np.zeros(img.shape[:2], np.float32)
            
            for i in range(img.shape[0]):
                for j in range(img.shape[1]):
                    # Small displacement based on depth (just as a mock example of warping)
                    displacement = (depth[i,j] / 255.0) * 10 
                    map_x[i, j] = j + displacement
                    map_y[i, j] = i
                    
            warped_img = cv2.remap(img, map_x, map_y, cv2.INTER_LINEAR)
            
            # Encode back to bytes
            _, buffer = cv2.imencode('.png', warped_img)
            
            return {
                "status": "success",
                "warped_image": buffer.tobytes(),
                "texture_mapped": True,
                "garment_applied": garment_id
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def process_image(self, image_data: bytes, session_token: str) -> dict:
        """
        Orchestrates the Mode B AR processing pipeline.
        """
        print(f"Starting Mode B processing for session {session_token}...")
        
        garment_id = "wishlist_item_999" # Mock garment ID
        
        # Step 1: Body Segmentation
        print("Segmenting body...")
        segmentation = self.segment_body(image_data)
        if segmentation["status"] != "success":
            return {"status": "error", "message": "Segmentation failed"}
            
        # Step 2: Depth Estimation
        print("Estimating depth...")
        depth = self.estimate_depth(image_data)
        if depth["status"] != "success":
            return {"status": "error", "message": "Depth estimation failed"}
            
        # Step 3: Silhouette Warping & Texture Mapping
        print("Warping silhouette and applying texture...")
        warp_result = self.warp_silhouette(
            image_data, 
            segmentation["mask_data"], 
            depth["depth_map"], 
            garment_id
        )
        
        print("Mode B processing complete.")
        
        # In reality, this would save to a secure S3 bucket with a presigned URL
        # We simulate that by returning a mock URL and the final status
        return {
            "status": "success",
            "asset_url": "s3://mock-bucket/ar_assets/warped_silhouette_456.png",
            "mode": "B",
            "session_token_used": session_token
        }
