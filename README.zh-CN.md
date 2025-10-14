# 自动化监控环境部署系统

一个完整的 DevOps 与 Platform工程项目，实现从基础设施自动化到监控与AIOps初步集成的完整流程。

[English](README.md) | 简体中文

## 🎯 项目概述

本项目构建了一个基于AWS EC2的自动化监控系统，集成了Prometheus、Grafana和AIOps异常检测功能，实现：

- 🏗️ **基础设施自动化**：使用Terraform自动化部署AWS环境
- ⚙️ **服务配置管理**：使用Ansible配置监控服务
- 📊 **监控指标收集**：自动收集系统和自定义业务指标
- 🤖 **智能异常检测**：集成机器学习模型进行异常检测
- 📈 **可视化仪表板**：Grafana数据可视化

## 🏛️ 系统架构

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

## 📁 项目结构

```
automated-monitoring-system/
├── 📋 README.md                          # 项目文档 (英文)
├── 📋 README.zh-CN.md                     # 项目文档 (中文)
├── 🚀 scripts/deploy.sh                  # 主部署脚本
├── 🔧 scripts/destroy.sh                 # 资源清理脚本
├── 🔑 monitoring-key.pem                 # SSH密钥（需要生成）
├── 📂 infra/                             # Terraform配置
│   ├── 🌐 network.tf                     # 网络配置
│   ├── 🖥️  ec2.tf                        # EC2实例配置
│   ├── 🔐 variables.tf                   # 变量定义
│   ├── 📤 outputs.tf                     # 输出定义
│   └── 📋 versions.tf                    # Terraform版本
├── 📂 ansible/                           # Ansible配置
│   ├── 📜 playbook.yml                   # 主剧本
│   ├── 📂 group_vars/                    # 组变量
│   │   └── 📄 all.yml                    # 全局变量
│   ├── 📂 roles/                         # 角色定义
│   │   ├── 📂 common/                    # 通用配置
│   │   ├── 📂 prometheus/                # Prometheus配置
│   │   ├── 📂 node_exporter/             # Node Exporter配置
│   │   ├── 📂 grafana/                   # Grafana配置
│   │   └── 📂 aiops/                     # AIOps异常检测
│   │       ├── 📂 tasks/
│   │       │   └── 📄 main.yml
│   │       ├── 📂 files/
│   │       │   ├── 📊 metrics_exporter.py
│   │       │   └── 🤖 anomaly_detector.py
│   │       └── 📂 templates/
│   └── 📂 files/                         # 配置文件
├── 📂 docs/                              # 文档目录
│   └── 📄 metrics.md                     # 指标文档
└── 📂 scripts/                           # 辅助脚本
    └── ⏳ wait-for-ssh.sh                # SSH等待脚本
```

## 🚀 快速开始

### 前置要求

- ✅ [Terraform](https://www.terraform.io/downloads.html) >= 1.0
- ✅ [Ansible](https://docs.ansible.com/ansible/latest/installation_guide/) >= 2.9
- ✅ [AWS CLI](https://aws.amazon.com/cli/) 已配置
- ✅ AWS凭证已配置（环境变量或~/.aws/credentials）

### 一键部署

```bash
# 1. 克隆项目
git clone <your-repo-url>
cd automated-monitoring-system

# 2. 生成SSH密钥对（如果没有）
ssh-keygen -t rsa -b 4096 -f monitoring-key.pem -N ""

# 3. 在AWS中导入公钥
aws ec2 import-key-pair \
    --key-name monitoring-key \
    --public-key-material fileb://monitoring-key.pem.pub \
    --region ap-northeast-1

# 4. 执行部署
chmod +x scripts/deploy.sh scripts/wait-for-ssh.sh scripts/destroy.sh
./scripts/deploy.sh
```

部署完成后，你将看到：
```
✅ 部署完成!
📊 Grafana: http://<INSTANCE_IP>:3000
🔍 Prometheus: http://<INSTANCE_IP>:9090
```

## 🔧 详细配置

### Terraform配置

**AWS区域** (`infra/variables.tf`):
```hcl
variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "ap-northeast-1"
}
```

**实例类型**:
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

### Ansible配置

**全局变量** (`ansible/group_vars/all.yml`):
```yaml
# 服务版本
prometheus_version: "2.53.0"
node_exporter_version: "1.8.1"
grafana_version: "11.0.0"

# 路径配置
prometheus_dir: /opt/prometheus
node_exporter_dir: /opt/node_exporter
grafana_dir: /opt/grafana

# Prometheus配置
prometheus_scrape_interval: 15s
prometheus_targets:
  - localhost:9100
  - localhost:8000  # AIOps自定义指标

# Grafana配置
grafana_admin_user: admin
grafana_admin_password: admin
```

## 📊 监控功能

### 1. 系统指标监控

通过Node Exporter收集以下系统指标：
- **CPU使用率**: 实时CPU使用情况
- **内存使用率**: 内存使用情况
- **磁盘使用率**: 磁盘空间使用情况
- **网络流量**: 网络收发字节数
- **系统负载**: 1分钟、5分钟、15分钟负载平均值

### 2. 自定义业务指标

通过AIOps Metrics Exporter提供：
- **系统负载平均值**: 更精确的负载指标
- **进程数量**: 系统运行的进程总数
- **网络连接数**: 活跃的网络连接数
- **自定义业务指标**: 模拟的业务KPI
- **异常分数**: AIOps异常检测分数

### 3. AIOps异常检测

**异常检测算法**:
- 使用Isolation Forest机器学习算法
- 结合多种系统指标进行异常检测
- 实时计算异常分数(0-1范围)

**检测指标**:
```python
metrics = {
    "cpu_usage": CPU使用率,
    "memory_usage": 内存使用率,
    "disk_usage": 磁盘使用率,
    "network_rx": 网络接收速率
}
```

**异常分数说明**:
- `0.0 - 0.3`: 系统正常
- `0.3 - 0.7`: 轻微异常，需要关注
- `0.7 - 1.0`: 严重异常，需要立即处理

## 🖥️ 访问监控平台

### Grafana Dashboard

访问地址: `http://<INSTANCE_IP>:3000`

- **用户名**: `admin`
- **密码**: `admin` (可在`ansible/group_vars/all.yml`中修改)

**推荐配置**:
1. 导入Prometheus数据源（已自动配置）
2. 创建系统监控仪表板
3. 设置AIOps异常分数图表
4. 配置告警规则

### Prometheus

访问地址: `http://<INSTANCE_IP>:9090`

**查询示例**:
```promql
# CPU使用率
100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)

# 内存使用率
(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100

# AIOps异常分数
aiops_anomaly_score
```

## 🤖 AIOps功能详解

### 1. 指标导出器 (`metrics_exporter.py`)

```python
# 运行在端口8000
# 提供自定义指标端点: /metrics
# 健康检查端点: /healthz
```

**主要指标**:
- `system_load_average_1m/5m/15m`: 系统负载
- `cpu_usage_percent`: CPU使用率
- `memory_usage_percent`: 内存使用率
- `custom_application_metric`: 自定义业务指标
- `aiops_anomaly_score`: 异常检测分数

### 2. 异常检测器 (`anomaly_detector.py`)

**工作流程**:
1. **数据收集**: 从Prometheus查询系统指标
2. **历史存储**: 维护最近200个数据点的历史记录
3. **特征标准化**: 使用StandardScaler标准化数据
4. **异常检测**: Isolation Forest算法检测异常
5. **分数计算**: 计算当前系统异常分数

**检测间隔**: 建议设置为5分钟运行一次

## 📚 文档

- **[指标文档](docs/metrics.md)** - 完整的指标目录和说明
- **[CLAUDE.md](CLAUDE.md)** - Claude Code 开发指南

## 🔍 故障排查

### 常见问题

**1. SSH连接失败**
```bash
# 检查密钥权限
chmod 600 monitoring-key.pem

# 检查安全组配置
aws ec2 describe-security-groups --group-ids <sg-id>
```

**2. 服务启动失败**
```bash
# 登录实例检查服务状态
ssh -i monitoring-key.pem ec2-user@<INSTANCE_IP>
sudo systemctl status prometheus
sudo systemctl status grafana-server
```

**3. Prometheus无法访问**
```bash
# 检查Prometheus配置
sudo cat /opt/prometheus/prometheus.yml

# 检查防火墙
sudo ufw status
```

**4. Grafana无法连接Prometheus**
```bash
# 检查数据源配置
sudo cat /etc/grafana/provisioning/datasources/datasource.yml

# 重启Grafana
sudo systemctl restart grafana-server
```

### 日志查看

```bash
# AIOps日志
sudo tail -f /opt/monitoring/aiops/aiops.log

# Prometheus日志
sudo journalctl -u prometheus -f

# Grafana日志
sudo journalctl -u grafana-server -f
```

## 🧹 清理资源

当不再需要监控环境时，运行清理脚本：

```bash
./scripts/destroy.sh
```

**手动清理步骤**:
```bash
# 1. 销毁Terraform资源
cd infra
terraform destroy -auto-approve

# 2. 删除SSH密钥对（可选）
aws ec2 delete-key-pair --key-name monitoring-key --region ap-northeast-1

# 3. 删除本地密钥文件（可选）
rm -f monitoring-key.pem monitoring-key.pem.pub
```

## 🔧 自定义配置

### 修改监控目标

编辑 `ansible/roles/templates/prometheus.yml.j2`:

```yaml
scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'node'
    static_configs:
      - targets: ['localhost:9100']

  # 添加新的监控目标
  - job_name: 'custom-app'
    static_configs:
      - targets: ['<TARGET_IP>:<PORT>']
```

### 添加Grafana仪表板

1. 在Grafana中创建仪表板
2. 导出为JSON文件
3. 放置在 `ansible/roles/grafana/files/dashboards/`
4. 更新Grafana角色配置以自动导入

### 自定义AIOps检测

修改 `ansible/roles/aiops/files/anomaly_detector.py`:

```python
# 添加新的检测指标
def collect_metrics(self):
    metrics = {
        "cpu_usage": self.query_metric('...'),
        "memory_usage": self.query_metric('...'),
        # 添加新指标
        "custom_metric": self.query_metric('<your_prometheus_query>'),
    }
    return metrics
```

## 📈 性能优化

### 1. 实例规格建议

**小型环境**:
- 实例类型: `t2.small`
- 磁盘大小: 20GB

**中型环境**:
- 实例类型: `t2.medium` (当前默认)
- 磁盘大小: 50GB

**大型环境**:
- 实例类型: `t3.large`
- 磁盘大小: 100GB

### 2. 数据保留策略

在Prometheus配置中添加数据保留策略:

```yaml
storage:
  tsdb:
    retention.time: 15d
    retention.size: 10GB
```

### 3. 资源限制

为服务设置资源限制以防止过度消耗:

```yaml
# 在systemd服务文件中
[Service]
MemoryMax=1G
CPUQuota=50%
```

## 🔒 安全建议

1. **修改默认密码**: 部署后立即修改Grafana管理员密码
2. **网络安全**: 配置安全组只允许必要的端口
3. **SSL/TLS**: 在生产环境中启用HTTPS
4. **访问控制**: 配置Grafana的用户角色和权限
5. **密钥管理**: 使用AWS KMS或Parameter Store管理敏感信息

## 📚 技术栈详情

| 技术 | 版本 | 用途 |
|------|------|------|
| Terraform | >=1.0 | 基础设施即代码 |
| Ansible | >=2.9 | 配置管理 |
| AWS EC2 | - | 云计算资源 |
| Prometheus | 2.53.0 | 监控数据收集 |
| Grafana | 11.0.0 | 数据可视化 |
| Node Exporter | 1.8.1 | 系统指标导出 |
| Python | 3.8+ | AIOps脚本 |
| scikit-learn | latest | 机器学习算法 |
| pandas | latest | 数据处理 |

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证

本项目仅供学习和研究使用。请确保在生产环境中遵循相应的安全最佳实践。

## 📞 支持

如遇到问题，请检查：
1. [故障排查](#故障排查)部分
2. 各服务的日志文件
3. AWS CloudWatch日志（如果配置）

---

**项目作者**: Cyper
**最后更新**: 2025年10月
**项目状态**: 开发中 - 适用于DevOps学习和实验环境