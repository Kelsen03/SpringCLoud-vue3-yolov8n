#!/bin/bash
# ============================================
# DuckDNS DDNS 自动更新脚本
# 每次服务器开机或 IP 变化时自动更新 DNS 记录
# ============================================
#
# 使用前请修改下面两个变量：
#   DOMAIN  — 你在 duckdns.org 注册的子域名
#   TOKEN   — 你的 duckdns token（在 duckdns.org 页面可见）
#
# 配置方式（二选一）：
#   1. crontab 定时执行：  */5 * * * * /bin/bash /opt/duckdns-update.sh
#   2. 手动执行：         bash /opt/duckdns-update.sh
# ============================================

DOMAIN="mylsshop"
TOKEN="7fb2bf5d-e813-4a0d-a358-097203ba93d7"

RESPONSE=$(curl -s "https://www.duckdns.org/update?domains=${DOMAIN}&token=${TOKEN}&ip=")

if [ "$RESPONSE" = "OK" ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] DuckDNS updated successfully: ${DOMAIN}.duckdns.org"
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] DuckDNS update failed: ${RESPONSE}"
fi
