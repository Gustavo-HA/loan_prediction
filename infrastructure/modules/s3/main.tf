resource "aws_s3_bucket" "s3_bucket" {
    bucket = var.bucket_name
    acl = "private"

    # Allows Terraform to delete the bucket even if it contains objects
    force_destroy = true
}

output "bucket_name" {
    value = aws_s3_bucket.s3_bucket.bucket
}