# AIOps 本地测试环境

这个目录包含了用于本地测试AIOps功能的所有文件。

## 📁 文件说明

- `metrics_exporter_local.py` - 本地版本的指标导出器
- `anomaly_detector_local.py` - 本地版本的异常检测器
- `test_runner.py` - 测试运行器，提供一键测试功能
- `README.md` - 本说明文件

## 🚀 快速开始

### 1. 安装依赖

确保你已安装uv，然后在项目根目录运行：

```bash
# 安装项目依赖
uv sync

# 或者安装开发依赖（包含测试工具）
uv sync --dev
```

### 2. 运行测试

```bash
# 进入测试目录
cd local_test

# 运行完整测试
python test_runner.py test

# 或者只检查依赖
python test_runner.py check

# 或者只生成测试数据
python test_runner.py generate

# 或者只运行异常检测
python test_runner.py detect
```

## 🧪 测试功能

### 完整测试流程

运行 `python test_runner.py test` 将会：

1. ✅ 检查所有必需的依赖包
2. 🚀 启动 Metrics Exporter (端口8000)
3. 🧪 测试所有HTTP端点
4. 📊 生成50个测试数据点（包含正常和异常数据）
5. 🔍 运行异常检测算法
6. 📋 显示测试结果和生成的文件

### 手动测试

#### 启动指标导出器

```bash
cd local_test
python metrics_exporter_local.py
```

然后在浏览器访问：
- 📊 Metrics: http://localhost:8000/metrics
- 🏥 Health: http://localhost:8000/healthz

#### 运行异常检测

```bash
# 生成测试数据
python anomaly_detector_local.py --generate-test-data

# 运行异常检测
python anomaly_detector_local.py
```

## 📊 生成的文件

测试完成后，会在当前目录生成：

- `anomaly_score.txt` - 当前异常分数 (0-1)
- `metrics_history.csv` - 历史指标数据
- `aiops.log` - 异常检测日志

### 异常分数说明

- `0.0 - 0.3`: 系统正常
- `0.3 - 0.7`: 轻微异常，需要关注
- `0.7 - 1.0`: 严重异常，需要立即处理

## 🔧 配置选项

可以通过环境变量修改配置：

```bash
# 修改指标导出器端口
export EXPORTER_PORT=8080
python metrics_exporter_local.py

# 修改Prometheus URL（如果使用真实的Prometheus）
export PROMETHEUS_URL=http://your-prometheus:9090
python anomaly_detector_local.py
```

## 🐛 故障排查

### 1. 依赖问题

如果遇到依赖问题，请确保：

```bash
# 在项目根目录运行
uv sync

# 检查uv是否正确安装
uv --version
```

### 2. 端口冲突

如果8000端口被占用，修改端口：

```bash
export EXPORTER_PORT=8080
python metrics_exporter_local.py
```

### 3. 权限问题

某些系统指标可能需要管理员权限才能访问。如果遇到权限错误：

```bash
# macOS/Linux
sudo python metrics_exporter_local.py

# 或者使用用户级别的指标收集
```

### 4. Windows兼容性

代码已经针对Windows系统进行了优化：
- 自动处理`psutil.getloadavg()`在某些Windows版本上的兼容性问题
- 处理网络连接权限问题

## 📈 扩展测试

### 添加自定义指标

可以修改 `metrics_exporter_local.py` 来添加更多自定义指标：

```python
# 在 collect_metrics 方法中添加
custom_metric_2 = random.uniform(0, 1000)
```

### 修改异常检测算法

可以修改 `anomaly_detector_local.py` 中的检测算法：

```python
# 调整IsolationForest参数
model = IsolationForest(contamination=0.2, random_state=42)  # 调整异常比例
```

### 集成真实Prometheus

如果你有真实的Prometheus实例：

1. 修改环境变量：
   ```bash
   export PROMETHEUS_URL=http://your-prometheus:9090
   ```

2. 确保Prometheus中有相应的指标

3. 运行测试：
   ```bash
   python anomaly_detector_local.py
   ```

## 📝 日志查看

所有操作都会记录在 `aiops.log` 文件中：

```bash
# 实时查看日志
tail -f aiops.log

# 查看完整日志
cat aiops.log
```