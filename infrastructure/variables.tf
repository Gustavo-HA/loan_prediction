variable "aws_region" {
    description = "AWS region for the resources"
    type        = string
    default     = "us-east-2"
}

variable "project_id" {
    description = "Unique identifier for the project"
    type        = string
    default     = "loan-prediction"
}

variable "source_stream_name" {
    description = "Name of the source Kinesis stream (e.g. 'project_events')"
}

variable "output_stream_name" {
    description = "Name of the output Kinesis stream (e.g. 'project_predictions')"
}

variable "model_bucket" {
    description = "Name of the S3 bucket"
    type        = string
}

variable "ecr_repo_name" {
    description = "Name of the ECR repository"
    type        = string
}

variable "lambda_function_local_path" {
    type        = string
}

variable "docker_image_local_path" {
    type        = string
}