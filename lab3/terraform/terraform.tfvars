# terraform.tfvars – Override default variable values here
# DO NOT commit real credentials to version control

aws_region           = "us-east-1"
project_name         = "lab3-devops"
vpc_cidr             = "10.0.0.0/16"
public_subnet_cidr   = "10.0.1.0/24"
allowed_cidr         = "0.0.0.0/0"    # Replace with your IP

# Ubuntu 22.04 LTS – us-east-1
ami_id               = "ami-0c7217cdde317cfec"

monitoring_instance_type = "t3.medium"
elk_instance_type        = "t3.large"
app_instance_type        = "t3.small"
app_server_count         = 2

public_key_path = "~/.ssh/lab3_key.pub"
