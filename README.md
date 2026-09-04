# Myntra Digital Fitting Room

An advanced, scalable proof-of-concept for a hyper-realistic digital fitting room experience. This project uses a "Client-Server Split" architecture to deliver computationally heavy 3D rendering and AR transformations directly to low-end mobile devices without causing Out-of-Memory (OOM) crashes.

## Table of Contents
- [Architecture Overview](#architecture-overview)
- [Project Structure](#project-structure)
- [Core Features](#core-features)
- [Local Development & Testing](#local-development--testing)
- [Cloud Deployment (AWS)](#cloud-deployment-aws)
- [Documentation Reference](#documentation-reference)

## Architecture Overview

The platform uses a heavily decoupled client-server architecture:
1. **Frontend (Stitch UI)**: A lightweight, responsive web view acting solely as a rendering surface. It handles zero heavy lifting, only passing parameters and displaying streamed output.
2. **API Gateway (FastAPI)**: Routes client requests (photo uploads or param generation) to the backend message queue (Celery/Redis).
3. **GPU Worker Clusters (Python)**: Dedicated ML instances that utilize `rembg`, PyTorch (`DPTForDepthEstimation`), and OpenCV to generate depth maps and 3D meshes.
4. **Ephemeral Cache (Redis)**: Rapid-access memory storage that streams the final low-poly assets back to the client, preventing mobile device overload.

## Project Structure

```
├── backend_engine/
│   ├── api_gateway/        # FastAPI routing and Celery task dispatching
│   │   └── main.py
│   └── gpu_workers/        # Heavy Python ML processing logic
│       ├── ar_processor.py # Mode B: Computer Vision Depth Estimation & Silhouette Warping
│       ├── mesh_processor.py # Mode A: Trimesh Parametric Scaling & Decimation
│       ├── worker.py       # Celery worker consuming Redis queues
│       └── requirements.txt
├── frontend_ui/
│   └── stitch_realistic_frame_visualizer/ # Compiled HTML/JS/CSS assets
│       ├── myntra_fitting_room_ai_avatar_mode_frame_b/ # Mode A UI
│       └── myntra_fitting_room_ar_photo_mode_frame_c/  # Mode B UI
├── preprocessing_service/  # Dockerized catalog asset ingestion pipeline
├── terraform/              # Infrastructure as Code (AWS EKS, S3, ElastiCache)
├── docker-compose.yml      # Local container orchestration
└── README.md
```

## Core Features

- **Mode A (AI Avatar)**: Generates a parametric 3D mesh based on height, weight, and body shape inputs. Backend decimates polygons dynamically for smooth mobile streaming.
- **Mode B (AR Photo)**: Takes a 2D user photograph, performs flawless background segmentation via `rembg`, estimates depth topologies using HuggingFace Transformers, and applies a perspective warp to simulate realistic fabric drape.
- **Stateless Execution**: The backend purges all photos immediately after the synthesis task completes, ensuring 100% data privacy compliance.
- **Loading Constraints**: The frontend handles fallback vector scanning animations locally to mask the 3-second GPU processing latency.

## Local Development & Testing

Since the heavy ML pipelines require significant compute and local Docker might be unavailable, you can test the frontend UI and Javascript API wiring using a local Python HTTP server.

1. **Start the local UI Server:**
   ```bash
   cd "frontend_ui/stitch_realistic_frame_visualizer/"
   python3 -m http.server 8080
   ```
2. **Access the UI:**
   Open your browser to `http://localhost:8080/myntra_fitting_room_ai_avatar_mode_frame_b/code.html`. 
   
*(Note: Hitting the buttons will trigger the loading state, but you will receive an API connection alert since the backend FastAPI server and Redis broker are not actively running).*

## Cloud Deployment (AWS)

The project includes production-ready Terraform templates to deploy the infrastructure to AWS.

1. Install Terraform.
2. Navigate to the infrastructure directory:
   ```bash
   cd terraform/
   ```
3. Initialize and Apply:
   ```bash
   terraform init
   terraform plan
   terraform apply
   ```
This will provision the S3+CloudFront CDN for the frontend, an ElastiCache Redis node, and an EKS cluster with specialized `g4dn.xlarge` GPU node pools for the ML workers (scaled to 0 by default to save costs).

## Documentation Reference

Review these internal markdown files for deep dives into specific architectural decisions:
- `architecture.md`: Detailed breakdown of the Client-Server split vs Edge rendering.
- `edge-case.md`: Documentation on handling hardware failures, network drops, and malicious inputs.
- `deployment-plan.md`: The phased rollout strategy and CI/CD philosophy.
