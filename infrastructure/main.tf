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

module "source_kinesis_stream" {
    source              = "./modules/kinesis"
    stream_name         = "${var.source_stream_name}_${var.project_id}"
    retention_period    = 24
    shard_count         = 1
    tags                = var.project_id
}