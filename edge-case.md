# Edge Cases & Corner Scenarios: Digital Fitting Room

Before deploying the Digital Fitting Room to production, the following edge cases and corner scenarios must be accounted for and handled gracefully across the UI, backend engine, and preprocessing pipelines.

## 1. User Input & Photo Uploads (Mode B: AR Photo)
- **Multiple People in Frame:** The computer vision segmentation model must either gracefully fail with a specific error ("Please ensure only one person is in the photo") or automatically detect and isolate the primary subject closest to the camera.
- **Obscured Body Topology:** If a user uploads a photo wearing heavy, baggy clothing (e.g., a thick winter coat), the depth estimation and silhouette warping will be inaccurate. The UI should prompt users to wear form-fitting clothing for best results.
- **Cropped or Partial Framing:** Uploads missing key skeletal points (e.g., no legs, missing head) will break the 2D-to-3D texture mapping. A pre-validation check should ensure the full body is visible before sending it to the GPU cluster.
- **Extreme Lighting/Shadows:** High-contrast lighting that casts harsh shadows across the body might be misinterpreted as physical topology by the depth estimator.

## 2. Parametric Avatar Generation (Mode A: AI Avatar)
- **Impossible Parameter Combinations:** Users inputting extreme or physically impossible height/weight ratios (e.g., 9 feet tall, 40 lbs). The frontend must clamp inputs to realistic human distributions to prevent the 3D base mesh from tearing or glitching.
- **Rapid Re-rendering Requests:** A user sliding the weight/height slider rapidly back and forth could spam the GPU workers with hundreds of sequential scaling requests. **Mitigation:** Implement strict debouncing (e.g., 500ms) on the sliders before triggering the API call.

## 3. Seller Asset Preprocessing Anomalies
- **Transparent & Sheer Fabrics:** Background removal algorithms struggle with lace, mesh, or highly sheer fabrics. The preprocessing microservice must have a fallback pipeline or flag these items for manual review, as the alpha channel generation will likely fail.
- **Zero-Contrast Backgrounds:** A pure white dress photographed against a pure white studio backdrop may cause the segmentation model to clip the garment itself.
- **Non-Standard Garment Poses:** Garments photographed folded, on a hanger, or worn by a mannequin with distinct limbs will warp incorrectly when mapped to a human avatar. The system must restrict inputs to "flat lay" or standard T-pose/A-pose catalog shots.

## 4. Hardware, Network, & State Failures
- **The 3-Second Timeout Breach:** If the backend GPU clusters are experiencing severe latency during a traffic spike and fail to return the asset within the strict 3-second window, the client must seamlessly transition from the vector loading state to a "Server Busy" error state without crashing the app.
- **Network Drop Mid-Processing:** If the user's mobile connection drops after uploading their photo but *before* receiving the AR asset, the ephemeral session on the backend must still securely expire and purge the photo from memory.
- **Client-Side Cache Thrashing:** A user rapidly trying on 20+ different garments in a single session. Even with low-poly textures, this could trigger OOM crashes. The mobile memory manager must strictly enforce an LRU (Least Recently Used) cache policy, aggressively purging older garment textures from local memory.

## 5. Security & Privacy Edge Cases
- **Backend Container Crash:** If the ephemeral container processing a user's photo crashes unexpectedly *before* the session token naturally expires, the raw image data might remain trapped in the dead container's memory footprint. **Mitigation:** Ensure Kubernetes pod termination lifecycle hooks include an absolute memory wipe or that the nodes themselves use encrypted, ephemeral RAM disks that wipe on pod eviction.
