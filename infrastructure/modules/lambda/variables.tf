variable "source_stream_arn" {
  description = "The name of the source Kinesis stream for loan events"
  type        = string
}

variable "output_stream_name" {
  description = "The name of the output Kinesis stream for predictions"
  type        = string
}

variable "output_stream_arn" {
  description = "The ARN of the output Kinesis stream for predictions"
  type        = string
}

variable "lambda_function_name" {
  description = "The name of the Lambda function"
  type        = string
}

variable "model_bucket" {
  description = "The S3 bucket where the model artifacts are stored"
  type        = string
}

variable "image_uri" {
  description = "The URI of the Docker image in ECR for the Lambda function"
  type        = string
}