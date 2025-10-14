
# 创建EC2实例
resource "aws_instance" "monitoring_server" {
  ami                    = var.ami_id # Ubuntu 24.04 LTS
  instance_type          = var.instance_type
  subnet_id              = aws_subnet.monitoring_subnet.id
  vpc_security_group_ids = [aws_security_group.monitoring_sg.id]
  key_name               = "monitoring-key"
  associate_public_ip_address = true

#   user_data = <<-EOF
#               #!/bin/bash
#               apt-get update
#               apt-get install -y python3 python3-pip
#               EOF

  tags = {
    Name = "monitoring-server"
  }

  root_block_device {
    volume_size = 20
    volume_type = "gp2"
  }
}

# 输出公共IP地址
output "monitoring_server_ip" {
  value = aws_instance.monitoring_server.public_ip
}

output "monitoring_server_url" {
  value = "http://${aws_instance.monitoring_server.public_ip}:3000"
}