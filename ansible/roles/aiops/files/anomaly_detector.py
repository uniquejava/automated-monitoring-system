#!/usr/bin/env python3
"""
AIOps 异常检测系统
结合统计与机器学习模型检测系统指标异常
"""

import json
import logging
import os
from datetime import datetime

import numpy as np
import pandas as pd
import requests
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

# === 配置 ===
PROM_URL = os.getenv("PROMETHEUS_URL", "http://localhost:9090")
HISTORY_FILE = "/opt/monitoring/aiops/metrics_history.csv"
ANOMALY_SCORE_FILE = "/opt/monitoring/aiops/anomaly_score.txt"
LOG_FILE = "/opt/monitoring/aiops/aiops.log"
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


class AIOpsAnomalyDetector:
    def __init__(self, prometheus_url=PROM_URL):
        self.prometheus_url = prometheus_url

    def query_metric(self, query):
        """查询 Prometheus 指标"""
        try:
            resp = requests.get(f"{self.prometheus_url}/api/v1/query", params={"query": query}, timeout=10)
            data = resp.json()
            return float(data["data"]["result"][0]["value"][1])
        except Exception as e:
            logging.warning(f"Prometheus 查询失败: {query} ({e})")
            return np.nan

    def collect_metrics(self):
        """收集基础指标"""
        metrics = {
            "cpu_usage": self.query_metric('100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)'),
            "memory_usage": self.query_metric('(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100'),
            "disk_usage": self.query_metric('(1 - (node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"})) * 100'),
            "network_rx": self.query_metric('rate(node_network_receive_bytes_total[5m])')
        }
        return metrics

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
            logging.info("系统运行正常")


if __name__ == "__main__":
    detector = AIOpsAnomalyDetector()
    detector.run()
