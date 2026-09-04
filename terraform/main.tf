terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# ==========================================
# 1. Frontend: S3 Bucket & CloudFront CDN
# ==========================================

resource "aws_s3_bucket" "frontend_bucket" {
  bucket = "myntra-digital-fitting-room-ui-${var.environment}"
}

resource "aws_s3_bucket_website_configuration" "frontend_bucket_website" {
  bucket = aws_s3_bucket.frontend_bucket.id

  index_document {
    suffix = "index.html"
  }
}

# (Simplified CloudFront distribution for the static assets)
resource "aws_cloudfront_distribution" "frontend_cdn" {
  origin {
    domain_name = aws_s3_bucket.frontend_bucket.bucket_regional_domain_name
    origin_id   = "S3-${aws_s3_bucket.frontend_bucket.bucket}"
  }

  enabled             = true
  is_ipv6_enabled     = true
  default_root_object = "index.html"

  default_cache_behavior {
    allowed_methods  = ["GET", "HEAD"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "S3-${aws_s3_bucket.frontend_bucket.bucket}"

    forwarded_values {
      query_string = false
      cookies {
        forward = "none"
      }
    }
    viewer_protocol_policy = "redirect-to-https"
  }

  viewer_certificate {
    cloudfront_default_certificate = true
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }
}

# ==========================================
# 2. Ephemeral Cache: ElastiCache Redis
# ==========================================

resource "aws_elasticache_cluster" "ephemeral_cache" {
  cluster_id           = "dfr-redis-${var.environment}"
  engine               = "redis"
  node_type            = "cache.t4g.micro" # Cost-effective for dev/ephemeral
  num_cache_nodes      = 1
  parameter_group_name = "default.redis7"
  port                 = 6379
}

# ==========================================
# 3. Backend: EKS Cluster & GPU Node Pools
# ==========================================

module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 19.0"

  cluster_name    = var.cluster_name
  cluster_version = "1.28"

  # Basic VPC config (assuming module-created VPC for simplicity in this template)
  vpc_id                   = "vpc-0123456789abcdef0" # Placeholder
  subnet_ids               = ["subnet-01234567", "subnet-89abcdef"] # Placeholder
  
  eks_managed_node_groups = {
    # CPU Pool for API Gateway & Preprocessing Service
    cpu_nodes = {
      min_size     = 1
      max_size     = 5
      desired_size = 2
      
      instance_types = ["t3.medium"]
      capacity_type  = "ON_DEMAND"
    }

    # GPU Pool strictly for AR/Mesh Processors (Scales to 0)
    gpu_nodes = {
      min_size     = 0
      max_size     = 5
      desired_size = 0  # Start at 0 to save costs
      
      # T4 GPU instances optimized for ML inference
      instance_types = ["g4dn.xlarge"]
      
      # Amazon Machine Image optimized for EKS + GPU
      ami_type = "AL2_x86_64_GPU"
      
      # Taints to ensure ONLY the GPU workers are scheduled here
      taints = [
        {
          key    = "nvidia.com/gpu"
          value  = "true"
          effect = "NO_SCHEDULE"
        }
      ]
    }
  }
}
