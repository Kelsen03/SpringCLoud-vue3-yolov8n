#!/bin/bash
# ============================================================
# 连锁超市管理系统 — Docker 一键构建部署脚本
# 用法: bash build.sh
# ============================================================
set -e

echo "=== Step 1: 安装 Maven（如未安装）==="
if ! command -v mvn &> /dev/null; then
    sudo dnf install -y maven
fi

echo ""
echo "=== Step 2: 创建 Swap（如内存不足）==="
if [ ! -f /swapfile ]; then
    sudo fallocate -l 2G /swapfile
    sudo chmod 600 /swapfile
    sudo mkswap /swapfile
    sudo swapon /swapfile
    echo "Swap 创建完成"
else
    echo "Swap 已存在，跳过"
fi

echo ""
echo "=== Step 3: 停掉旧服务释放内存 ==="
pkill -f 'java -jar' 2>/dev/null || true
systemctl stop nginx 2>/dev/null || true
pkill -f ai_server.py 2>/dev/null || true
echo "旧服务已停止"

echo ""
echo "=== Step 4: Maven 编译所有微服务（一次性编译，约 2-5 分钟）==="
cd "$(dirname "$0")"
mvn clean package -DskipTests -q

echo ""
echo "=== Step 5: Docker Compose 构建镜像 ==="
docker compose build

echo ""
echo "=== Step 6: 启动所有容器 ==="
docker compose up -d

echo ""
echo "=== 部署完成！==="
echo "查看状态: docker compose ps"
echo "查看日志: docker compose logs -f"
echo "前端:     http://$(curl -s ifconfig.me 2>/dev/null || echo 'YOUR_IP')"
echo "Nacos:    http://$(curl -s ifconfig.me 2>/dev/null || echo 'YOUR_IP'):8848/nacos"
