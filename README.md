# Automated Monitoring System

A comprehensive DevOps and Platform Engineering project implementing a complete workflow from infrastructure automation to monitoring and AIOps integration.

[简体中文](README.zh-CN.md) | English

## 🎯 Project Overview

This project builds an automated monitoring system on AWS EC2, integrating Prometheus, Grafana, and AIOps anomaly detection capabilities:

- 🏗️ **Infrastructure Automation**: Terraform for AWS environment deployment
- ⚙️ **Service Configuration Management**: Ansible for monitoring service configuration
- 📊 **Metrics Collection**: Automated system and custom business metrics collection
- 🤖 **Intelligent Anomaly Detection**: Machine learning models for anomaly detection
- 📈 **Data Visualization**: Grafana data visualization

## 🏛️ System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Terraform     │    │     Ansible     │    │   Monitoring    │
│                 │    │                 │    │    Stack        │
│ • EC2 Instance  │───▶│ • Prometheus    │───▶│ • Prometheus    │
│ • VPC           │    │ • Grafana       │    │ • Grafana       │
│ • Security      │    │ • Node Exporter │    │ • Node Exporter │
│   Group         │    │ • AIOps         │    │ • AIOps         │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📁 Project Structure

```
automated-monitoring-system/
├── 📋 README.md                          # Project documentation
├── 📋 README.zh-CN.md                     # Chinese documentation
├── 🚀 scripts/deploy.sh                  # Main deployment script
├── 🔧 scripts/destroy.sh                 # Resource cleanup script
├── 🔑 monitoring-key.pem                 # SSH key (to be generated)
├── 📂 infra/                             # Terraform configuration
│   ├── 🌐 network.tf                     # Network configuration
│   ├── 🖥️  ec2.tf                        # EC2 instance configuration
│   ├── 🔐 variables.tf                   # Variable definitions
│   ├── 📤 outputs.tf                     # Output definitions
│   └── 📋 versions.tf                    # Terraform version
├── 📂 ansible/                           # Ansible configuration
│   ├── 📜 playbook.yml                   # Main playbook
│   ├── 📂 group_vars/                    # Group variables
│   │   └── 📄 all.yml                    # Global variables
│   ├── 📂 roles/                         # Role definitions
│   │   ├── 📂 common/                    # Common configuration
│   │   ├── 📂 prometheus/                # Prometheus configuration
│   │   ├── 📂 node_exporter/             # Node Exporter configuration
│   │   ├── 📂 grafana/                   # Grafana configuration
│   │   └── 📂 aiops/                     # AIOps anomaly detection
│   │       ├── 📂 tasks/
│   │       │   └── 📄 main.yml
│   │       ├── 📂 files/
│   │       │   ├── 📊 metrics_exporter.py
│   │       │   └── 🤖 anomaly_detector.py
│   │       └── 📂 templates/
│   └── 📂 files/                         # Configuration files
├── 📂 docs/                              # Documentation
│   └── 📄 metrics.md                     # Metrics documentation
└── 📂 scripts/                           # Utility scripts
    └── ⏳ wait-for-ssh.sh                # SSH wait script
```

## 🚀 Quick Start

### Prerequisites

- ✅ [Terraform](https://www.terraform.io/downloads.html) >= 1.0
- ✅ [Ansible](https://docs.ansible.com/ansible/latest/installation_guide/) >= 2.9
- ✅ [AWS CLI](https://aws.amazon.com/cli/) configured
- ✅ AWS credentials configured (environment variables or ~/.aws/credentials)

### One-Click Deployment

```bash
# 1. Clone the project
git clone <your-repo-url>
cd automated-monitoring-system

# 2. Generate SSH key pair (if you don't have one)
ssh-keygen -t rsa -b 4096 -f monitoring-key.pem -N ""

# 3. Import public key to AWS
aws ec2 import-key-pair \
    --key-name monitoring-key \
    --public-key-material fileb://monitoring-key.pem.pub \
    --region ap-northeast-1

# 4. Execute deployment
chmod +x scripts/deploy.sh scripts/wait-for-ssh.sh scripts/destroy.sh
./scripts/deploy.sh
```

After deployment, you will see:
```
✅ Deployment complete!
📊 Grafana: http://<INSTANCE_IP>:3000
🔍 Prometheus: http://<INSTANCE_IP>:9090
```

## 🔧 Detailed Configuration

### Terraform Configuration

**AWS Region** (`infra/variables.tf`):
```hcl
variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "ap-northeast-1"
}
```

**Instance Type**:
```hcl
variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t2.medium"
}
```

**AMI ID**:
```hcl
variable "ami_id" {
  description = "EC2 AMI ID"
  type        = string
  default     = "ami-0d4aa492f133a3068"  # Amazon Linux 2023
}
```

### Ansible Configuration

**Global Variables** (`ansible/group_vars/all.yml`):
```yaml
# Service versions
prometheus_version: "2.53.0"
node_exporter_version: "1.8.1"
grafana_version: "11.0.0"

# Path configuration
prometheus_dir: /opt/prometheus
node_exporter_dir: /opt/node_exporter
grafana_dir: /opt/grafana

# Prometheus configuration
prometheus_scrape_interval: 15s
prometheus_targets:
  - localhost:9100
  - localhost:8000  # AIOps custom metrics

# Grafana configuration
grafana_admin_user: admin
grafana_admin_password: admin
```

## 📊 Monitoring Features

### 1. System Metrics Monitoring

System metrics collected through Node Exporter:
- **CPU Usage**: Real-time CPU utilization
- **Memory Usage**: Memory utilization status
- **Disk Usage**: Disk space utilization
- **Network Traffic**: Network receive/transmit bytes
- **System Load**: 1-minute, 5-minute, 15-minute load averages

### 2. Custom Business Metrics

Provided by AIOps Metrics Exporter:
- **System Load Average**: More precise load metrics
- **Process Count**: Total number of running processes
- **Network Connections**: Active network connections
- **Custom Business Metrics**: Simulated business KPIs
- **Anomaly Score**: AIOps anomaly detection score

### 3. AIOps Anomaly Detection

**Detection Algorithm**:
- Uses Isolation Forest machine learning algorithm
- Combines multiple system metrics for anomaly detection
- Real-time anomaly score calculation (0-1 range)

**Detection Metrics**:
```python
metrics = {
    "cpu_usage": CPU usage rate,
    "memory_usage": Memory usage rate,
    "disk_usage": Disk usage rate,
    "network_rx": Network receive rate
}
```

**Anomaly Score Interpretation**:
- `0.0 - 0.3`: System normal
- `0.3 - 0.7`: Mild anomaly, attention needed
- `0.7 - 1.0`: Severe anomaly, immediate action required

## 🖥️ Access Monitoring Platform

### Grafana Dashboard

Access URL: `http://<INSTANCE_IP>:3000`

- **Username**: `admin`
- **Password**: `admin` (can be modified in `ansible/group_vars/all.yml`)

**Recommended Configuration**:
1. Import Prometheus data source (auto-configured)
2. Create system monitoring dashboard
3. Set up AIOps anomaly score charts
4. Configure alert rules

### Prometheus

Access URL: `http://<INSTANCE_IP>:9090`

**Query Examples**:
```promql
# CPU usage rate
100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)

# Memory usage rate
(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100

# AIOps anomaly score
aiops_anomaly_score
```

## 🤖 AIOps Features

### 1. Metrics Exporter (`metrics_exporter.py`)

```python
# Runs on port 8000
# Provides custom metrics endpoint: /metrics
# Health check endpoint: /healthz
```

**Main Metrics**:
- `system_load_average_1m/5m/15m`: System load
- `cpu_usage_percent`: CPU usage rate
- `memory_usage_percent`: Memory usage rate
- `custom_application_metric`: Custom business metric
- `aiops_anomaly_score`: Anomaly detection score

### 2. Anomaly Detector (`anomaly_detector.py`)

**Workflow**:
1. **Data Collection**: Query system metrics from Prometheus
2. **Historical Storage**: Maintain last 200 data points
3. **Feature Standardization**: Use StandardScaler for data normalization
4. **Anomaly Detection**: Isolation Forest algorithm for anomaly detection
5. **Score Calculation**: Calculate current system anomaly score

**Detection Interval**: Recommended to run every 5 minutes

## 📚 Documentation

- **[Metrics Documentation](docs/metrics.md)** - Comprehensive metrics catalog
- **[CLAUDE.md](CLAUDE.md)** - Claude Code development guide

## 🔍 Troubleshooting

### Common Issues

**1. SSH Connection Failure**
```bash
# Check key permissions
chmod 600 monitoring-key.pem

# Check security group configuration
aws ec2 describe-security-groups --group-ids <sg-id>
```

**2. Service Startup Failure**
```bash
# Login to instance to check service status
ssh -i monitoring-key.pem ec2-user@<INSTANCE_IP>
sudo systemctl status prometheus
sudo systemctl status grafana-server
```

**3. Prometheus Access Issues**
```bash
# Check Prometheus configuration
sudo cat /opt/prometheus/prometheus.yml

# Check firewall
sudo ufw status
```

**4. Grafana Cannot Connect to Prometheus**
```bash
# Check data source configuration
sudo cat /etc/grafana/provisioning/datasources/datasource.yml

# Restart Grafana
sudo systemctl restart grafana-server
```

### Log Viewing

```bash
# AIOps logs
sudo tail -f /opt/monitoring/aiops/aiops.log

# Prometheus logs
sudo journalctl -u prometheus -f

# Grafana logs
sudo journalctl -u grafana-server -f
```

## 🧹 Resource Cleanup

When you no longer need the monitoring environment, run the cleanup script:

```bash
./scripts/destroy.sh
```

**Manual Cleanup Steps**:
```bash
# 1. Destroy Terraform resources
cd infra
terraform destroy -auto-approve

# 2. Delete SSH key pair (optional)
aws ec2 delete-key-pair --key-name monitoring-key --region ap-northeast-1

# 3. Delete local key files (optional)
rm -f monitoring-key.pem monitoring-key.pem.pub
```

## 🔧 Custom Configuration

### Modify Monitoring Targets

Edit `ansible/roles/templates/prometheus.yml.j2`:

```yaml
scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'node'
    static_configs:
      - targets: ['localhost:9100']

  # Add new monitoring targets
  - job_name: 'custom-app'
    static_configs:
      - targets: ['<TARGET_IP>:<PORT>']
```

### Add Grafana Dashboard

1. Create dashboard in Grafana
2. Export as JSON file
3. Place in `ansible/roles/grafana/files/dashboards/`
4. Update Grafana role configuration for auto-import

### Custom AIOps Detection

Modify `ansible/roles/aiops/files/anomaly_detector.py`:

```python
# Add new detection metrics
def collect_metrics(self):
    metrics = {
        "cpu_usage": self.query_metric('...'),
        "memory_usage": self.query_metric('...'),
        # Add new metrics
        "custom_metric": self.query_metric('<your_prometheus_query>'),
    }
    return metrics
```

## 📈 Performance Optimization

### 1. Instance Specifications

**Small Environment**:
- Instance type: `t2.small`
- Disk size: 20GB

**Medium Environment**:
- Instance type: `t2.medium` (current default)
- Disk size: 50GB

**Large Environment**:
- Instance type: `t3.large`
- Disk size: 100GB

### 2. Data Retention Policy

Add data retention policy in Prometheus configuration:

```yaml
storage:
  tsdb:
    retention.time: 15d
    retention.size: 10GB
```

### 3. Resource Limits

Set resource limits for services to prevent over-consumption:

```yaml
# In systemd service file
[Service]
MemoryMax=1G
CPUQuota=50%
```

## 🔒 Security Recommendations

1. **Change Default Passwords**: Modify Grafana admin password immediately after deployment
2. **Network Security**: Configure security groups to allow only necessary ports
3. **SSL/TLS**: Enable HTTPS in production environments
4. **Access Control**: Configure Grafana user roles and permissions
5. **Key Management**: Use AWS KMS or Parameter Store for sensitive information management

## 📚 Technology Stack Details

| Technology | Version | Purpose |
|------------|---------|---------|
| Terraform | >=1.0 | Infrastructure as Code |
| Ansible | >=2.9 | Configuration Management |
| AWS EC2 | - | Cloud Computing Resources |
| Prometheus | 2.53.0 | Metrics Collection |
| Grafana | 11.0.0 | Data Visualization |
| Node Exporter | 1.8.1 | System Metrics Export |
| Python | 3.8+ | AIOps Scripts |
| scikit-learn | latest | Machine Learning Algorithms |
| pandas | latest | Data Processing |

## 🤝 Contributing

1. Fork the project
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📄 License

This project is for learning and research purposes only. Please ensure appropriate security best practices are followed in production environments.

## 📞 Support

If you encounter issues, please check:
1. [Troubleshooting](#troubleshooting) section
2. Service log files
3. AWS CloudWatch logs (if configured)

---

**Project Author**: Cyper
**Last Updated**: October 2025
**Project Status**: In Development - Suitable for DevOps learning and experimental environments