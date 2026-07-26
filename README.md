# 连锁超市微服务管理系统

基于 **Spring Cloud Alibaba + Vue3 + YOLOv8 + ONNX** 的连锁超市综合管理平台，涵盖商品管理、多门店库存隔离、跨店调拨、AI 视觉收银、数据分析及收银员换班等完整业务链路。

全新深海主题营销首页，GSAP 驱动的叙事式滚动体验。

---

## 前端首页亮点

- **叙事式滚动**：暗调全屏滚动 + Lenis 平滑缓动，章节式内容呈现
- **光标聚光灯**：标题文字默认暗色，光标以径向渐变实时照亮周围文字（`background-clip: text`）
- **Canvas 海浪**：三层正弦海浪动画，相位随滚动位置动态变化
- **开幕序幕**：GSAP 文字淡入淡出序列，自动过渡到主页
- **3D 翻转登录弹窗**：毛玻璃 + 3D `rotateY` 翻转，登录/注册双面
- **YOLO 检测可视化**：彩色检测框 + 置信度标签，模拟 AI 实时识别
- **自定义光标**：慢悠悠跟随的暖色/冷色光环，hover 交互反馈
- **技术链接**：hover 展开描述气泡，click 跳转外部文档
- **调色盘**（开发版）：右下角实时换色面板，6 个预设方案

---

## 技术架构

### 后端

| 组件 | 技术 | 版本 |
|------|------|------|
| 基础框架 | Spring Boot | 2.7.18 |
| 微服务 | Spring Cloud Alibaba | 2021.0.8 / 2021.0.5.0 |
| 注册中心 | Nacos | 2.x |
| 网关 | Spring Cloud Gateway | — |
| 认证 | JWT + BCrypt | — |
| ORM | MyBatis-Plus | 3.5.3.1 |
| 数据库 | MySQL | 8.0 |

| 服务 | 端口 | 职责 |
|------|------|------|
| `gateway` | 8000 | API 网关，JWT 拦截 |
| `auth` | 9000 | 登录注册，BCrypt |
| `product` | 9001 | 商品管理 |
| `inventory` | 9002 | 库存 + 调拨 |
| `order` | 9003 | 订单 + 换班 |
| `analysis` | 9004 | 数据聚合 |

### 前端

| 技术 | 说明 |
|------|------|
| Vue 3 | Composition API |
| Vite | 构建工具 |
| Element Plus | UI 组件库 |
| ECharts | 数据图表 |
| **GSAP** | 动画引擎（ScrollTrigger + Timeline） |
| **Lenis** | 平滑滚动 |
| Axios | HTTP 请求 |

### AI 识别服务（Flask + YOLOv8n + ONNX）

| 技术 | 说明 |
|------|------|
| Flask | API（端口 5000） |
| YOLOv8n | 自建 10 类 1219 张数据集，mAP@0.5 = 0.925 |
| ONNX Runtime | best.onnx 推理引擎，内存 < 300MB |
| OpenCV | HSV 颜色分析 + Canny 纹理过滤 |
| Ultralytics | best.pt 直接推理（PyTorch 回退） |

#### 推理策略

| 策略 | 说明 |
|------|------|
| 分级置信度 | 5 类困难商品用低阈值（0.12~0.30），其余 0.20 |
| Canny 纹理过滤 | pepsi/redbull/mizone 边缘密度 <2% 判为背景误检 |
| 遮挡救援 | 检出 <3 件时自动减半阈值二次检索 |
| HSV 颜色分析 | 乐事薯片：绿色占比 >5% → 青柠味，否则原味 |

#### 分级置信度阈值

| 类别 | 阈值 | 原因 |
|------|:--:|------|
| 农夫山泉 | 0.12 | 透明瓶身，特征弱 |
| 王老吉 | 0.15 | 数据量偏少 |
| 红牛 | 0.20 | 金罐反光易误识别 |
| 脉动 | 0.28 | 蓝色瓶身易误识别 |
| 百事可乐 | 0.30 | 蓝红包装易与背景混淆 |
| 其余 5 类 | 0.20 | 标准阈值 |

---

## 快速启动

### 环境要求
- JDK 1.8 / Maven 3.6+ / MySQL 8.0 / Redis 6.2+
- Node.js 16+ / Python 3.8+

### 后端
```bash
cd 连锁超市微服务管理系统/supermarket-cloud
mvn clean package -DskipTests
java -jar supermarket-gateway/target/supermarket-gateway-*.jar
# 按序启动 auth → product → inventory → order → analysis
```

### 前端
```bash
cd 前端/supermarket-ui
npm install
npm run dev       # 开发 localhost:5173
npm run build     # 生产 → dist/
```

### AI 服务
```bash
pip install flask flask-cors opencv-python onnxruntime ultralytics
python ai_server.py   # 端口 5000
```

---

## 部署

前端 `dist/` 上传至 Nginx `/usr/share/nginx/html/`，配置 API 代理：

```nginx
location /api/ {
    proxy_pass http://127.0.0.1:8000/;
}
```

---

## 项目结构

```
陆铿全源码/
├── 前端/
│   └── supermarket-ui/
│       └── src/views/
│           ├── Login.vue              ← 首页（叙事式营销落地页）
│           ├── Pos.vue                ← AI 收银台
│           ├── Product.vue            ← 商品管理
│           ├── Inventory.vue          ← 库存管理
│           ├── Order.vue              ← 订单管理
│           ├── Analysis.vue           ← 数据分析
│           └── Transfer.vue           ← 跨店调拨
│
├── 连锁超市微服务管理系统/
│   └── supermarket-cloud/
│       ├── supermarket-gateway/
│       ├── supermarket-auth/
│       ├── supermarket-product/
│       ├── supermarket-inventory/
│       ├── supermarket-order/
│       └── supermarket-analysis/
```

---

## 许可证

仅供学习交流使用。Copyright © 2026 陆铿全
