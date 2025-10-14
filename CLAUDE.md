# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an automated monitoring system that deploys a comprehensive monitoring stack on AWS EC2 using Terraform and Ansible. The system includes Prometheus for metrics collection, Grafana for visualization, Node Exporter for system metrics, and custom AIOps components for anomaly detection using machine learning.

## Development Commands

### Deployment and Management
```bash
# Deploy the entire monitoring stack
./deploy.sh

# Destroy all AWS resources
./destroy.sh

# Wait for SSH connectivity (used internally by deploy.sh)
./scripts/wait-for-ssh.sh <INSTANCE_IP>
```

### Local Testing and Development
```bash
# Install dependencies
uv sync

# Run local AIOps tests
cd local_test
python test_runner.py

# Run individual components locally
python metrics_exporter_local.py      # Local metrics exporter
python anomaly_detector_local.py      # Local anomaly detection
```

## System Architecture

### Infrastructure Layer
- **Terraform** (`infra/`): AWS infrastructure provisioning
  - EC2 instances in VPC with security groups
  - SSH key management and network configuration
  - Variables configured in `infra/variables.tf`

### Configuration Layer
- **Ansible** (`ansible/`): Service configuration and deployment
  - Main playbook: `ansible/playbook.yml`
  - Global variables: `ansible/group_vars/all.yml`
  - Role-based architecture for each service

### Monitoring Stack
- **Prometheus**: Metrics collection and storage (port 9090)
- **Grafana**: Data visualization and dashboards (port 3000)
- **Node Exporter**: System metrics export (port 9100)
- **AIOps Components**: Custom metrics and anomaly detection (port 8000)

### AIOps Components
- **Metrics Exporter** (`ansible/roles/aiops/files/metrics_exporter.py`):
  - Exposes custom system and business metrics on `/metrics` endpoint
  - Health check on `/healthz`
  - Reads anomaly scores from shared file

- **Anomaly Detector** (`ansible/roles/aiops/files/anomaly_detector.py`):
  - Uses Isolation Forest ML algorithm for anomaly detection
  - Queries Prometheus for system metrics
  - Maintains historical data in CSV format
  - Writes anomaly scores to shared file

## Key Configuration Files

### Service Versions and Paths
- Located in `ansible/group_vars/all.yml`
- Controls Prometheus, Node Exporter, and Grafana versions
- Defines installation paths and scrape intervals

### Terraform Variables
- AWS region: `ap-northeast-1` (default)
- Instance type: `t2.medium` (default)
- AMI ID: Ubuntu 24.04 LTS
- SSH key path: `../monitoring-key.pem`

### Ansible Roles Structure
```
ansible/roles/
├── common/          # System preparation
├── prometheus/      # Prometheus server configuration
├── node_exporter/   # System metrics exporter
├── grafana/         # Visualization platform
└── aiops/           # Custom AIOps components
```

## Python Dependencies

Main project dependencies in `pyproject.toml`:
- `psutil>=5.9.0` - System metrics collection
- `requests>=2.28.0` - HTTP client for Prometheus API
- `pandas>=1.5.0` - Data manipulation
- `numpy>=1.24.0` - Numerical computations
- `scikit-learn>=1.3.0` - Machine learning algorithms

Development dependencies:
- `pytest>=7.0.0` - Testing framework
- `httpx>=0.24.0` - Async HTTP client

## Local Development

### Testing AIOps Components
The `local_test/` directory contains local versions of the AIOps components:
- `test_runner.py` - orchestrates local testing
- `metrics_exporter_local.py` - local metrics server
- `anomaly_detector_local.py` - local anomaly detection
- Uses local data files (`metrics_history.csv`, `anomaly_score.txt`, `aiops.log`)

### Environment Setup
1. Generate SSH key pair: `ssh-keygen -t rsa -b 4096 -f monitoring-key.pem -N ""`
2. Import public key to AWS: `aws ec2 import-key-pair --key-name monitoring-key --public-key-material fileb://monitoring-key.pem.pub`
3. Ensure AWS credentials are configured in environment

## Anomaly Detection System

### Detection Algorithm
- **Isolation Forest**: ML algorithm for anomaly detection
- **Features**: CPU usage, memory usage, disk usage, network receive rate
- **Scoring**: 0.0-1.0 range (0.0-0.3 normal, 0.3-0.7 mild anomaly, 0.7-1.0 severe)
- **History**: Maintains last 200 data points for training

### Metrics Collection
The system collects both system metrics via Node Exporter and custom business metrics via the AIOps metrics exporter, providing comprehensive monitoring capabilities.

## Service Access

After deployment, access the monitoring stack at:
- **Grafana**: `http://<INSTANCE_IP>:3000` (admin/admin)
- **Prometheus**: `http://<INSTANCE_IP>:9090`
- **Node Exporter**: `http://<INSTANCE_IP>:9100/metrics`
- **AIOps Metrics**: `http://<INSTANCE_IP>:8000/metrics`