# Project Context: Myntra Digital Fitting Room

## 1. Problem Overview
- **Core Challenge:** High pre-purchase drop-offs in the Myntra wishlist funnel caused by static catalog photos failing to resolve size uncertainty (65%) and fabric drape/quality doubt (55%).
- **Engineering Constraints:**
  - **Visual Decoupling:** 2D assets provide no geometric context for how multi-size stretch fabrics contour across different human body topologies.
  - **Client-Side Bottlenecks:** Executing real-time 3D simulation or NeRF mapping locally causes severe thermal throttling, memory spikes, and aggressive out-of-memory (OOM) crashes on mid-range Android devices.
  - **Asset Ingestion Latency:** Raw seller assets often lack standard depth maps, skeletal rigging metadata, and alpha channels, causing processing queues to fail or stall.

## 2. Technical Architecture
The system employs a **Client-Server Split**, offloading heavy computer vision tasks (body segmentation, depth estimation, 3D mesh texturing) to scalable backend GPU worker clusters, and returning lightweight rendering assets to the client.

**Dual-Mode Engine Pipeline:**
- **Mode A (Body Double / AI Avatar):** Parametric 3D avatar generation using pre-rigged base meshes scaled via numerical weight/height inputs.
- **Mode B (Photo-Realistic AR):** Single-image silhouette warping combined with 2D-to-3D texture coordinate mapping for accurate cloth draping.

## 3. Engineering Risks & Mitigations
- **Rendering Latency & Stuttering:** Offload heavy computations to server-side GPUs and stream optimized, compressed low-polygon texture assets to the client to maintain acceptable framerates on low-end devices.
- **Unstandardized Seller Inputs:** Utilize an automated preprocessing microservice to perform computer vision background removal, dimension normalization, and color profile standardization before caching.
- **Memory Exhaustion (OOM Crashes):** Enforce strict memory management policies using ephemeral, compressed texture caches, aggressive garbage collection, and a hard three-second timeout ceiling backed by a fallback vector state.
- **Data Privacy & Compliance:** Process all user uploads within isolated, ephemeral container sessions, instantly purging raw image data from memory after the session token expires to ensure zero long-term retention.
