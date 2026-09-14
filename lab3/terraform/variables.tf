variable "aws_region" {
  description = "AWS region to deploy infrastructure"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project name prefix for all resources"
  type        = string
  default     = "lab3-devops"
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidr" {
  description = "CIDR block for public subnet"
  type        = string
  default     = "10.0.1.0/24"
}

variable "allowed_cidr" {
  description = "CIDR allowed to access management ports (use your IP)"
  type        = string
  default     = "0.0.0.0/0"  # Replace with your IP: "x.x.x.x/32"
}

variable "ami_id" {
  description = "Ubuntu 22.04 LTS AMI ID (region-specific)"
  type        = string
  default     = "ami-0c7217cdde317cfec"  # us-east-1 Ubuntu 22.04
}

variable "monitoring_instance_type" {
  description = "EC2 instance type for monitoring server"
  type        = string
  default     = "t3.medium"
}

variable "elk_instance_type" {
  description = "EC2 instance type for ELK server (needs more RAM)"
  type        = string
  default     = "t3.large"
}

variable "app_instance_type" {
  description = "EC2 instance type for application servers"
  type        = string
  default     = "t3.small"
}

variable "app_server_count" {
  description = "Number of application server instances"
  type        = number
  default     = 2
}

variable "public_key_path" {
  description = "Path to SSH public key"
  type        = string
  default     = "~/.ssh/lab3_key.pub"
}

variable "common_tags" {
  description = "Common tags applied to all resources"
  type        = map(string)
  default = {
    Project     = "Lab3"
    Environment = "lab"
    ManagedBy   = "Terraform"
    Course      = "DevOps"
  }
}
