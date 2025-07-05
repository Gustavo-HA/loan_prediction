# Make sure to create state bucket before running this code
terraform {
    required_version = ">= 1.0.0"
    backend "s3" {
        bucket = "tf-state-loan-prediction"
        key = "loan-prediction.tfstate"
        region = "us-east-2"
        encrypt = true
    }
}

provider "aws" {
    region = var.aws_region
}

data "aws_caller_identity" "current" {}

locals {
    account_id = data.aws_caller_identity.current.account_id
}

# loan_events
module "source_kinesis_stream" {
    source              = "./modules/kinesis"
    stream_name         = "${var.source_stream_name}_${var.project_id}"
    retention_period    = 24
    shard_count         = 1
    tags                = var.project_id
}

# loan_predictions
module "output_kinesis_stream" {
    source              = "./modules/kinesis"
    stream_name         = "${var.output_stream_name}_${var.project_id}"
    retention_period    = 24
    shard_count         = 1
    tags                = var.project_id
}

# model_bucket
module "s3_bucket" {
    source      = "./modules/s3"
    bucket_name = "${var.model_bucket}-${var.project_id}"
}

# image repository
module "ecr_image" {
    source      = "./modules/ecr"
    ecr_repo_name = "${var.ecr_repo_name}-${var.project_id}"
    account_id = local.account_id
    lambda_function_local_path = var.lambda_function_local_path
    docker_image_local_path = var.docker_image_local_path
}