#!/usr/bin/env python3
"""
AIOps 本地测试运行器
用于测试 metrics_exporter 和 anomaly_detector 的功能
"""

import subprocess
import sys
import time
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def start_metrics_exporter():
    """启动metrics exporter"""
    print("🚀 启动 Metrics Exporter...")
    process = subprocess.Popen([
        sys.executable,
        "metrics_exporter_local.py"
    ], cwd=Path(__file__).parent)
    return process

def run_anomaly_detection():
    """运行异常检测"""
    print("🔍 运行异常检测...")
    process = subprocess.run([
        sys.executable,
        "anomaly_detector_local.py"
    ], cwd=Path(__file__).parent, capture_output=True, text=True)
    return process

def generate_test_data():
    """生成测试数据"""
    print("📊 生成测试数据...")
    process = subprocess.run([
        sys.executable,
        "anomaly_detector_local.py",
        "--generate-test-data"
    ], cwd=Path(__file__).parent)
    return process.returncode == 0

def check_dependencies():
    """检查依赖是否安装"""
    print("🔍 检查依赖...")
    try:
        import psutil
        import requests
        import pandas
        import numpy
        import sklearn
        print("✅ 所有依赖已安装")
        return True
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("请运行: uv sync")
        return False

def test_metrics_endpoint():
    """测试metrics端点"""
    print("🧪 测试 Metrics 端点...")
    try:
        import requests
        response = requests.get("http://localhost:8000/metrics", timeout=5)
        if response.status_code == 200:
            print("✅ Metrics 端点正常")
            return True
        else:
            print(f"❌ Metrics 端点返回状态码: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 无法访问 Metrics 端点: {e}")
        return False

def test_health_endpoint():
    """测试健康检查端点"""
    print("🏥 测试健康检查端点...")
    try:
        import requests
        response = requests.get("http://localhost:8000/healthz", timeout=5)
        if response.status_code == 200 and response.text == "ok":
            print("✅ 健康检查端点正常")
            return True
        else:
            print(f"❌ 健康检查端点异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 无法访问健康检查端点: {e}")
        return False

def run_full_test():
    """运行完整测试"""
    print("🧪 开始完整测试流程...")

    # 1. 检查依赖
    if not check_dependencies():
        return False

    # 2. 启动 metrics exporter
    exporter_process = start_metrics_exporter()

    try:
        # 3. 等待服务启动
        time.sleep(3)

        # 4. 测试端点
        metrics_ok = test_metrics_endpoint()
        health_ok = test_health_endpoint()

        if not (metrics_ok and health_ok):
            return False

        # 5. 生成测试数据
        if not generate_test_data():
            print("❌ 测试数据生成失败")
            return False

        # 6. 运行异常检测
        result = run_anomaly_detection()
        if result.returncode == 0:
            print("✅ 异常检测运行成功")
            print("📋 输出:")
            print(result.stdout)
        else:
            print("❌ 异常检测运行失败")
            print("❌ 错误输出:")
            print(result.stderr)
            return False

        # 7. 显示结果文件
        print("\n📁 生成的文件:")
        for file_name in ["anomaly_score.txt", "metrics_history.csv", "aiops.log"]:
            file_path = Path(__file__).parent / file_name
            if file_path.exists():
                print(f"  📄 {file_name}")
                if file_name == "anomaly_score.txt":
                    with open(file_path, 'r') as f:
                        score = f.read().strip()
                        print(f"     当前异常分数: {score}")

        print("\n🎉 所有测试完成!")
        print("\n📊 访问地址:")
        print("  📈 Metrics: http://localhost:8000/metrics")
        print("  🏥 Health: http://localhost:8000/healthz")

        return True

    finally:
        # 8. 清理
        print("\n🧹 清理进程...")
        exporter_process.terminate()
        try:
            exporter_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            exporter_process.kill()

def show_help():
    """显示帮助信息"""
    print("AIOps 本地测试工具")
    print("\n用法:")
    print("  python test_runner.py [命令]")
    print("\n命令:")
    print("  test        运行完整测试")
    print("  check       检查依赖")
    print("  generate    生成测试数据")
    print("  detect      运行异常检测")
    print("  help        显示帮助")
    print("\n示例:")
    print("  python test_runner.py test")

def main():
    """主函数"""
    if len(sys.argv) < 2:
        run_full_test()
        return

    command = sys.argv[1]

    if command == "test":
        run_full_test()
    elif command == "check":
        check_dependencies()
    elif command == "generate":
        if check_dependencies():
            generate_test_data()
    elif command == "detect":
        if check_dependencies():
            run_anomaly_detection()
    elif command == "help":
        show_help()
    else:
        print(f"未知命令: {command}")
        show_help()

if __name__ == "__main__":
    main()