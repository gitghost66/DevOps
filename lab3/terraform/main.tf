# ==============================================================================
# Terraform – Lab 3 Infrastructure Provisioning
# Provider: AWS (swap to Azure/GCP/local as needed)
# ==============================================================================

terraform {
  required_version = ">= 1.7.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # Uncomment to use remote state (recommended for teams)
  # backend "s3" {
  #   bucket = "lab3-terraform-state"
  #   key    = "lab3/terraform.tfstate"
  #   region = "us-east-1"
  # }
}

provider "aws" {
  region = var.aws_region
}

# ---- VPC & Networking --------------------------------------------------------
resource "aws_vpc" "lab3_vpc" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = merge(var.common_tags, {
    Name = "${var.project_name}-vpc"
  })
}

resource "aws_subnet" "lab3_public_subnet" {
  vpc_id                  = aws_vpc.lab3_vpc.id
  cidr_block              = var.public_subnet_cidr
  availability_zone       = "${var.aws_region}a"
  map_public_ip_on_launch = true

  tags = merge(var.common_tags, {
    Name = "${var.project_name}-public-subnet"
  })
}

resource "aws_internet_gateway" "lab3_igw" {
  vpc_id = aws_vpc.lab3_vpc.id

  tags = merge(var.common_tags, {
    Name = "${var.project_name}-igw"
  })
}

resource "aws_route_table" "lab3_rt" {
  vpc_id = aws_vpc.lab3_vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.lab3_igw.id
  }

  tags = merge(var.common_tags, {
    Name = "${var.project_name}-rt"
  })
}

resource "aws_route_table_association" "lab3_rta" {
  subnet_id      = aws_subnet.lab3_public_subnet.id
  route_table_id = aws_route_table.lab3_rt.id
}

# ---- Security Groups ---------------------------------------------------------
resource "aws_security_group" "monitoring_sg" {
  name        = "${var.project_name}-monitoring-sg"
  description = "Allow Prometheus, Grafana, Alertmanager traffic"
  vpc_id      = aws_vpc.lab3_vpc.id

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.allowed_cidr]
    description = "SSH"
  }
  ingress {
    from_port   = 9090
    to_port     = 9090
    protocol    = "tcp"
    cidr_blocks = [var.allowed_cidr]
    description = "Prometheus"
  }
  ingress {
    from_port   = 3000
    to_port     = 3000
    protocol    = "tcp"
    cidr_blocks = [var.allowed_cidr]
    description = "Grafana"
  }
  ingress {
    from_port   = 9093
    to_port     = 9093
    protocol    = "tcp"
    cidr_blocks = [var.allowed_cidr]
    description = "Alertmanager"
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = var.common_tags
}

resource "aws_security_group" "elk_sg" {
  name        = "${var.project_name}-elk-sg"
  description = "Allow ELK Stack traffic"
  vpc_id      = aws_vpc.lab3_vpc.id

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.allowed_cidr]
    description = "SSH"
  }
  ingress {
    from_port   = 9200
    to_port     = 9200
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr]
    description = "Elasticsearch"
  }
  ingress {
    from_port   = 5601
    to_port     = 5601
    protocol    = "tcp"
    cidr_blocks = [var.allowed_cidr]
    description = "Kibana"
  }
  ingress {
    from_port   = 5044
    to_port     = 5044
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr]
    description = "Logstash Beats"
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = var.common_tags
}

resource "aws_security_group" "app_sg" {
  name        = "${var.project_name}-app-sg"
  description = "Allow application traffic"
  vpc_id      = aws_vpc.lab3_vpc.id

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.allowed_cidr]
  }
  ingress {
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Application"
  }
  ingress {
    from_port   = 9100
    to_port     = 9100
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr]
    description = "Node Exporter"
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = var.common_tags
}

# ---- EC2 Instances -----------------------------------------------------------
resource "aws_key_pair" "lab3_key" {
  key_name   = "${var.project_name}-key"
  public_key = file(var.public_key_path)
}

resource "aws_instance" "monitoring_server" {
  ami                    = var.ami_id
  instance_type          = var.monitoring_instance_type
  subnet_id              = aws_subnet.lab3_public_subnet.id
  vpc_security_group_ids = [aws_security_group.monitoring_sg.id]
  key_name               = aws_key_pair.lab3_key.key_name

  root_block_device {
    volume_size = 30
    volume_type = "gp3"
  }

  user_data = <<-EOF
    #!/bin/bash
    apt-get update -y
    apt-get install -y docker.io docker-compose python3 python3-pip
    systemctl enable docker && systemctl start docker
  EOF

  tags = merge(var.common_tags, {
    Name = "${var.project_name}-monitoring"
    Role = "monitoring"
  })
}

resource "aws_instance" "elk_server" {
  ami                    = var.ami_id
  instance_type          = var.elk_instance_type
  subnet_id              = aws_subnet.lab3_public_subnet.id
  vpc_security_group_ids = [aws_security_group.elk_sg.id]
  key_name               = aws_key_pair.lab3_key.key_name

  root_block_device {
    volume_size = 50
    volume_type = "gp3"
  }

  user_data = <<-EOF
    #!/bin/bash
    apt-get update -y
    apt-get install -y docker.io docker-compose
    sysctl -w vm.max_map_count=262144
    echo "vm.max_map_count=262144" >> /etc/sysctl.conf
    systemctl enable docker && systemctl start docker
  EOF

  tags = merge(var.common_tags, {
    Name = "${var.project_name}-elk"
    Role = "elk"
  })
}

resource "aws_instance" "app_server" {
  count                  = var.app_server_count
  ami                    = var.ami_id
  instance_type          = var.app_instance_type
  subnet_id              = aws_subnet.lab3_public_subnet.id
  vpc_security_group_ids = [aws_security_group.app_sg.id]
  key_name               = aws_key_pair.lab3_key.key_name

  root_block_device {
    volume_size = 20
    volume_type = "gp3"
  }

  tags = merge(var.common_tags, {
    Name = "${var.project_name}-app-${count.index + 1}"
    Role = "app"
  })
}
