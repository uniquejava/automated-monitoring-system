variable "aws_profile" {
  type    = string
  default = ""
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "ap-northeast-1"
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t2.medium"
}

variable "ami_id" {
  description = "EC2 AMI ID"
  type        = string
  default     = "ami-0d4aa492f133a3068"
}
variable "ssh_private_key_path" {
  type        = string
  default     = "../monitoring-key.pem"
}