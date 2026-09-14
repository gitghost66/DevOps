output "monitoring_server_ip" {
  description = "Public IP of the Monitoring server (Prometheus + Grafana)"
  value       = aws_instance.monitoring_server.public_ip
}

output "elk_server_ip" {
  description = "Public IP of the ELK server"
  value       = aws_instance.elk_server.public_ip
}

output "app_server_ips" {
  description = "Public IPs of application servers"
  value       = aws_instance.app_server[*].public_ip
}

output "prometheus_url" {
  description = "Prometheus UI URL"
  value       = "http://${aws_instance.monitoring_server.public_ip}:9090"
}

output "grafana_url" {
  description = "Grafana UI URL"
  value       = "http://${aws_instance.monitoring_server.public_ip}:3000"
}

output "kibana_url" {
  description = "Kibana UI URL"
  value       = "http://${aws_instance.elk_server.public_ip}:5601"
}

output "elasticsearch_url" {
  description = "Elasticsearch API URL"
  value       = "http://${aws_instance.elk_server.public_ip}:9200"
}

output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.lab3_vpc.id
}

output "ansible_inventory_content" {
  description = "Suggested Ansible inventory (copy to ansible/inventory/hosts.ini)"
  value = <<-EOT
    [monitoring_servers]
    monitor01 ansible_host=${aws_instance.monitoring_server.public_ip} ansible_user=ubuntu

    [elk_servers]
    elk01 ansible_host=${aws_instance.elk_server.public_ip} ansible_user=ubuntu

    [app_servers]
    %{for i, ip in aws_instance.app_server[*].public_ip}
    app0${i + 1} ansible_host=${ip} ansible_user=ubuntu
    %{endfor}

    [all:vars]
    ansible_python_interpreter=/usr/bin/python3
    ansible_ssh_private_key_file=~/.ssh/lab3_key
  EOT
}
