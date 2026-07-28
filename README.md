# 连锁超市微服务管理系统

基于 SpringCloud + Vue3 + YOLOv8 ONNX 的连锁超市管理平台，支持多门店、AI 视觉收银、库存调拨、数据分析和 Docker 容器化部署。

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端框架 | Spring Boot 2.7.18 + Spring Cloud 2021.0.8 |
| 服务注册 | Nacos 2.2.3（仅服务发现） |
| 数据库 | MySQL 8.0.36（4 库：auth / product / inventory / order） |
| 缓存 | Redis 7.2 |
| ORM | MyBatis-Plus 3.5 |
| 前端 | Vue 3 + Vite + Element Plus 2.13 |
| AI 识别 | Python Flask + YOLOv8 ONNX Runtime |
| 容器化 | Docker + Docker Compose（11 容器） |

## 项目结构

```
├── supermarket-gateway/       # Spring Cloud Gateway :8000 — JWT 鉴权 + 路由分发
├── supermarket-auth/          # 认证服务 :9000 — 登录/注册/BCrypt/用户管理
├── supermarket-product/       # 商品服务 :9001 — 商品 CRUD + Redis 缓存 + AI 调用
├── supermarket-inventory/     # 库存服务 :9002 — 库存/调拨/补货/跨库写
├── supermarket-order/         # 订单服务 :9003 — 订单/收银交班/Feign 调库存
├── supermarket-analysis/      # 分析服务 :9004 — 跨库只读分析/定时任务
├── supermarket-ui/            # Vue 3 前端 — 多阶段构建（npm build → nginx）
├── ai-service/                # Python Flask :5000 — ONNX Runtime 商品识别
├── docker/mysql/init/         # MySQL 初始化脚本（建库 + 权限修复）
├── docker/mysql/conf/         # MySQL 配置文件（128M buffer pool）
├── docker/redis/              # Redis 配置（128M maxmemory）
├── docker/nginx/conf.d/       # Nginx 反向代理（前端 + /api → Gateway + /ai → Flask）
├── sql/                       # 数据导入脚本（product_import.sql 等）
├── docker-compose.yml         # 11 容器编排
├── build.sh                   # 一键构建部署脚本
├── proxy_bridge.py            # Windows 用 SOCKS5→HTTP 代理桥（Docker Desktop 走 VPN）
└── pom.xml                    # Maven 父 POM
```

## 架构图

```
浏览器 (http://IP:8888)
       │
       ▼
┌─────────────────┐
│  Nginx :80 :8888  │  前端 SPA + 反向代理
│  /api/* → gateway │  /ai/* → ai-service
│  /*     → index   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Gateway :8000    │  JWT 全局过滤器 + 路由
│  路由到 5 个服务   │
└──┬──┬──┬──┬───┘
   │  │  │  │
   ▼  ▼  ▼  ▼
 Auth Product Inventory Order Analysis
 :9000 :9001  :9002    :9003   :9004
   │    │      │        │
   └────┴──────┴────────┘
         │        │
         ▼        ▼
    ┌─────────┐ ┌───────┐
    │ MySQL   │ │ Redis │
    │ :3306   │ │ :6379 │
    └─────────┘ └───────┘
         │
         ▼
    ┌─────────────┐
    │ AI Service  │ ← 仅 product 调用
    │ :5000 ONNX  │
    └─────────────┘
```

## 快速部署

### 1. 前置条件

- **服务器**: 4GB+ 内存推荐，2GB 可运行（需调整内存限制）
- **操作系统**: Linux（Alibaba Cloud 3 / CentOS 8+ / Ubuntu 20.04+）
- **软件**: Docker 24+ + Docker Compose Plugin + Git + Maven 3.6+

### 2. 安装 Docker

```bash
# Alibaba Cloud Linux 3
sudo dnf config-manager --add-repo https://mirrors.aliyun.com/docker-ce/linux/centos/docker-ce.repo
sudo dnf install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
sudo systemctl enable --now docker
```

### 3. 部署

```bash
git clone https://github.com/Kelsen03/SpringCLoud-vue3-yolov8n.git
cd SpringCLoud-vue3-yolov8n

# 加载基础镜像（如服务器无法访问 Docker Hub，需预先 docker save/load）
docker load -i /path/to/supermarket-base-images.tar

# 一键构建 + 启动
bash build.sh
```

### 4. 访问

| 服务 | 地址 | 说明 |
|------|------|------|
| 前端 | `http://IP:8888` | 80 端口国内需 ICP 备案 |
| Nacos | `http://IP:8848/nacos` | 免密 |

### 5. 默认账号

| 用户名 | 密码 | 角色 | 说明 |
|--------|------|------|------|
| admin | 123456 | HQ | 总部管理员，全部权限 |
| store1 | 123456 | STORE | 一号门店店长 |
| docker | 123456 | STORE | 测试账号 |
| lkq0120260325 | 123456 | CASHIER | 收银员示例 |

---

## 运维命令

```bash
# 状态
docker compose -f ~/SpringCLoud-vue3-yolov8n/docker-compose.yml ps

# 日志
docker compose logs -f supermarket-gateway

# 重启单个服务
docker compose restart supermarket-product

# 全部停/启
docker compose down
docker compose up -d

# 清理数据卷（危险！）
docker compose down -v
```

---

## 中国大陆部署注意事项

### Docker Hub 不可访问

中国大陆阿里云服务器无法从 Docker Hub 拉取镜像。解决方案：

1. **Windows 本地构建** — 安装 Docker Desktop，开 VPN 拉取镜像
2. **导出离线包** — `docker save` → tar → scp/上传到服务器
3. **服务器加载** — `docker load -i xxx.tar`

需要的 7 个基础镜像：

```
eclipse-temurin:8-jre-alpine  # Java 微服务（openjdk 已下架）
python:3.10-slim              # AI 服务
node:20-alpine                # 前端构建
nginx:1.25-alpine             # 前端运行
mysql:8.0.36                  # 数据库
redis:7.2-alpine              # 缓存
nacos/nacos-server:v2.2.3     # 注册中心
```

### 80 端口封锁

国内 ISP 对无 ICP 备案的 80/443 端口进行阻断。`docker-compose.yml` 已将 Nginx 映射为 `8888:80`，通过 `http://IP:8888` 访问。

### 旧服务端口冲突

部署 Docker 前需彻底停用旧的 systemd 服务：

```bash
systemctl stop nacos nginx redis mysql mysqld
systemctl disable nacos nginx redis mysql mysqld
systemctl mask mysqld mysql  # mask 比 disable 更强
pkill -9 -f nacos-server
```

---

## 2GB 内存优化

| 配置项 | 默认 | 2GB 建议 | 文件 |
|--------|------|----------|------|
| Nacos JVM | 128m | 256m | docker-compose.yml |
| MySQL buffer | 128m | 128m | docker/mysql/conf/my.cnf |
| Redis maxmemory | 128m | 128m | docker/redis/redis.conf |
| Java 服务内存 | 256m/个 | 256m/个 | docker-compose.yml |
| 关闭 analysis | — | 平时不开 | 凌晨定时任务 |

---

## 数据维护

### 恢复产品数据

```bash
docker exec -i supermarket-mysql mysql -uroot -p123456 -h127.0.0.1 supermarket_product < sql/product_import.sql
```

### 清除 Redis 缓存

```bash
docker exec supermarket-redis redis-cli FLUSHALL
```

### 重置密码（BCrypt 哈希不匹配时）

```bash
docker exec supermarket-mysql mysql -uroot -p123456 -h127.0.0.1 -e "
UPDATE supermarket_auth.user SET password='\$2a\$10\$IR5ya2Qh7aYwTa1zDgeng.wzF8L3wuahAP1LeSoIKeFKlcKeEo.Hy' WHERE username='admin';
"
```

---

## 本地开发

```bash
# 后端（IDEA 直接运行）
cd supermarket-product && mvn spring-boot:run

# 前端
cd supermarket-ui && npm install && npm run dev
```

本地开发时，所有 `application.yml` 的 `${}` 占位符默认值均为 `localhost`，可直接运行。

---

## 常见问题

| 现象 | 原因 | 解决 |
|------|------|------|
| 502 Bad Gateway | Gateway 未注册到 Nacos | 等 1-2 分钟或 restart gateway |
| health check unhealthy | Spring Security 拦截 actuator | SecurityConfig 需 permitAll `/actuator/**` |
| 登录后页面空白 | `<transition mode="out-in">` 卡住渲染 | 已移除 |
| 商品数据每次重启丢失 | `SQL_INIT_MODE=always` | 已改为 never |
| 数据为 20 条旧数据 | `data.sql` + `TRUNCATE` | 文件已删除 |
| Docker Hub 拉镜像超时 | GFW | 离线 docker save/load |
| 80 端口无法访问 | ISP 封锁 | 使用 8888 端口 |
