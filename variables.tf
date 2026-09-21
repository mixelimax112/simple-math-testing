variable "bucket_name" {
  description = "Name of the S3 bucket"
  type        = string
  default     = "121225ptm-maksym-kravchenko"
}

variable "name" {
  description = "Name tag for the bucket"
  type        = string
  default     = "maksym-kravchenko"
}

variable "environment" {
  description = "Environment tag for the bucket"
  type        = string
  default     = "dev"
}
