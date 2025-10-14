#!/bin/bash

# 获取脚本所在目录，并找到项目根目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

HOST=$1
SSH_KEY="$PROJECT_ROOT/monitoring-key.pem"
TIMEOUT=180

echo "等待 $HOST 可 SSH..."
echo "使用SSH密钥: $SSH_KEY"

# 检查SSH密钥是否存在
if [ ! -f "$SSH_KEY" ]; then
    echo "❌ SSH密钥文件不存在: $SSH_KEY"
    exit 1
fi

for ((i=1;i<=$TIMEOUT;i++)); do
  if ssh -o StrictHostKeyChecking=no -i "$SSH_KEY" ec2-user@$HOST 'exit' 2>/dev/null; then
    echo "✅ SSH 连接成功"
    exit 0
  fi
  sleep 2
done
echo "❌ 超时：无法连接 $HOST"
exit 1
