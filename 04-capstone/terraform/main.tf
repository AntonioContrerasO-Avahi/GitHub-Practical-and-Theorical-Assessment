# terraform/main.tf
# Creates the S3 bucket and uploads the texts/ folder

terraform {
  required_version = ">= 1.6"
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

# --- S3 Bucket ---
resource "aws_s3_bucket" "pipeline" {
  bucket = var.bucket_name

  tags = {
    Project     = "avahi-rag-pipeline"
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}

# Public read access — bucket is intentionally public for the eval pipeline.
# Terraform will destroy this bucket after the assessment.
resource "aws_s3_bucket_public_access_block" "pipeline" {
  bucket = aws_s3_bucket.pipeline.id

  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

resource "aws_s3_bucket_policy" "public_read" {
  bucket     = aws_s3_bucket.pipeline.id
  depends_on = [aws_s3_bucket_public_access_block.pipeline]

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Sid       = "PublicReadGetObject"
      Effect    = "Allow"
      Principal = "*"
      Action    = "s3:GetObject"
      Resource  = "${aws_s3_bucket.pipeline.arn}/*"
    }]
  })
}

# Enable versioning — so we can recover overwritten eval results
resource "aws_s3_bucket_versioning" "pipeline" {
  bucket = aws_s3_bucket.pipeline.id
  versioning_configuration {
    status = "Enabled"
  }
}

# Encrypt at rest with AES-256
resource "aws_s3_bucket_server_side_encryption_configuration" "pipeline" {
  bucket = aws_s3_bucket.pipeline.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# --- Upload texts/ folder ---
# One s3 object per .txt file found in ../texts/
resource "aws_s3_object" "texts" {
  for_each = fileset("${path.module}/../texts", "*.txt")

  bucket       = aws_s3_bucket.pipeline.id
  key          = "dataset/input/${each.value}"
  source       = "${path.module}/../texts/${each.value}"
  content_type = "text/plain"
  etag         = filemd5("${path.module}/../texts/${each.value}")
}
