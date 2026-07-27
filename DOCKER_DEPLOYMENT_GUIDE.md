# 超级市场微服务系统 Docker 化部署 — 完整技术复盘

> 从毕业设计项目 `java -jar` 手动部署 → Docker Compose 一键编排 11 容器  
> 服务器: 阿里云 2C2G / Alibaba Cloud Linux 3 / 公网 IP: 8.148.221.19  
> 代码仓库: https://github.com/Kelsen03/SpringCLoud-vue3-yolov8n

---

## 目录

1. [项目架构概览](#1-项目架构概览)
2. [源码适配改造](#2-源码适配改造)
3. [Docker 配置文件详解](#3-docker-配置文件详解)
4. [Docker Desktop 安装与代理配置](#4-docker-desktop-安装与代理配置)
5. [镜像离线分发](#5-镜像离线分发)
6. [服务器部署全流程](#6-服务器部署全流程)
7. [数据迁移](#7-数据迁移)
8. [10 大核心问题与解决方案](#8-10-大核心问题与解决方案)
9. [最终可用状态](#9-最终可用状态)
10. [踩坑排行榜](#10-踩坑排行榜)
11. [经验清单](#11-经验清单)
12. [Docker 基础速查](#12-docker-基础速查)

---

## 1. 项目架构概览

### 1.1 技术栈

| 层面 | 技术 |
|------|------|
| 微服务框架 | SpringBoot 2.7.18 + SpringCloud 2021.0.8 + SpringCloud Alibaba 2021.0.5.0 |
| 注册中心 | Nacos 2.2.3（仅服务发现，无配置中心） |
| 数据库 | MySQL 8.0.36（4 个库：auth / product / inventory / order） |
| 缓存 | Redis 7.2 |
| 前端 | Vue3 + Vite + Element Plus |
| AI 服务 | Python Flask + YOLOv8（ONNX Runtime 推理） |
| 编排 | Docker Compose v2 |

### 1.2 11 个容器清单

| 容器名 | 镜像 | 端口 | 内存限制 | 说明 |
|--------|------|------|----------|------|
| supermarket-mysql | mysql:8.0.36 | 3306 | 350M | 4 个数据库 |
| supermarket-redis | redis:7.2-alpine | 6379 | 150M | product 服务缓存 |
| supermarket-nacos | nacos/nacos-server:v2.2.3 | 8848/9848 | 300M | 服务注册中心 |
| supermarket-ai | 自构建（Python ONNX） | 5000 | 600M | YOLOv8 商品识别 |
| supermarket-gateway | 自构建（Java） | 8000 | 256M | SpringCloud Gateway + JWT |
| supermarket-auth | 自构建（Java） | 9000 | 256M | 登录注册 + 用户管理 |
| supermarket-product | 自构建（Java） | 9001 | 256M | 商品 CRUD + Redis 缓存 |
| supermarket-inventory | 自构建（Java） | 9002 | 256M | 库存/调拨/补货 |
| supermarket-order | 自构建（Java） | 9003 | 256M | 订单/收银/Feign |
| supermarket-analysis | 自构建（Java） | 9004 | 256M | 跨库分析 + 定时任务 |
| supermarket-nginx | 自构建（Vue+nginx） | 80/8888 | 100M | 前端 + 反向代理 |

### 1.3 网络拓扑

```
浏览器 (http://8.148.221.19:8888)
    │
    ▼
┌─────────────────────┐
│  Nginx :80 :8888    │  ← 自构建（npm build + nginx）
│  /api/* → gateway   │
│  /ai/*  → ai:5000   │
│  /*     → index.html │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Gateway :8000      │  ← JWT 全局过滤器
│  路由到下游服务      │     /auth/login, /auth/register 放行
└──────┬──────────────┘
       │
  ┌────┼────┬────────┬──────────┐
  ▼    ▼    ▼        ▼          ▼
 Auth Product Inventory Order  Analysis
:9000 :9001  :9002    :9003     :9004
  │    │      │        │          │
  │    │      │        ├─Feign──→│
  │    │      │        │          │
  └────┴──────┴────────┴──────────┘
       │        │        │
       ▼        ▼        ▼
  ┌─────────────────────────┐
  │  MySQL :3306            │
  │  supermarket_auth       │
  │  supermarket_product    │
  │  supermarket_inventory  │
  │  supermarket_order      │
  └─────────────────────────┘
       │
       ▼
  ┌──────────────┐
  │  Redis :6379 │  ← 仅 product 用
  └──────────────┘
       │
       ▼
  ┌──────────────────────┐
  │  AI Service :5000    │  ← Python Flask + ONNX
  │  /health             │
  │  /api/detect         │
  └──────────────────────┘
```

---

## 2. 源码适配改造

### 2.1 改动清单

| # | 文件 | 改动内容 | 原因 |
|---|------|----------|------|
| 1 | 6 个 `pom.xml` | 添加 `spring-boot-starter-actuator` | Docker HEALTHCHECK 需要 `/actuator/health` |
| 2 | `pom.xml`（根） | maven-compiler-plugin 3.13.0 → 3.10.1 | 服务器 Maven 3.6.2 不兼容 3.13.0 |
| 3 | 6 个 `application.yml` | `localhost:8848` → `${NACOS_SERVER_ADDR:localhost:8848}` | 容器间用 Docker 网络通信 |
| 4 | 6 个 `application.yml` | `localhost:3306` → `${MYSQL_HOST:localhost}:${MYSQL_PORT:3306}` | 同上 |
| 5 | product `application.yml` | `localhost:6379` → `${REDIS_HOST:localhost}:${REDIS_PORT:6379}` | 同上 |
| 6 | product `application.yml` | 添加 `ai.service.url: ${AI_SERVICE_URL:http://localhost:5000}` | AI 服务地址可配置 |
| 7 | `ProductController.java:27-28` | 添加 `@Value("${ai.service.url}") private String aiServiceUrl;` | 注入 AI 地址 |
| 8 | `ProductController.java:44` | `"http://localhost:5000/api/detect"` → `aiServiceUrl + "/api/detect"` | 使用注入变量 |
| 9 | `product.js:44` | `http://8.148.236.60:5000/api/detect` → `/ai/detect` | 走 Nginx 反向代理 |
| 10 | `vite.config.js` | 添加 `/ai` 代理到 `8.148.236.60:5000` | 本地开发也能调 AI |
| 11 | 3 个 `schema.sql` | `CREATE TABLE` → `CREATE TABLE IF NOT EXISTS` | 防止重启丢数据 |
| 12 | `product schema.sql` | 删除 `DROP TABLE IF EXISTS product;` | 防止重启丢数据 |
| 13 | `AuthFilter.java` | 添加 `token.startsWith("Bearer ")` 判断 | 修复 JWT 鉴权 |
| 14 | `SecurityConfig.java` | 添加 `"/actuator/**"` 到 permitAll | 修复健康检查 403 |
| 15 | `request.js` | `timeout: 10000` → `timeout: 30000` | 2C2G 响应慢 |
| 16 | `Login.vue` | 退出登录跳回时跳过开幕动画 | 修复退出白屏 |
| 17 | `data.sql`（auth） | 明文 `123456` → BCrypt 哈希 | 密码正确比对 |

### 2.2 环境变量化模板

所有微服务 `application.yml` 统一模板：

```yaml
server:
  port: ${SERVER_PORT:9001}

spring:
  application:
    name: product-service
  cloud:
    nacos:
      discovery:
        server-addr: ${NACOS_SERVER_ADDR:localhost:8848}
  datasource:
    url: jdbc:mysql://${MYSQL_HOST:localhost}:${MYSQL_PORT:3306}/${MYSQL_DATABASE:supermarket_product}?...
    username: ${MYSQL_USERNAME:root}
    password: ${MYSQL_PASSWORD:123456}
  redis:
    host: ${REDIS_HOST:localhost}
    port: ${REDIS_PORT:6379}
  sql:
    init:
      mode: ${SQL_INIT_MODE:always}   # 生产改 never

management:
  endpoints:
    web:
      exposure:
        include: health,info
```

> **设计理由**: 默认值用 `localhost`，这样 IDEA 本地开发也能直接跑；Docker 环境通过 `docker-compose.yml` 的 `environment` 覆盖为容器名。

---

## 3. Docker 配置文件详解

### 3.1 目录结构

```
项目根目录/
├── docker-compose.yml               # 11 容器编排（核心文件）
├── .env                             # MYSQL_ROOT_PASSWORD=123456
├── .gitignore                       # 排除 .env、target/
├── build.sh                         # 一键构建部署脚本
├── README.md                        # 部署文档
├── proxy_bridge.py                  # Windows 用 SOCKS5→HTTP 代理桥
│
├── docker/
│   ├── mysql/
│   │   ├── init/01-create-databases.sql   # 创建 4 个数据库
│   │   └── conf/my.cnf                    # InnoDB 128M buffer pool
│   ├── redis/
│   │   └── redis.conf                    # maxmemory 128M
│   └── nginx/
│       └── conf.d/default.conf           # 前端 + 反向代理
│
├── supermarket-gateway/
│   ├── Dockerfile
│   └── src/main/resources/application.yml
│
├── supermarket-auth/
│   ├── Dockerfile
│   ├── src/main/resources/application.yml
│   ├── src/main/resources/schema.sql     # 建表
│   ├── src/main/resources/data.sql       # 初始用户（BCrypt）
│   └── src/main/java/.../config/
│       ├── SecurityConfig.java           # Spring Security 配置
│       └── DataInitializer.java          # CommandLineRunner 种子数据
│
├── supermarket-product/
│   ├── Dockerfile
│   └── src/main/resources/
│       ├── application.yml
│       ├── schema.sql
│       └── data.sql                      # 20 条初始商品
│
├── supermarket-inventory/
│   ├── Dockerfile
│   └── src/main/resources/
│       ├── application.yml
│       ├── schema.sql
│       └── SchemaMigration.java          # @PostConstruct 跨库写
│
├── supermarket-order/
│   ├── Dockerfile
│   └── src/main/resources/
│       ├── application.yml
│       └── schema.sql
│
├── supermarket-analysis/
│   ├── Dockerfile
│   └── src/main/resources/application.yml
│
├── supermarket-ui/
│   ├── Dockerfile                        # 多阶段: npm build → nginx
│   └── nginx.conf
│
└── ai-service/
    ├── Dockerfile
    ├── app.py                            # Flask + ONNX Runtime
    ├── requirements.txt                  # flask, onnxruntime, opencv, numpy
    ├── best.onnx                         # 12MB ONNX YOLOv8 权重
    └── best.pt                           # 6MB PyTorch 权重（备用）
```

### 3.2 Java 微服务 Dockerfile（6 个一致）

```dockerfile
FROM eclipse-temurin:8-jre-alpine
# 注意: openjdk:8-jre-alpine 已被 Docker 下架，改用 eclipse-temurin

RUN apk add --no-cache tzdata curl && \
    cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    echo "Asia/Shanghai" > /etc/timezone

RUN addgroup -g 1000 app && adduser -u 1000 -G app -D appuser

WORKDIR /app
COPY target/*.jar app.jar

HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:<服务端口>/actuator/health || exit 1

USER appuser
ENTRYPOINT ["sh", "-c", "java -jar -XX:+UseG1GC -XX:MaxRAMPercentage=75.0 app.jar"]
```

> **为什么不用多阶段构建**: 服务器有 Maven，用 `build.sh` 先编译再构建镜像更快。多阶段构建需要每次从头拉 Maven 依赖。

### 3.3 前端 Dockerfile（多阶段）

```dockerfile
# 阶段 1: Node 构建 Vue
FROM node:20-alpine AS builder
WORKDIR /build
COPY package*.json ./
RUN npm ci --registry=https://registry.npmmirror.com
COPY . .
RUN npm run build

# 阶段 2: Nginx 运行
FROM nginx:1.25-alpine
COPY --from=builder /build/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### 3.4 AI 服务 Dockerfile

```dockerfile
FROM python:3.10-slim

# 使用阿里云 Debian 镜像源（否则服务器 apt 超时）
RUN sed -i 's|http://deb.debian.org|http://mirrors.aliyun.com|g' /etc/apt/sources.list.d/debian.sources && \
    apt-get update && apt-get install -y --no-install-recommends \
    libgl1 libglib2.0-0 libgomp1 curl \
    && rm -rf /var/lib/apt/lists/*

# 阿里云 pip 镜像源
RUN pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY best.onnx .

EXPOSE 5000
HEALTHCHECK --interval=15s --timeout=5s --start-period=30s --retries=5 \
    CMD curl -f http://localhost:5000/health || exit 1

CMD ["python", "app.py"]
```

### 3.5 docker-compose.yml 核心配置

```yaml
networks:
  supermarket-net:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16

services:
  mysql:
    image: mysql:8.0.36
    environment:
      MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD:-123456}
      TZ: Asia/Shanghai
    volumes:
      - mysql-data:/var/lib/mysql
      - ./docker/mysql/init:/docker-entrypoint-initdb.d:ro
      - ./docker/mysql/conf/my.cnf:/etc/mysql/conf.d/my.cnf:ro
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost", "-u", "root", "-p${MYSQL_ROOT_PASSWORD:-123456}"]
      interval: 10s
      retries: 10

  nacos:
    image: nacos/nacos-server:v2.2.3
    environment:
      MODE: standalone
      PREFER_HOST_MODE: hostname
      NACOS_AUTH_ENABLE: "false"
      JVM_XMS: 256m
      JVM_XMX: 256m
      JVM_XMN: 128m

  supermarket-product:
    build:
      context: ./supermarket-product      # ★ context 是子目录
      dockerfile: Dockerfile
    environment:
      - NACOS_SERVER_ADDR=nacos:8848       # ★ 容器名通信
      - MYSQL_HOST=mysql
      - REDIS_HOST=redis
      - AI_SERVICE_URL=http://ai-service:5000
      - SQL_INIT_MODE=never               # ★ 生产不要 always
    depends_on:
      mysql:
        condition: service_healthy         # ★ 等 MySQL 就绪
      nacos:
        condition: service_healthy
    deploy:
      resources:
        limits:
          memory: 256M
```

### 3.6 Nginx 反向代理配置

```nginx
server {
    listen 80;

    # 前端 SPA（Vue Router history 模式）
    location / {
        root /usr/share/nginx/html;
        try_files $uri $uri/ /index.html;
    }

    # API 反向代理 → Gateway（剥离 /api/ 前缀）
    location /api/ {
        proxy_pass http://supermarket-gateway:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_connect_timeout 30s;
        proxy_read_timeout 60s;
    }

    # AI 识别反向代理 → Flask（映射 /ai/ → /api/）
    location /ai/ {
        proxy_pass http://ai-service:5000/api/;
        proxy_set_header Host $host;
        client_max_body_size 10m;
    }
}
```

### 3.7 build.sh 一键部署脚本

```bash
#!/bin/bash
set -e

# Step 1: 安装 Maven（如未安装）
if ! command -v mvn &> /dev/null; then
    sudo dnf install -y maven
fi

# Step 2: 创建 Swap（内存不足时）
if [ ! -f /swapfile ]; then
    sudo fallocate -l 2G /swapfile
    sudo chmod 600 /swapfile
    sudo mkswap /swapfile
    sudo swapon /swapfile
fi

# Step 3: 停掉旧服务释放内存
pkill -f 'java -jar' 2>/dev/null || true
systemctl stop nginx 2>/dev/null || true
pkill -f ai_server.py 2>/dev/null || true

# Step 4: Maven 编译所有微服务
cd "$(dirname "$0")"
mvn clean package -DskipTests -q

# Step 5: Docker Compose 构建镜像
docker compose build

# Step 6: 启动所有容器
docker compose up -d
```

---

## 4. Docker Desktop 安装与代理配置

### 4.1 Windows 安装 Docker Desktop

1. **确认架构**: `uname -m` → `x86_64` → 选 **AMD64** 版本（不是 ARM）
2. 官网下载慢 → 腾讯云镜像 `https://mirrors.cloud.tencent.com/docker-ce/win/stable/`（可能失效）→ 百度网盘
3. 安装时勾选 **Use WSL 2 instead of Hyper-V**
4. 如果 WSL 没装：管理员 PowerShell `wsl --install`
   - GitHub 被墙导致 Ubuntu 下载失败 → 不用管，Docker Desktop 自带 WSL 发行版
   - `wsl --set-default-version 2`

### 4.2 Docker Desktop 国内镜像源配置

Docker Desktop → Settings → Docker Engine:

```json
{
  "registry-mirrors": [
    "https://docker.1ms.run",
    "https://docker.xuanyuan.me",
    "https://docker.m.daocloud.io"
  ]
}
```

> **实际效果**: Windows 上有时代理源可以通（429 限流也常见），服务器端全部超时。最终靠 VPN 直连 Docker Hub。

### 4.3 VPN 代理让 Docker Desktop 走代理

**Docker Desktop 不跟随系统 VPN 设置!** 需要单独配置。

用户用的 **JAMJAMS** VPN（SOCKS5: 127.0.0.1:1080），但 Docker Desktop 只支持 HTTP 代理。

**解决方案: 写一个 Python SOCKS5→HTTP 代理桥** (`proxy_bridge.py`):

```python
"""纯标准库，不需 pip install 任何包"""
import socket, threading, struct

def socks5_connect(host, port):
    s = socket.socket()
    s.connect(("127.0.0.1", 1080))
    s.sendall(b"\x05\x01\x00")           # SOCKS5 握手
    s.recv(2)
    req = b"\x05\x01\x00\x03" + bytes([len(host)]) + host.encode() + struct.pack("!H", port)
    s.sendall(req)
    s.recv(10)
    return s

# HTTP 代理监听 127.0.0.1:7890，转发到 SOCKS5 127.0.0.1:1080
server = socket.socket()
server.bind(("127.0.0.1", 7890))
server.listen(50)
# ... 处理 HTTP CONNECT 和普通请求
```

运行 `python proxy_bridge.py` 保持窗口开着。

Docker Desktop → Settings → Resources → Proxies:
- HTTP Proxy: `http://127.0.0.1:7890`
- HTTPS Proxy: `http://127.0.0.1:7890`

Apply & Restart。

### 4.4 Git 走 VPN 推代码

```powershell
# 配置 Git 走 SOCKS5 代理
git config --global http.proxy socks5://127.0.0.1:1080
git config --global https.proxy socks5://127.0.0.1:1080

# 推送（本地 master → 远程 main）
git push origin master:main

# 用完去掉（否则关 VPN 后 Git 全挂）
git config --global --unset http.proxy
git config --global --unset https.proxy
```

> **注意**: PowerShell 不支持 `&&`，用 `;` 分隔命令。

---

## 5. 镜像离线分发

这是整个项目最关键的技能点。中国大陆服务器无法访问 Docker Hub，必须走离线分发。

### 5.1 完整流程

```
┌─────────────────────────────────────────────────────────┐
│  Windows（开 VPN）                                       │
│                                                         │
│  1. docker pull 拉取 7 个基础镜像                         │
│  2. docker compose build 构建项目镜像                     │
│  3. docker save -o xxx.tar 导出                          │
│  4. 压缩（可选） → Workbench 上传                         │
└──────────────────────┬──────────────────────────────────┘
                       │  SCP / Workbench 上传
                       ▼
┌─────────────────────────────────────────────────────────┐
│  阿里云服务器                                            │
│                                                         │
│  5. docker load -i xxx.tar 加载                          │
│  6. docker compose up -d 启动                            │
└─────────────────────────────────────────────────────────┘
```

### 5.2 使用的 7 个基础镜像

| 镜像 | 大小 | 用途 |
|------|------|------|
| `eclipse-temurin:8-jre-alpine` | 220MB | 6 个 Java 微服务 |
| `python:3.10-slim` | 185MB | AI 识别服务 |
| `node:20-alpine` | 194MB | 前端构建阶段 |
| `nginx:1.25-alpine` | 75MB | 前端运行阶段 |
| `mysql:8.0.36` | 839MB | 数据库 |
| `redis:7.2-alpine` | 57MB | 缓存 |
| `nacos/nacos-server:v2.2.3` | 1.25GB | 注册中心 |

### 5.3 导出和加载命令

```bash
# Windows 导出（约 2.8GB）
docker save -o K:\Desktop\supermarket-base-images.tar \
  eclipse-temurin:8-jre-alpine python:3.10-slim node:20-alpine \
  nginx:1.25-alpine mysql:8.0.36 redis:7.2-alpine nacos/nacos-server:v2.2.3

# 上传方式
# - 阿里云 Workbench 网页端 → 文件上传（单文件上限 1.2GB）
# - 超 1.2GB 时用 PowerShell 分片：
$chunkSize = 1000MB
# ... [System.IO.File]::OpenRead + 循环写入 .part00 .part01 .part02

# 服务器合并 + 加载
cat xxx.tar.part* > xxx.tar
docker load -i xxx.tar

# AI 镜像单独构建
docker compose build ai-service
docker save -o ai-service-v3.tar supermarket-cloud-ai-service:latest
# 上传到服务器后:
docker load -i ai-service-v3.tar
docker tag supermarket-cloud-ai-service:latest springcloud-vue3-yolov8n-ai-service:latest
```

### 5.4 镜像命名规则

- **Windows 构建**: `docker.io/library/supermarket-cloud-ai-service:latest`
- **服务器 docker compose 构建**: `docker.io/library/springcloud-vue3-yolov8n-ai-service:latest`
- 上传后需要 `docker tag` 改名

---

## 6. 服务器部署全流程

### 6.1 初始环境准备

```bash
# 安装 Docker（阿里云 Linux）
sudo dnf config-manager --add-repo \
  https://mirrors.aliyun.com/docker-ce/linux/centos/docker-ce.repo
sudo dnf install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
sudo systemctl enable --now docker

# 安装 Git + Maven
sudo dnf install -y git maven

# 克隆代码
git clone https://github.com/Kelsen03/SpringCLoud-vue3-yolov8n.git
cd SpringCLoud-vue3-yolov8n
```

### 6.2 清理旧服务

```bash
# 1. 找出所有端口占用
ss -tlnp | grep -E '80|3306|6379|8848|9848|5000|8000|900[0-4]'

# 2. 停掉 systemd 服务
systemctl stop nacos nginx redis mysql mysqld \
  supermarket-ai supermarket-auth supermarket-product \
  supermarket-inventory supermarket-order supermarket-analysis \
  supermarket-gateway 2>/dev/null

# 3. 禁用开机自启
systemctl disable nacos nginx redis mysql mysqld \
  supermarket-ai supermarket-auth supermarket-product \
  supermarket-inventory supermarket-order supermarket-analysis \
  supermarket-gateway 2>/dev/null

# 4. 杀残留进程
pkill -9 -f nacos-server
pkill -9 -f 'java -jar'
pkill -9 -f redis-server
pkill -9 -f mysqld
pkill -9 nginx

# 5. 确认端口全释放
ss -tln | grep -E '80|3306|6379|8848|9848|5000|8000|900[0-4]'
```

### 6.3 部署

```bash
# 加载基础镜像
docker load -i /root/supermarket-base-images.tar

# 加载 AI 镜像
docker load -i /root/ai-service-v3.tar
docker tag supermarket-cloud-ai-service:latest springcloud-vue3-yolov8n-ai-service:latest

# 拉代码
cd ~/SpringCLoud-vue3-yolov8n
git pull origin main

# 一键部署
bash build.sh
```

### 6.4 常用运维命令

```bash
# 查看状态
docker compose ps

# 查看日志
docker compose logs -f supermarket-auth

# 重启单个服务
docker compose restart supermarket-auth

# 重建单个服务
docker compose build supermarket-auth
docker compose up -d supermarket-auth

# 全部停/启
docker compose down       # 停止 + 删除容器
docker compose up -d      # 启动

# 清理（危险！会删数据卷）
docker compose down -v
docker volume rm springcloud-vue3-yolov8n_mysql-data
```

---

## 7. 数据迁移

### 7.1 问题背景

- **旧数据库**: MariaDB 10.5，数据目录 `/var/lib/mysql`
- **新数据库**: Docker MySQL 8.0.36
- **数据量**: 4 个库，11 张表，共约 3000+ 条记录
- **困难**: `mysqldump --all-databases` 导出包含 MariaDB 特有系统表语法，MySQL 8.0 不兼容

### 7.2 迁移方法：逐表导出 INSERT 语句

**核心思路**: 用 mysql 命令行生成 INSERT 语句，用 `QUOTE()` 处理特殊字符。

**Step 1: 启动旧 MariaDB**

```bash
mysqld --user=root --datadir=/var/lib/mysql --port=3307 --skip-grant-tables &
sleep 10
ss -tln | grep 3307   # 确认监听
```

**Step 2: 确认数据量**

```bash
mysql -uroot -P3307 -N -e "
  SELECT 'product', COUNT(*) FROM supermarket_product.product
  UNION ALL SELECT 'inventory', COUNT(*) FROM supermarket_inventory.inventory
  UNION ALL SELECT 'order', COUNT(*) FROM supermarket_order.\`order\`;
"
```

**Step 3: 先从 Docker MySQL 建表（让 Java 服务自动建，或手动）**

```bash
# 确认表存在
docker exec supermarket-mysql mysql -uroot -p123456 -h127.0.0.1 -e "
  SHOW TABLES FROM supermarket_product;
  SHOW TABLES FROM supermarket_inventory;
  SHOW TABLES FROM supermarket_order;
"
```

**Step 4: 逐表导出并导入（推荐方法）**

```bash
# product 表（含特殊字符，用双引号包裹）
docker exec supermarket-mysql mysql -uroot -p123456 -h127.0.0.1 \
  -e "DELETE FROM supermarket_product.product;"

mysql -uroot -P3307 -N -B -e \
  "SELECT CONCAT('INSERT INTO product VALUES(',id,',\"',REPLACE(name,'\"','\\\\\"'),'\",',IFNULL(CONCAT('\"',barcode,'\"'),'NULL'),',\"',category,'\",',ROUND(price,2),',',ROUND(promo_price,2),',',is_local,',',IFNULL(store_id,'NULL'),');') \
   FROM supermarket_product.product;" \
  | docker exec -i supermarket-mysql mysql -uroot -p123456 -h127.0.0.1 supermarket_product

# order 表
mysql -uroot -P3307 -N -B -e \
  "SELECT CONCAT('INSERT INTO \`order\` VALUES(',id,',',QUOTE(order_no),',',IFNULL(store_id,'NULL'),',',IFNULL(member_id,'NULL'),',',total_price,',',IFNULL(points,0),',',QUOTE(create_time),',',QUOTE(IFNULL(cashier_account,'')),',',QUOTE(IFNULL(create_by,'')),');') \
   FROM supermarket_order.\`order\`;" \
  | docker exec -i supermarket-mysql mysql -uroot -p123456 -h127.0.0.1 supermarket_order

# order_item（Docker 表比 MariaDB 多 2 列，补 NULL）
mysql -uroot -P3307 -N -B -e \
  "SELECT CONCAT('INSERT INTO order_item VALUES(',id,',',order_id,',',IFNULL(product_id,'NULL'),',NULL,NULL,',price,',',quantity,');') \
   FROM supermarket_order.order_item;" \
  | docker exec -i supermarket-mysql mysql -uroot -p123456 -h127.0.0.1 supermarket_order

# shift_record
mysql -uroot -P3307 -N -B -e \
  "SELECT CONCAT('INSERT INTO shift_record VALUES(',id,',',store_id,',',QUOTE(cashier_username),',',QUOTE(shift_start),',',IFNULL(QUOTE(shift_end),'NULL'),',',opening_cash,',',IFNULL(closing_cash,'NULL'),',',system_cash,',',system_online,',',total_orders,',',QUOTE(status),',',IFNULL(QUOTE(remark),'NULL'),');') \
   FROM supermarket_order.shift_record;" \
  | docker exec -i supermarket-mysql mysql -uroot -p123456 -h127.0.0.1 supermarket_order
```

### 7.3 迁移结果

| 表 | MariaDB 原始 | Docker MySQL |
|---|---|---|
| product | 412 | 412 ✅ |
| inventory | 1068 | 1068 ✅ |
| order | 1383 | 1383 ✅ |
| order_item | 1307 | 1307 ✅ |
| stock_transfer | 37 | 37 ✅ |
| shift_record | 32 | 32 ✅ |
| member | 7 | 7 ✅ |
| product_sales | 68 | 68 ✅ |
| store | 2 | 2 ✅ |
| user | 4 | 5 ✅（含 docker 账户） |
| replenish_record | — | 手动建表 ✅ |

### 7.4 缺失表的手动创建

```bash
# replenish_record 表
docker exec supermarket-mysql mysql -uroot -p123456 -h127.0.0.1 supermarket_inventory -e "
CREATE TABLE IF NOT EXISTS replenish_record (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  product_id BIGINT NOT NULL,
  product_name VARCHAR(100),
  category VARCHAR(50),
  store_id BIGINT NOT NULL,
  count INT NOT NULL,
  production_date DATE,
  shelf_life_months INT DEFAULT 12,
  operator VARCHAR(50),
  create_time DATETIME DEFAULT CURRENT_TIMESTAMP
);"

# stock_transfer 表
docker exec supermarket-mysql mysql -uroot -p123456 -h127.0.0.1 supermarket_inventory -e "
CREATE TABLE IF NOT EXISTS stock_transfer (
  id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  product_id BIGINT, from_store BIGINT, to_store BIGINT,
  quantity INT, create_time DATETIME, status VARCHAR(20)
);"
```

### 7.5 SQL_INIT_MODE 问题

`spring.sql.init.mode=always` 会在每次 Java 服务启动时执行 `schema.sql` 和 `data.sql`，覆盖已迁移的数据。

**修复**: 把 docker-compose.yml 中所有 `SQL_INIT_MODE` 改为 `never`：

```bash
sed -i 's/SQL_INIT_MODE=always/SQL_INIT_MODE=never/g' docker-compose.yml
```

### 7.6 密码 BCrypt 问题

**根因**: `data.sql` 是明文 `INSERT INTO user VALUES(1,'admin','123456','HQ')`，但 `LoginController` 用 `BCryptPasswordEncoder.matches("123456", "123456")` 比对失败。

**但同时**: `DataInitializer.java`（CommandLineRunner）会用 `BCryptPasswordEncoder.encode("123456")` 创建 admin。然而 `data.sql` 先执行（`INSERT IGNORE`），所以明文先插入，`DataInitializer` 检查 admin 已存在就跳过。

**修复**: `data.sql` 的密码改为 BCrypt 哈希（在服务器上直接 UPDATE）：

```bash
# 复制 docker 用户的 BCrypt 哈希给 admin
docker exec supermarket-mysql mysql -uroot -p123456 -h127.0.0.1 -e "
  UPDATE supermarket_auth.user u1,
         (SELECT password FROM supermarket_auth.user WHERE username='docker') u2
  SET u1.password = u2.password
  WHERE u1.username = 'admin';
"
```

---

## 8. 10 大核心问题与解决方案

### 问题 1: Docker Hub 不可访问

**耗时**: ~4 小时

**链路**:
```
docker pull → registry-1.docker.io → GFW 封锁 → timeout
docker pull → docker.xuanyuan.me → 服务器 timeout
docker pull → docker.1ms.run → 服务器 timeout
docker pull → docker.m.daocloud.io → 服务器 timeout
Windows + VPN → docker.1ms.run → 429 Too Many Requests
Windows 无镜像源 + VPN → docker.io → 成功 ✅
```

**解决**: Windows Docker Desktop + VPN 拉取 → `docker save` 导出 tar → Workbench 上传 → 服务器 `docker load`

---

### 问题 2: Systemd 服务反复复活

**耗时**: ~2 小时

**现象**: 每次 `pkill` 后进程几秒就回来

**罪魁祸首**:
```bash
systemctl list-unit-files | grep -E "supermarket|nacos|redis|mysql|nginx"
# 发现 nginx.service enabled、redis.service enabled、mysql.service enabled
# 还有 7 个 supermarket-*.service（虽然 disabled，但 nacos.service 在复活）
```

**排查链路**:
```
端口被占 → ss -tlnp | grep <port> → 找 PID
  → ps -fp <pid> → 看是什么进程
    → systemctl list-unit-files | grep <name> → 找 service
      → crontab -l → 找定时任务
        → /etc/rc.local → 找开机脚本
```

**修复**:
```bash
systemctl stop nginx redis mysql mysqld nacos
systemctl disable nginx redis mysql mysqld nacos
systemctl disable supermarket-ai supermarket-auth supermarket-product \
  supermarket-inventory supermarket-order supermarket-analysis supermarket-gateway
pkill -9 -f nacos-server
pkill -9 -f mysqld
```

---

### 问题 3: 数据迁移

**耗时**: ~2 小时（反复尝试多种方案）

**失败方案**:
1. `mysqldump --all-databases` → MariaDB 系统表语法不兼容 MySQL 8.0
2. `mysqldump --compatible=mysql40` → 同样问题
3. `mysqldump <db> <table>` → 语法错误
4. 用 `mysql -e "SHOW CREATE TABLE" | docker exec` → 管道格式问题

**成功方案**: 逐表用 `SELECT CONCAT('INSERT INTO ...')` 生成并管道导入

**关键教训**:
- MariaDB 的 mysqldump 在 `--skip-grant-tables` 模式下不稳定
- `mysqldump` 需要 TCP 连接密码认证，`--skip-grant-tables` 只跳过 socket 认证
- Docker MySQL 导入通过 `docker exec -i` + `-h127.0.0.1`（避免 Unix socket 路径）

---

### 问题 4: Spring Security 403 → 健康检查 unhealthy

**耗时**: ~1 小时

**故障链路**:
```
Docker HEALTHCHECK → curl :9000/actuator/health
  → Spring Security → /actuator/** 需要认证
    → 返回 403 Forbidden
      → Docker 标记 unhealthy
        → Nacos 实例状态 unhealthy
          → Gateway 不路由请求
            → Nginx → Gateway → 503 Service Unavailable
              → 前端 502 Bad Gateway
```

**修复**: `SecurityConfig.java`
```java
.antMatchers("/auth/**", "/actuator/**", "/v3/api-docs/**", "/swagger-ui/**", "/doc.html").permitAll()
```

---

### 问题 5: AI 镜像过大

**原方案**: `ultralytics==8.2.0` → 依赖 `torch` + `nvidia-cublas` + `nvidia-cudnn` → **2.5GB**

**服务器**: 2C2G，磁盘只剩 3.3GB，构建失败。

**优化方案**: 用 `onnxruntime` 替代 `ultralytics+torch`

```python
# 改前（2.5GB）
from ultralytics import YOLO
model = YOLO("best.pt")
results = model(img, conf=0.10)

# 改后（300MB）
import onnxruntime as ort
session = ort.InferenceSession("best.onnx")
# 手动做 letterbox 预处理 + NMS 后处理
```

**Dockerfile 精简**:
```dockerfile
# requirements.txt — 5 个包就够了
flask==3.0.0
flask-cors==4.0.0
onnxruntime
opencv-python-headless==4.9.0.80
numpy==1.26.2
```

**效果**: 镜像从 2.5GB → 300MB，构建从 10 分钟 → 60 秒

**注意事项**:
- `libgl1-mesa-glx` 在 Debian Trixie 中改名 `libgl1`
- `best.onnx` 需要和 `best.pt` 同一次训练导出

---

### 问题 6: ONNX 类名顺序不匹配

**训练 data.yaml**:
```yaml
names: ['cocacola', 'fanta', 'lays', 'masterkong', 'mizone',
        'nongfu spring', 'pepsi', 'redbull', 'sprite', 'wanglaoji']
```

**我写的（错误）**:
```python
CLASS_NAMES_EN = ["cocacola", "pepsi", "sprite", "fanta", ...]
# 索引完全错位 → 芬达被当成百事、雪碧被当成芬达
```

**修复**: 严格对齐 `data.yaml` 的 `names` 顺序

---

### 问题 7: Docker Build Context 路径

**错误写法**:
```yaml
build:
  context: .                      # ← 项目根目录
  dockerfile: ai-service/Dockerfile
```
Dockerfile 中的 `COPY best.onnx .` 在项目根目录找 `best.onnx`，但文件在 `ai-service/best.onnx`。

**正确写法**:
```yaml
build:
  context: ./ai-service           # ← 子目录
  dockerfile: Dockerfile
```
现在 `COPY best.onnx .` 找到 `ai-service/best.onnx`。

> 6 个微服务和 AI 服务都有此问题，需全部修正。

---

### 问题 8: JWT Bearer 前缀

**Request header**: `Authorization: Bearer eyJh...`
**JwtUtil.parseToken()**: 直接调用 `Jwts.parser().parseClaimsJws(token)`
- jjwt 0.9 的 `parseClaimsJws` **不会**去掉 `"Bearer "` 前缀
- 导致鉴权失败 → 401

**修复** (`AuthFilter.java`):
```java
String token = exchange.getRequest().getHeaders().getFirst("Authorization");
if (token != null && token.startsWith("Bearer ")) {
    token = token.substring(7);   // 去掉 "Bearer "
}
JwtUtil.parseToken(token);
```

---

### 问题 9: 2C2G 性能瓶颈

**现象**:
- Java 服务启动 2-4 分钟（正常 30 秒）
- Nacos gRPC 连接超时：`Client not connected, current status:STARTING`
- Nacos JVM 128M 不够 → 频繁 FGC → 重启
- axios 10s 超时 → 连接中断
- 6 个 JVM + MySQL + Redis + Nacos 共抢 2GB RAM

**缓解措施**:
1. Nacos JVM: 128M → 256M（docker-compose.yml 环境变量）
2. axios timeout: 10s → 30s（`request.js`）
3. `SQL_INIT_MODE=never`（避免每次启动重建表）
4. 关掉 analysis（平时不用）：`docker compose stop supermarket-analysis`
5. 每个 Java 服务 JVM 用 `-XX:MaxRAMPercentage=75.0` 动态分配

---

### 问题 10: ISP 封锁 80 端口

**现象**: 手机流量 + Chrome 都打不开 `http://8.148.221.19`，但 PowerShell `curl` 返回 200。

**测试方法**:
```bash
# 服务器本地测试 OK
curl -s http://localhost/ | head -5       # ✅ HTML

# 手机流量测试 FAIL
http://8.148.221.19 → 无法连接 ❌

# 非 80 端口测试 OK
http://8.148.221.19:5000/health → {"status":"ok"} ✅
```

**原因**: 中国大陆 ISP 对没有 ICP 备案的 80/443 端口进行 HTTP 层阻断。

**解决**: Nginx 加端口映射 `8888:80`，从 `http://8.148.221.19:8888` 访问。

**浏览器 HSTS 问题**: 如果之前用 HTTPS 访问过该 IP，Chrome 会自动升级到 HTTPS → `ERR_SSL_PROTOCOL_ERROR`。需清除 HSTS：
```
chrome://net-internals/#hsts → Delete domain: 8.148.221.19
```

---

## 9. 最终可用状态

### 9.1 访问地址

| 服务 | URL | 说明 |
|------|-----|------|
| 前端 | `http://8.148.221.19:8888` | 80 端口 ISP 封锁 |
| Nacos | `http://8.148.221.19:8848/nacos` | 免密 |
| AI 服务 | `http://8.148.221.19:5000/health` | 健康检查 |

### 9.2 账号

| 用户名 | 密码 | 角色 | 说明 |
|--------|------|------|------|
| admin | 123456 | HQ | 总部管理员，全部权限 |
| docker | 123456 | STORE | Docker 化时创建（storeId=1） |
| store1 | 123456 | STORE | 一号门店店长 |
| lkq0120260325 | 123456 | CASHIER | 收银员 |

### 9.3 数据量

| 数据库 | 表 | 行数 |
|--------|-----|------|
| supermarket_auth | store | 2 |
| supermarket_auth | user | 5 |
| supermarket_product | product | 412 |
| supermarket_inventory | inventory | 1068 |
| supermarket_inventory | stock_transfer | 37 |
| supermarket_inventory | replenish_record | 0（新表） |
| supermarket_order | order | 1383 |
| supermarket_order | order_item | 1307 |
| supermarket_order | member | 7 |
| supermarket_order | product_sales | 68 |
| supermarket_order | shift_record | 32 |

### 9.4 容器健康状态

```bash
$ docker compose ps
NAME                    STATUS
supermarket-mysql       Up (healthy)
supermarket-redis       Up (healthy)
supermarket-nacos       Up (healthy)
supermarket-ai          Up (healthy)
supermarket-gateway     Up (healthy)
supermarket-auth        Up (healthy)
supermarket-product     Up (healthy)
supermarket-inventory   Up (healthy)
supermarket-order       Up (healthy)
supermarket-analysis    Up (healthy)
supermarket-nginx       Up
```

---

## 10. 踩坑排行榜

| 排名 | 问题 | 耗时 | 根因 | 一句话教训 |
|------|------|------|------|-----------|
| 1 | Docker Hub 拉镜像全部超时 | ~4h | GFW + 镜像源全挂 | 提前准备离线镜像 |
| 2 | 旧 systemd 服务反复复活占端口 | ~2h | 多个自启服务没禁干净 | `systemctl disable` + `pkill -9` |
| 3 | MariaDB 10.5 → MySQL 8.0 迁移 | ~2h | 跨版本不兼容，逐表生成 INSERT | 别用 `--all-databases` |
| 4 | Spring Security 403 → unhealthy 链路 | ~1h | 加 actuator 忘了放行 | Security 加 `permitAll("/actuator/**")` |
| 5 | Nacos gRPC 超时 → 服务启动循环 | ~1h | 2C2G 内存不够 | 低配下 Nacos JVM 至少要 256M |
| 6 | AI 镜像 2.5GB 构建失败 | ~30min | ultralytics 拖进全家桶 | ONNX Runtime 替代 PyTorch |
| 7 | ONNX 类名顺序全错 | ~30min | 没对照 data.yaml | 类名索引必须等于训练顺序 |
| 8 | ISP 80 端口封锁 | ~30min | 无 ICP 备案 | 加 8888 端口绕过 |
| 9 | JWT Bearer 前缀 | ~15min | jjwt 不会自动去前缀 | 手写 `substring(7)` |
| 10 | Docker context 路径 | ~15min | 不理解 COPY 相对于 context | context 设子目录 |
| 11 | Nginx AI 代理路径 /detect vs /api/detect | ~15min | Flask 路由前缀 | `proxy_pass` 加 `/api/` |
| 12 | 明文密码 vs BCrypt | ~15min | data.sql 和 DataInitializer 冲突 | data.sql 存 BCrypt 哈希 |
| 13 | 退出白屏 | ~10min | Login.vue 开幕动画二次挂载卡死 | sessionStorage 跳过 |
| 14 | Workbench 上传 1.2GB 限制 | ~10min | 平台限制 | 分片上传 |

---

## 11. 经验清单

### 部署前检查表

- [ ] 服务器 `docker pull hello-world` 能否成功？不能 → 准备离线镜像
- [ ] `ss -tln` 确认目标端口空闲（80/3306/6379/8848/9848/5000/8000/9000-9004）
- [ ] `systemctl list-unit-files | grep -E "nginx|redis|mysql|nacos|supermarket"` → 全部 disable
- [ ] `crontab -l` 确认没有复活任务
- [ ] 磁盘 `df -h` 至少 10GB 可用
- [ ] 阿里云安全组放行对应端口
- [ ] `mvn --version` → 3.6.x → pom.xml 的 maven-compiler-plugin ≤ 3.10.1

### 代码改造检查表

- [ ] 6 个 pom.xml 有 `spring-boot-starter-actuator`
- [ ] 所有 `application.yml` 的 `localhost` 改为 `${}` 占位符
- [ ] `management.endpoints.web.exposure.include: health,info`
- [ ] SecurityConfig 有 `.antMatchers("/actuator/**").permitAll()`
- [ ] AuthFilter 处理 `Bearer ` 前缀
- [ ] `schema.sql` 用 `CREATE TABLE IF NOT EXISTS`
- [ ] 前端 API 调用用相对路径（`/api/...`）
- [ ] `SQL_INIT_MODE=never`（生产环境）
- [ ] ONNX 类名映射对照 data.yaml

### 故障排查速查

```bash
# 端口被谁占？
ss -tlnp | grep <port>

# 容器为什么 unhealthy？
docker logs <container> --tail 20

# Nacos 注册了哪些服务？
curl -s "http://localhost:8848/nacos/v1/ns/service/list?pageNo=1&pageSize=10"

# 某个服务能否被访问？
docker exec supermarket-gateway curl -s http://<service>:<port>/actuator/health

# 数据库有数据吗？
docker exec supermarket-mysql mysql -uroot -p123456 -h127.0.0.1 -e "SELECT COUNT(*) FROM <db>.<table>;"

# API 是否通？
curl -sv http://localhost/api/<path> -H "Authorization: Bearer <token>" 2>&1
```

---

## 12. Docker 基础速查

### 12.1 镜像操作

```bash
# 拉取
docker pull eclipse-temurin:8-jre-alpine

# 查看本地
docker images

# 构建（从当前目录 Dockerfile）
docker build -t my-app:v1 .

# 导出
docker save -o my-images.tar image1 image2

# 加载
docker load -i my-images.tar

# 打标签
docker tag old-name:tag new-name:tag

# 删除
docker rmi image-id
docker image prune -a   # 删所有未用镜像
```

### 12.2 容器操作

```bash
# 查看运行中
docker ps
docker compose ps

# 启动/停止/重启
docker compose up -d              # 启动全部
docker compose up -d <service>    # 启动单个
docker compose stop <service>
docker compose restart <service>

# 进入容器
docker exec -it <container> sh

# 查看日志
docker logs <container> --tail 50 -f

# 删除所有停止的容器
docker container prune
```

### 12.3 磁盘清理

```bash
docker system prune -a   # 删所有未用镜像+容器+网络（危险！）
docker system df         # 看占用
df -h /                  # 服务器磁盘
```

### 12.4 数据卷

```bash
docker volume ls
docker volume rm <name>
docker compose down -v  # 删除所有卷（危险！）
```

### 12.5 网络

```bash
docker network ls
docker network inspect <name>   # 看 IP 分配
docker exec <container> ping <other-container>  # 容器间通不通
```

---

## 附录：项目文件变更汇总

```
新建:
  docker-compose.yml
  .env
  .gitignore
  build.sh
  README.md
  proxy_bridge.py                     # Windows 代理桥
  DOCKER_DEPLOYMENT_GUIDE.md         # 本文档
  docker/mysql/init/01-create-databases.sql
  docker/mysql/conf/my.cnf
  docker/redis/redis.conf
  docker/nginx/conf.d/default.conf
  supermarket-gateway/Dockerfile
  supermarket-auth/Dockerfile
  supermarket-product/Dockerfile
  supermarket-inventory/Dockerfile
  supermarket-order/Dockerfile
  supermarket-analysis/Dockerfile
  supermarket-ui/Dockerfile
  supermarket-ui/nginx.conf
  ai-service/Dockerfile
  ai-service/app.py                  # 重写（ONNX Runtime）
  ai-service/requirements.txt

修改:
  pom.xml（根）                       # maven-compiler-plugin 3.10.1
  6 个微服务 pom.xml                   # +actuator
  6 个微服务 application.yml           # 环境变量化
  supermarket-auth/src/.../SecurityConfig.java   # +/actuator/**
  supermarket-auth/src/.../data.sql              # 明文→BCrypt
  supermarket-gateway/src/.../AuthFilter.java    # +"Bearer " strip
  supermarket-product/src/.../ProductController.java  # +@Value aiServiceUrl
  supermarket-ui/src/utils/request.js            # timeout 30s
  supermarket-ui/src/views/Login.vue             # 退出跳过开幕动画
  supermarket-ui/src/api/product.js              # /ai/detect 相对路径
  supermarket-ui/vite.config.js                  # +/ai 代理
  supermarket-product/.../schema.sql             # DROP TABLE 删除
```

---

> **总结**: 从零开始把一个毕业设计的 SpringCloud 项目 Docker 化，踩遍了 Docker Hub 封锁、数据迁移、Security、JWT、Nacos gRPC、ONNX 推理、ISP 备案等几乎所有典型坑。最终 11 个容器稳定运行，前端正常访问，AI 准确识别，412 条商品 + 1383 条订单数据完整迁移。这段经历覆盖了企业级 Docker 部署的 80% 实战场景。
