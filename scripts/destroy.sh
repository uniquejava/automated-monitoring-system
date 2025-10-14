#!/bin/bash
set -e

# 获取脚本所在目录，并找到项目根目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

SSH_KEY=${SSH_KEY:-"$PROJECT_ROOT/monitoring-key.pem"}
AWS_REGION=${AWS_REGION:-ap-northeast-1}
KEY_NAME=${KEY_NAME:-monitoring-key}

echo "🧹 Starting cleanup of monitoring environment resources..."
echo "📍 项目根目录: $PROJECT_ROOT"

# Check if infra directory exists
INFRA_DIR="$PROJECT_ROOT/infra"
if [ ! -d "$INFRA_DIR" ]; then
    echo "❌ infra directory does not exist: $INFRA_DIR"
    exit 1
fi

cd "$INFRA_DIR"

# Check if Terraform state exists
if [ ! -f "terraform.tfstate" ]; then
    echo "⚠️  No Terraform state file found, possibly no deployed resources"
    echo "🗑️  Deleting local SSH key files..."
    rm -f "$SSH_KEY" "${SSH_KEY}.pub"
    echo "✅ Cleanup completed"
    exit 0
fi

# 1. Get resource information for confirmation
echo "📋 Checking currently deployed resources..."
if command -v terraform >/dev/null 2>&1; then
    terraform show -json 2>/dev/null | jq -r '.values.root_module.resources[]? | "\(.type): \(.name)"' 2>/dev/null || echo "Unable to parse resource details"
else
    echo "❌ Terraform not installed, please install Terraform first"
    exit 1
fi

# 2. Confirm destroy operation
echo ""
read -p "⚠️  Are you sure you want to destroy all AWS resources? This will delete EC2 instances, VPCs and all infrastructure. (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Operation cancelled by user"
    exit 1
fi

# 3. Execute Terraform destroy
echo "🔥 Destroying AWS infrastructure..."
terraform destroy -auto-approve

# 4. Clean up SSH key pair in AWS (optional)
echo ""
read -p "🔑 Delete SSH key pair '$KEY_NAME' from AWS? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🗑️  Deleting AWS SSH key pair..."
    if aws ec2 delete-key-pair --key-name "$KEY_NAME" --region "$AWS_REGION" 2>/dev/null; then
        echo "✅ AWS SSH key pair deleted"
    else
        echo "⚠️  SSH key pair deletion failed or does not exist"
    fi
fi

# 5. Delete local key files
echo "🗑️  Deleting local SSH key files..."
rm -f "$SSH_KEY" "${SSH_KEY}.pub"

# 6. Clean up temporary files
echo "🗑️  Cleaning up temporary files..."
rm -f "$PROJECT_ROOT/ansible/temp_inventory"

echo ""
echo "✅ All resources cleanup completed!"
echo "📊 Monitoring environment has been completely destroyed"