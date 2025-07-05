variable "aws_region" {
    description = "AWS region for the resources"
    type        = string
    default     = "us-east-2"
}

variable "project_id" {
    description = "Unique identifier for the project"
    type        = string
    default     = "loan_prediction"
}

variable "source_stream_name" {
    description = "Name of the source Kinesis stream"
}