# 连锁超市微服务管理系统 (SpringCloud + Vue3 + YOLOv8n)

本项目是一个基于**微服务架构**的连锁超市综合管理系统，采用前后端分离模式开发。系统不仅涵盖了传统的超市商品、库存、订单等核心业务管理，还创新性地引入了基于 **YOLOv8** 的 AI 图像识别技术，实现对特定商品（如不同品牌饮料）的智能识别。

## 🏗️ 系统架构与技术栈

### 1. 后端 (Spring Cloud 微服务)
后端采用 Spring Cloud Alibaba 生态构建，划分为多个独立职责的微服务模块：
- **核心框架**: Spring Boot (2.7.18) + Java 8
- **微服务组件**: Spring Cloud (2021.0.8) + Spring Cloud Alibaba (2021.0.5.0)
- **注册中心/配置中心**: Nacos
- **API 网关**: Spring Cloud Gateway
- **服务间调用**: OpenFeign + LoadBalancer
- **数据持久化**: MySQL (8.0.33) + MyBatis-Plus (3.5.3.1)
- **安全认证**: JWT (JSON Web Token)
- **模块划分**: 
  - `gateway`: 统一网关路由
  - `auth`: 用户认证授权中心
  - `product`: 商品管理服务
  - `inventory`: 库存管理服务
  - `order`: 订单管理服务
  - `analysis`: 数据统计分析服务

### 2. 前端 (Vue 3)
前端采用最新的 Vue 3 技术栈打造现代化后台管理界面：
- **核心框架**: Vue 3
- **构建工具**: Vite
- **UI 组件库**: Element Plus
- **路由与状态**: Vue Router 4
- **网络请求**: Axios
- **数据可视化**: ECharts (用于报表分析)
- **其他依赖**: Dayjs, XLSX (用于导出 Excel)

### 3. AI 图像识别服务 (Python)
独立的 Python 服务，用于处理前端上传的图像，进行智能分析：
- **核心框架**: Flask + Flask-CORS 提供 RESTful API
- **AI 算法**: **YOLOv8** (使用轻量级 `yolov8n.pt` 模型) 进行目标检测
- **图像处理**: OpenCV + NumPy (结合 HSV 色彩空间进行二次分析)
- **主要功能**: 接收 Base64 图片数据，识别出特定商品（如通过颜色特征区分可口可乐、雪碧、农夫山泉等），返回识别结果。

---

## 🚀 快速启动指南

### 环境准备
在运行项目前，请确保本地已安装以下环境：
- JDK 1.8
- Maven 3.6+
- MySQL 8.0+
- Node.js 16+ (推荐 18.x)
- Python 3.8+ (需安装 `ultralytics`, `flask`, `opencv-python` 等依赖)
- Nacos Server (建议 2.x 版本)

### 1. 启动后端微服务
1. 在 MySQL 中创建对应的数据库，并导入相关的 SQL 脚本（请检查各模块资源目录）。
2. 启动 Nacos 服务端。
3. 修改各微服务（在 Nacos 或 `application.yml` 中）的数据库连接配置及 Nacos 地址。
4. 按顺序启动微服务：
   - 先启动 `gateway` 和 `auth` 服务。
   - 随后启动 `product`、`inventory`、`order` 等业务微服务。

### 2. 启动 AI 识别服务
1. 进入 Python 脚本所在目录。
2. 安装所需依赖：`pip install ultralytics flask flask-cors opencv-python numpy`
3. 运行服务：`python ai_server.py`
4. 确保模型文件 `yolov8n.pt` 能够被正确加载。

### 3. 启动前端管理系统
1. 进入 `前端` 目录：
   ```bash
   cd 前端
   ```
2. 安装依赖：
   ```bash
   npm install
   ```
3. 运行开发服务器：
   ```bash
   npm run dev
   ```
4. 在浏览器中打开控制台输出的本地地址（如 `http://localhost:5173`）即可访问系统。

---

## 📝 许可证
本项目仅供学习交流使用。
