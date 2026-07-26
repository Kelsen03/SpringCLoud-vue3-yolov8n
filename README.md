# 连锁超市微服务管理系统

基于 SpringCloud + Vue3 + YOLOv8 的连锁超市管理平台，支持多门店、智能收银、库存调拨和数据分析。

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端框架 | Spring Boot 2.7.18 + Spring Cloud 2021.0.8 |
| 服务注册 | Nacos 2.x |
| 数据库 | MySQL 8.0 |
| 缓存 | Redis 7 |
| ORM | MyBatis-Plus 3.5 |
| 前端 | Vue 3 + Vite + Element Plus |
| AI 识别 | Python Flask + YOLOv8 (ultralytics) |
| 容器化 | Docker + Docker Compose |

## 项目结构

```
├── supermarket-gateway/     # Spring Cloud Gateway (8000)
├── supermarket-auth/        # 认证服务 (9000)
├── supermarket-product/     # 商品服务 (9001)
├── supermarket-inventory/   # 库存服务 (9002)
├── supermarket-order/       # 订单服务 (9003)
├── supermarket-analysis/    # 分析服务 (9004)
├── supermarket-ui/          # Vue3 前端
├── ai-service/              # Python AI 识别服务 (5000)
├── docker/                  # Docker 基础设施配置
├── sql/                     # 数据库脚本
├── scripts/                 # 工具脚本
├── docker-compose.yml       # 容器编排
└── pom.xml                  # Maven 父 POM
```

## 服务器部署（Docker Compose）

### 前置条件

- 服务器: 建议 4GB+ 内存（2GB 可勉强运行，见下文说明）
- 操作系统: Alibaba Cloud Linux 3 / CentOS 8+ / Ubuntu 20.04+
- 已安装: Docker Engine 24+ + Docker Compose Plugin

### 1. 安装 Docker

```bash
# Alibaba Cloud Linux 3 安装 Docker
sudo dnf install -y docker
sudo systemctl enable docker --now

# 安装 docker compose 插件
sudo dnf install -y docker-compose-plugin

# 验证
docker --version
docker compose version
```

### 2. 拉取项目并启动

```bash
# 克隆项目
git clone https://github.com/Kelsen03/SpringCLoud-vue3-yolov8n.git
cd SpringCLoud-vue3-yolov8n

# 构建所有镜像（首次约需 15-30 分钟，取决于网络）
docker compose build

# 启动所有服务
docker compose up -d

# 查看启动日志
docker compose logs -f

# 确认所有服务健康
docker compose ps
```

### 3. 访问

| 服务 | 地址 |
|------|------|
| 前端页面 | `http://<服务器IP>` |
| Nacos 控制台 | `http://<服务器IP>:8848/nacos` (用户/密码: nacos/nacos) |

### 4. 常用运维命令

```bash
# 查看所有服务状态
docker compose ps

# 查看某个服务日志
docker compose logs -f supermarket-gateway

# 重启单个服务
docker compose restart supermarket-product

# 停止所有服务
docker compose down

# 停止并清除数据（危险！）
docker compose down -v
```

## 2C2G 服务器部署注意事项

11 个容器在 2GB 内存上同时运行会比较吃紧。如果内存不足，可以：

**方案 A: 精简启动（仅核心服务）**
```bash
# 只启动基础设施 + 核心业务（约 1.2GB）
docker compose up -d mysql redis nacos supermarket-gateway supermarket-auth supermarket-product supermarket-order nginx
```

**方案 B: 创建 Linux Swap**
```bash
# 创建 2GB 虚拟内存作为缓冲
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile swap swap defaults 0 0' | sudo tee -a /etc/fstab
```

**方案 C: 卸载旧服务释放内存**
```bash
# 停止旧的 java -jar 进程
pkill -f 'java -jar'
# 停止旧的 Nginx
systemctl stop nginx
# 停止旧的 Python AI 服务
pkill -f ai_server.py
```

## 本地开发

```bash
# 后端：用 Maven 启动单个服务
cd supermarket-product
mvn spring-boot:run

# 前端：Vite 开发服务器
cd supermarket-ui
npm install
npm run dev
```

## 默认账号

| 角色 | 用户名 | 密码 |
|------|--------|------|
| 总部 HQ | admin | 123456 |
| 门店 | store01 | 123456 |
| 门店 | store02 | 123456 |
| 门店 | store03 | 123456 |
| 收银员 | cashier01 | 123456 |
