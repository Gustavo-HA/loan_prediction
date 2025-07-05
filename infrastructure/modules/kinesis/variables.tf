variable "stream_name" {
  description = "Name of the Kinesis stream"
  type        = string
}

variable "shard_count" {
  description = "Number of shards for the Kinesis stream"
  type        = number
}

variable "retention_period" {
  description = "Retention period in hours for the Kinesis stream"
  type        = number
}

variable "shard_level_metrics" {
  description = "List of shard-level metrics to enable for the Kinesis stream"
  type        = list(string)
  default     = []
}

variable "tags" {
    description = "Tags to apply to the Kinesis stream"
    default = "Gustavo Hernandez"
}