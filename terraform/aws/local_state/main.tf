terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.92"
    }
  }

  required_version = ">= 1.2"
}

provider "aws" {
  region = "ap-south-1"
}

# 1. Fetch the high-efficiency ARM64 Ubuntu Image
data "aws_ami" "ubuntu" {
  most_recent = true

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd-gp3/ubuntu-noble-24.04-arm64-server-*"] # <- Note the 'arm64' here
  }

  owners = ["099720109477"] # Canonical
}

# 2. Deploy on your allowed Free-Tier Graviton instance
resource "aws_instance" "app_server" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = var.instance_type # "t4g.small" # <- Picked directly from CLI list of free tier

  tags = {
    Name = var.instance_name # "Free-Tier-App-Server"
  }
}
