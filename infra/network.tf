
# 创建VPC
resource "aws_vpc" "monitoring_vpc" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  tags = {
    Name = "monitoring-vpc"
  }
}

# 创建子网
resource "aws_subnet" "monitoring_subnet" {
  vpc_id            = aws_vpc.monitoring_vpc.id
  cidr_block = cidrsubnet(aws_vpc.monitoring_vpc.cidr_block, 8, 0)
  tags = {
    Name = "monitoring-subnet"
  }
}

# 创建互联网网关
resource "aws_internet_gateway" "monitoring_igw" {
  vpc_id = aws_vpc.monitoring_vpc.id
  tags = {
    Name = "monitoring-igw"
  }
}

# 创建路由表
resource "aws_route_table" "monitoring_rt" {
  vpc_id = aws_vpc.monitoring_vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.monitoring_igw.id
  }

  tags = {
    Name = "monitoring-rt"
  }
}

# 关联路由表
resource "aws_route_table_association" "monitoring_rta" {
  subnet_id      = aws_subnet.monitoring_subnet.id
  route_table_id = aws_route_table.monitoring_rt.id
}

# 创建安全组
resource "aws_security_group" "monitoring_sg" {
  name        = "monitoring-sg"
  description = "Security group for monitoring servers"
  vpc_id      = aws_vpc.monitoring_vpc.id

  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "Grafana"
    from_port   = 3000
    to_port     = 3000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "Prometheus"
    from_port   = 9090
    to_port     = 9090
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "Node Exporter"
    from_port   = 9100
    to_port     = 9100
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "AIOps Metrics Exporter"
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "monitoring-sg"
  }
}