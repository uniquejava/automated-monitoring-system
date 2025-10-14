#!/usr/bin/env python3
"""
本地版本的 Custom Prometheus Metrics Exporter
为 AIOps 提供系统与自定义指标 - 修改用于本地测试
"""

import os
import random
import signal
from http.server import HTTPServer, BaseHTTPRequestHandler

import psutil

# 本地测试配置
PORT = int(os.getenv("EXPORTER_PORT", "8000"))
# 修改为本地路径
ANOMALY_SCORE_FILE = os.path.join(os.path.dirname(__file__), "anomaly_score.txt")


class MetricsHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/metrics":
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; version=0.0.4")
            self.end_headers()
            self.wfile.write(self.collect_metrics().encode())
        elif self.path == "/healthz":
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"ok")
        else:
            self.send_response(404)
            self.end_headers()

    def collect_metrics(self):
        """采集系统和自定义指标"""
        try:
            load1, load5, load15 = psutil.getloadavg()
        except AttributeError:
            # Windows系统可能没有getloadavg()
            load1, load5, load15 = 0.0, 0.0, 0.0

        cpu_percent = psutil.cpu_percent(interval=0.1)
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage("/")
        process_count = len(psutil.pids())

        try:
            net_conn = len(psutil.net_connections())
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            net_conn = 0

        # 模拟自定义业务指标
        custom_metric = random.uniform(0, 100)

        # AIOps异常分数（若存在）
        anomaly_score = 0.0
        if os.path.exists(ANOMALY_SCORE_FILE):
            try:
                with open(ANOMALY_SCORE_FILE, "r") as f:
                    anomaly_score = float(f.read().strip())
            except Exception:
                pass

        metrics = f"""# HELP system_load_average System load average
# TYPE system_load_average gauge
system_load_average_1m {load1}
system_load_average_5m {load5}
system_load_average_15m {load15}

# HELP cpu_usage_percent CPU usage percent
# TYPE cpu_usage_percent gauge
cpu_usage_percent {cpu_percent}

# HELP memory_usage_percent Memory usage percent
# TYPE memory_usage_percent gauge
memory_usage_percent {mem.percent}

# HELP disk_usage_percent Disk usage percent
# TYPE disk_usage_percent gauge
disk_usage_percent {disk.percent}

# HELP system_process_count Process count
# TYPE system_process_count gauge
system_process_count {process_count}

# HELP system_network_connections Active network connections
# TYPE system_network_connections gauge
system_network_connections {net_conn}

# HELP custom_application_metric Example business metric
# TYPE custom_application_metric gauge
custom_application_metric {custom_metric}

# HELP aiops_anomaly_score AIOps anomaly score (0-1)
# TYPE aiops_anomaly_score gauge
aiops_anomaly_score {anomaly_score}
"""
        return metrics

    def log_message(self, *args):
        # 禁用默认日志
        pass


def run_server():
    server = HTTPServer(("0.0.0.0", PORT), MetricsHandler)
    print(f"✅ Metrics Exporter started at http://localhost:{PORT}")
    print(f"📊 Metrics: http://localhost:{PORT}/metrics")
    print(f"🏥 Health: http://localhost:{PORT}/healthz")
    print(f"📁 Anomaly score file: {ANOMALY_SCORE_FILE}")

    def shutdown(signum, frame):
        print("\n🛑 Shutting down exporter gracefully...")
        server.shutdown()

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    server.serve_forever()


if __name__ == "__main__":
    # 确保异常分数文件存在
    os.makedirs(os.path.dirname(ANOMALY_SCORE_FILE), exist_ok=True)
    if not os.path.exists(ANOMALY_SCORE_FILE):
        with open(ANOMALY_SCORE_FILE, "w") as f:
            f.write("0.0")

    run_server()