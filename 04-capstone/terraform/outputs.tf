# terraform/outputs.tf

output "bucket_name" {
  description = "S3 bucket name — set this as S3_BUCKET in your .env"
  value       = aws_s3_bucket.pipeline.id
}

output "bucket_arn" {
  description = "S3 bucket ARN"
  value       = aws_s3_bucket.pipeline.arn
}

output "uploaded_files" {
  description = "Keys of uploaded text files"
  value       = [for obj in aws_s3_object.texts : obj.key]
}
