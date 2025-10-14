output "public_ip" {
  description = "Public IP of the monitoring server"
  value       = aws_instance.monitoring_server.public_ip
}

output "grafana_url" {
  description = "Grafana dashboard URL"
  value       = "http://${aws_instance.monitoring_server.public_ip}:3000"
}

output "prometheus_url" {
  description = "Prometheus UI URL"
  value       = "http://${aws_instance.monitoring_server.public_ip}:9090"
}