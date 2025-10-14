# 监控指标文档 (Metrics Documentation)

本文档详细说明了自动化监控系统中收集的所有指标，包括系统指标、自定义业务指标和 AIOps 异常检测指标。

## 📊 指标概览

### LETS 监控框架实现状态

| 指标类型 | 实现状态 | 说明 |
|----------|----------|------|
| **L - Latency (延迟)** | ❌ 未实现 | 需要应用层响应时间指标 |
| **E - Errors (错误)** | ❌ 未实现 | 需要错误计数指标 |
| **T - Traffic (流量)** | ✅ 已实现 | 网络流量、磁盘 I/O |
| **S - Saturation (饱和度)** | ✅ 已实现 | CPU、内存、磁盘使用率 |

## 🔧 Node Exporter 系统指标

Node Exporter 提供全面的系统级指标收集，运行在端口 `9100`。

### CPU 指标
- **`node_cpu_seconds_total`**: CPU 时间统计（按模式分类）
  - `mode="idle"`: 空闲时间
  - `mode="user"`: 用户态时间
  - `mode="system"`: 内核态时间
  - `mode="iowait"`: I/O 等待时间

### 内存指标
- **`node_memory_MemTotal_bytes`**: 总内存量
- **`node_memory_MemAvailable_bytes`**: 可用内存量
- **`node_memory_MemFree_bytes`**: 空闲内存量
- **`node_memory_Buffers_bytes`**: 缓冲区内存
- **`node_memory_Cached_bytes`**: 缓存内存

### 磁盘指标
- **`node_disk_read_bytes_total`**: 磁盘读取总字节数
- **`node_disk_write_bytes_total`**: 磁盘写入总字节数
- **`node_disk_reads_completed_total`**: 磁盘读取操作总数
- **`node_disk_writes_completed_total`**: 磁盘写入操作总数
- **`node_disk_io_time_seconds_total`**: 磁盘 I/O 时间总计

### 网络指标 (T - Traffic)
- **`node_network_receive_bytes_total`**: 网络接收字节总数
- **`node_network_transmit_bytes_total`**: 网络发送字节总数
- **`node_network_receive_packets_total`**: 网络接收包总数
- **`node_network_transmit_packets_total`**: 网络发送包总数

### 文件系统指标
- **`node_filesystem_size_bytes`**: 文件系统总大小
- **`node_filesystem_avail_bytes`**: 文件系统可用空间
- **`node_filesystem_free_bytes`**: 文件系统空闲空间
- **`node_filesystem_files`**: 文件系统文件总数
- **`node_filesystem_files_free`**: 文件系统空闲文件数

### 系统负载指标 (S - Saturation)
- **`node_load1`**: 1分钟平均负载
- **`node_load5`**: 5分钟平均负载
- **`node_load15`**: 15分钟平均负载

## 🤖 AIOps 自定义指标

AIOps 组件运行在端口 `8000`，提供自定义业务指标和异常检测功能。

### 系统资源指标 (S - Saturation)
- **`cpu_usage_percent`**: CPU 使用率百分比
  - 查询公式: `100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)`

- **`memory_usage_percent`**: 内存使用率百分比
  - 查询公式: `(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100`

- **`disk_usage_percent`**: 磁盘使用率百分比
  - 查询公式: `(1 - (node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"})) * 100`

### 系统负载指标
- **`system_load_average_1m`**: 1分钟系统负载平均值
- **`system_load_average_5m`**: 5分钟系统负载平均值
- **`system_load_average_15m`**: 15分钟系统负载平均值

### 进程和网络指标
- **`system_process_count`**: 系统运行的进程总数
- **`system_network_connections`**: 活跃的网络连接数

### 业务指标
- **`custom_application_metric`**: 示例业务指标
  - 可以根据实际业务需求自定义

### 异常检测指标
- **`aiops_anomaly_score`**: AIOps 异常检测分数 (0-1)
  - `0.0 - 0.3`: 系统正常
  - `0.3 - 0.7`: 轻微异常，需要关注
  - `0.7 - 1.0`: 严重异常，需要立即处理

## 📈 常用 PromQL 查询示例

### 基础资源使用率
```promql
# CPU 使用率
100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)

# 内存使用率
(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100

# 磁盘使用率
(1 - (node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"})) * 100

# 系统负载
node_load1
```

### 网络流量 (T - Traffic)
```promql
# 网络接收速率 (bytes/sec)
rate(node_network_receive_bytes_total[5m])

# 网络发送速率 (bytes/sec)
rate(node_network_transmit_bytes_total[5m])

# 网络接收速率 (bits/sec)
rate(node_network_receive_bytes_total[5m]) * 8

# 网络发送速率 (bits/sec)
rate(node_network_transmit_bytes_total[5m]) * 8
```

### 磁盘 I/O (T - Traffic)
```promql
# 磁盘读取速率
rate(node_disk_read_bytes_total[5m])

# 磁盘写入速率
rate(node_disk_write_bytes_total[5m])

# 磁盘 I/O 操作速率
rate(node_disk_reads_completed_total[5m])
rate(node_disk_writes_completed_total[5m])
```

### AIOps 自定义指标
```promql
# 异常检测分数
aiops_anomaly_score

# 系统进程数
system_process_count

# 网络连接数
system_network_connections

# 自定义业务指标
custom_application_metric
```

## 🎯 Grafana Dashboard

项目包含预配置的 Grafana Dashboard (`aiops-monitoring-dashboard.json`)，可视化所有关键指标：

### Dashboard 面板布局
1. **系统资源使用率** - CPU、内存、磁盘使用率时间序列图
2. **AIOps 异常检测分数** - 带颜色阈值的实时数值
3. **系统负载平均值** - 1分钟、5分钟、15分钟负载
4. **网络流量** - 接收/传输速率 (T-Traffic)
5. **磁盘 I/O** - 读写速率 (T-Traffic)
6. **自定义业务指标** - 进程数、网络连接数等
7. **饱和度指标** - CPU、内存、磁盘使用率实时数值 (S-Saturation)

### 导入方法
1. 访问 Grafana: `http://<INSTANCE_IP>:3000` (admin/admin)
2. 点击 **+ → Import**
3. 上传 `aiops-monitoring-dashboard.json`
4. 选择 Prometheus 数据源
5. 点击 **Import**

## 🚀 扩展指标建议

### 延迟指标 (L - Latency)
```promql
# HTTP 响应时间 (需要应用层实现)
http_request_duration_seconds

# 数据库查询时间 (需要应用层实现)
db_query_duration_seconds

# API 调用延迟 (需要应用层实现)
api_response_time_seconds
```

### 错误指标 (E - Errors)
```promql
# HTTP 错误计数 (需要应用层实现)
http_requests_total{status=~"5.."}

# 应用异常数 (需要应用层实现)
application_exceptions_total

# 失败请求率 (需要应用层实现)
rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m])
```

## 🔍 指标采集配置

### Prometheus 抓取配置
```yaml
scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'node_exporter'
    static_configs:
      - targets: ['localhost:9100']

  - job_name: 'aiops'
    static_configs:
      - targets: ['localhost:8000']
```

### 抓取间隔
- **Prometheus**: 15秒
- **Node Exporter**: 15秒
- **AIOps Metrics**: 15秒

### 数据保留策略
- **Prometheus**: 默认15天
- **AIOps 历史数据**: 200个数据点 (约16.7小时)

## 📚 相关文档

- [主 README](../README.md) - 项目概述和快速开始
- [CLAUDE.md](../CLAUDE.md) - Claude Code 开发指南
- [Grafana Dashboard](../aiops-monitoring-dashboard.json) - 预配置仪表板

## 🛠️ 故障排查

### 指标缺失检查
```bash
# 检查 Prometheus 目标状态
curl http://localhost:9090/api/v1/targets

# 检查 Node Exporter 指标
curl http://localhost:9100/metrics | head -20

# 检查 AIOps 指标
curl http://localhost:8000/metrics | head -20
```

### 服务状态检查
```bash
# 检查服务运行状态
systemctl status prometheus
systemctl status grafana-server
systemctl status aiops-exporter
```

### 日志查看
```bash
# Prometheus 日志
journalctl -u prometheus -f

# Grafana 日志
journalctl -u grafana-server -f

# AIOps 日志
tail -f /opt/monitoring/aiops/aiops.log
```