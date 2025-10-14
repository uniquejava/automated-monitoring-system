#!/bin/bash
set -e

# 获取脚本所在目录，并找到项目根目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

SSH_KEY=${SSH_KEY:-"$PROJECT_ROOT/monitoring-key.pem"}
PLAYBOOK=${PLAYBOOK:-"$PROJECT_ROOT/ansible/playbook.yml"}

echo "🚀 开始部署监控环境..."
echo "📍 项目根目录: $PROJECT_ROOT"

# 检查SSH密钥文件是否存在
if [ ! -f "$SSH_KEY" ]; then
    echo "❌ SSH密钥文件不存在: $SSH_KEY"
    echo "请先生成SSH密钥对: ssh-keygen -t rsa -b 4096 -f $SSH_KEY -N \"\""
    exit 1
fi

chmod 600 "$SSH_KEY"

# 1. Terraform
echo "📦 创建 AWS 基础设施..."
cd "$PROJECT_ROOT/infra"
terraform init -input=false
terraform apply -auto-approve
INSTANCE_IP=$(terraform output -raw public_ip)

# 2. Wait for SSH
echo "⏳ 等待实例启动..."
"$SCRIPT_DIR/wait-for-ssh.sh" "$INSTANCE_IP"

# 3. Ansible
echo "⚙️ 配置监控服务..."
INVENTORY_FILE=$(mktemp)
cat > "$INVENTORY_FILE" <<EOF
[monitoring_servers]
$INSTANCE_IP ansible_user=ec2-user ansible_ssh_private_key_file=$SSH_KEY
EOF

ANSIBLE_HOST_KEY_CHECKING=False ansible-playbook -i "$INVENTORY_FILE" "$PLAYBOOK"

# 4. 清理
rm -f "$INVENTORY_FILE"

echo "✅ 部署完成!"
echo "📊 Grafana: http://$INSTANCE_IP:3000"
echo "🔍 Prometheus: http://$INSTANCE_IP:9090"
