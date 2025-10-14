#!/usr/bin/env python3
"""
本地版本的 AIOps 异常检测系统
结合统计与机器学习模型检测系统指标异常 - 修改用于本地测试
"""

import json
import logging
import os
import sys
import time
from datetime import datetime

import numpy as np
import pandas as pd
import requests
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

# === 本地测试配置 ===
PROM_URL = os.getenv("PROMETHEUS_URL", "http://localhost:8000")  # 指向本地metrics exporter
METRICS_URL = f"{PROM_URL}/metrics"
HISTORY_FILE = os.path.join(os.path.dirname(__file__), "metrics_history.csv")
ANOMALY_SCORE_FILE = os.path.join(os.path.dirname(__file__), "anomaly_score.txt")
LOG_FILE = os.path.join(os.path.dirname(__file__), "aiops.log")
MAX_HISTORY = 200  # 保留历史数据点数量

# === 日志配置 ===
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)


class LocalMetricsCollector:
    """本地指标收集器 - 从本地metrics exporter收集数据"""

    def __init__(self, metrics_url=METRICS_URL):
        self.metrics_url = metrics_url

    def parse_metrics(self, metrics_text):
        """解析Prometheus格式的metrics文本"""
        metrics = {}
        for line in metrics_text.split('\n'):
            line = line.strip()
            if line and not line.startswith('#'):
                if ' ' in line:
                    name, value = line.split(' ', 1)
                    try:
                        metrics[name] = float(value)
                    except ValueError:
                        continue
        return metrics

    def collect_local_metrics(self):
        """从本地metrics exporter收集指标"""
        try:
            response = requests.get(self.metrics_url, timeout=10)
            response.raise_for_status()
            metrics = self.parse_metrics(response.text)

            # 转换为异常检测器需要的格式
            transformed_metrics = {
                "cpu_usage": metrics.get("cpu_usage_percent", 0.0),
                "memory_usage": metrics.get("memory_usage_percent", 0.0),
                "disk_usage": metrics.get("disk_usage_percent", 0.0),
                "network_rx": metrics.get("custom_application_metric", 0.0),  # 使用自定义指标模拟网络流量
            }

            return transformed_metrics
        except Exception as e:
            logging.warning(f"本地指标收集失败: {e}")
            # 返回模拟数据
            return {
                "cpu_usage": np.random.uniform(10, 80),
                "memory_usage": np.random.uniform(20, 90),
                "disk_usage": np.random.uniform(30, 70),
                "network_rx": np.random.uniform(0, 100)
            }


class AIOpsAnomalyDetector:
    def __init__(self, prometheus_url=PROM_URL):
        self.prometheus_url = prometheus_url
        self.metrics_collector = LocalMetricsCollector()

    def query_metric(self, query):
        """查询 Prometheus 指标 - 本地版本直接从metrics exporter获取"""
        try:
            metrics = self.metrics_collector.collect_local_metrics()
            # 简化版本，直接返回对应指标
            return metrics.get(query.split('{')[0].replace('rate(', '').replace('node_', '').replace('_total', '').replace('_bytes', ''), 0.0)
        except Exception as e:
            logging.warning(f"指标查询失败: {query} ({e})")
            return np.nan

    def collect_metrics(self):
        """收集基础指标"""
        return self.metrics_collector.collect_local_metrics()

    def update_history(self, new_metrics):
        """更新历史指标数据"""
        df_new = pd.DataFrame([new_metrics])
        df_new["timestamp"] = datetime.now()

        if os.path.exists(HISTORY_FILE):
            df = pd.read_csv(HISTORY_FILE)
            df = pd.concat([df, df_new], ignore_index=True)
            df = df.tail(MAX_HISTORY)
        else:
            df = df_new

        df.to_csv(HISTORY_FILE, index=False)
        return df

    def detect_anomalies(self, df):
        """使用 IsolationForest 检测异常"""
        if len(df) < 10:
            return 0.0  # 数据太少，不判断异常

        features = ["cpu_usage", "memory_usage", "disk_usage", "network_rx"]
        df = df.dropna(subset=features)

        if len(df) < 10:
            return 0.0

        scaler = StandardScaler()
        X = scaler.fit_transform(df[features])

        model = IsolationForest(contamination=0.1, random_state=42)
        preds = model.fit_predict(X)
        score = (preds == -1).mean()  # 异常比例

        return float(score)

    def run(self):
        logging.info("开始异常检测...")
        metrics = self.collect_metrics()
        if any(np.isnan(list(metrics.values()))):
            logging.warning("部分指标获取失败，跳过本轮检测")
            return

        df = self.update_history(metrics)
        score = self.detect_anomalies(df)

        # 写入异常分数文件
        with open(ANOMALY_SCORE_FILE, "w") as f:
            f.write(str(round(score, 4)))

        logging.info(json.dumps({
            "timestamp": datetime.now().isoformat(),
            "anomaly_score": score,
            "metrics": metrics
        }, ensure_ascii=False))

        if score > 0.5:
            logging.warning(f"⚠️ 检测到异常 (score={score:.2f})")
        else:
            logging.info("✅ 系统运行正常")

        return score

    def generate_test_data(self, num_points=50):
        """生成测试数据用于验证异常检测"""
        logging.info(f"生成 {num_points} 个测试数据点...")

        for i in range(num_points):
            # 生成正常数据
            if i < num_points * 0.8:
                metrics = {
                    "cpu_usage": np.random.normal(30, 10),
                    "memory_usage": np.random.normal(50, 15),
                    "disk_usage": np.random.normal(40, 10),
                    "network_rx": np.random.normal(50, 20)
                }
            else:
                # 生成异常数据
                metrics = {
                    "cpu_usage": np.random.normal(90, 5),
                    "memory_usage": np.random.normal(95, 3),
                    "disk_usage": np.random.normal(85, 8),
                    "network_rx": np.random.normal(200, 50)
                }

            # 确保数值在合理范围内
            metrics = {k: max(0, min(100, v)) for k, v in metrics.items()}

            df = self.update_history(metrics)
            logging.info(f"生成数据点 {i+1}/{num_points}: {metrics}")
            time.sleep(0.1)  # 短暂延迟以模拟真实数据收集

        logging.info("测试数据生成完成，可以运行异常检测")


if __name__ == "__main__":
    # 确保目录存在
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

    detector = AIOpsAnomalyDetector()

    # 如果命令行参数包含 --generate-test-data，则生成测试数据
    if len(sys.argv) > 1 and sys.argv[1] == "--generate-test-data":
        detector.generate_test_data()
    else:
        # 运行异常检测
        detector.run()