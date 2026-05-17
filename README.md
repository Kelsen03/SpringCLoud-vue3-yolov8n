# 连锁超市微服务管理系统

基于 **Spring Cloud Alibaba + Vue3 + YOLOv8** 的连锁超市综合管理平台，涵盖商品管理、多门店库存隔离、跨店调拨、智能收银、数据分析及收银员换班等完整业务链路。

---

## 🏗️ 技术架构

### 后端（Spring Cloud 微服务）

| 组件 | 技术 | 版本 |
|------|------|------|
| 基础框架 | Spring Boot | 2.7.18 |
| 微服务治理 | Spring Cloud + Alibaba | 2021.0.8 / 2021.0.5.0 |
| 注册中心 | Nacos | 2.x |
| API 网关 | Spring Cloud Gateway | — |
| 服务间调用 | OpenFeign + LoadBalancer | — |
| 安全认证 | JWT + BCrypt + Spring Security | — |
| ORM | MyBatis-Plus | 3.5.3.1 |
| 数据库 | MySQL | 8.0 |
| 缓存 | Redis | 6.2+ |
| 语言 | Java | 8 |

**微服务模块**：

| 服务 | 端口 | 职责 |
|------|------|------|
| `gateway` | 8000 | 统一入口，JWT 鉴权，路由转发 |
| `auth` | 9000 | 用户登录注册，BCrypt 密码加密，JWT 签发 |
| `product` | 9001 | 商品档案管理，统配/自营权限隔离，Redis 缓存 |
| `inventory` | 9002 | 库存原子扣减，跨店调拨，FIFO 日期合并 |
| `order` | 9003 | 收银下单，会员积分，订单流水号，换班管理 |
| `analysis` | 9004 | 定时数据聚合，门店/商品排行，区域偏好分析 |

### 前端（Vue 3）

| 技术 | 说明 |
|------|------|
| Vue 3 | `<script setup>` 组合式 API |
| Vite | 构建工具 |
| Element Plus | UI 组件库 |
| ECharts | 数据分析图表 |
| Axios | HTTP 请求 |
| Vue Router 4 | 角色路由守卫 |

### AI 识别服务（Python）

| 技术 | 说明 |
|------|------|
| Flask | RESTful API |
| YOLOv8n | 轻量目标检测（~3.2M 参数） |
| OpenCV | HSV 色彩空间分析 — 7 种饮料颜色区分 + 25+ COCO 类别映射（内存 <200MB） |

### Systemd 服务

| 服务 | 说明 |
|------|------|
| `supermarket-ai.service` | AI 识别开机自启，崩溃自动重启 |
| `supermarket-*.service` | 6 个微服务 systemd 守护 |

---

## ✨ 核心功能

### 库存管理
- **行级锁原子扣减**：`WHERE stock >= #{count}` 下沉至 InnoDB 引擎层，杜绝超卖
- **跨店调拨**：源店扣减 + 目标店增加 + 流水记录，`@Transactional` 事务保障
- **FIFO 日期合并**：调拨时按先进先出原则保留最早生产日期
- **自动可见性修复**：调拨后自动将私有商品升级为全局商品，解决跨店数据孤岛

### 商品管理
- **统配/自营隔离**：`isLocal` + SQL 动态条件，数据级权限过滤
- **条形码支持**：EAN-13 规范，适配扫码枪
- **Redis 缓存**：商品列表 30 分钟过期，更新/新增自动清缓存

### 智能收银（POS）
- **换班系统**：开班输入备用金 → 收银 → 交班自动对账（理论现金 vs 实际现金）
- **AI 视觉识别**：YOLOv8 定位 + HSV 颜色分析（可乐/雪碧/芬达/百事/维他柠檬茶/东方树叶/农夫山泉），25+ 种食品日用品映射
- **条形码扫描**：扫码枪键盘输入自动识别，输入框手动查找
- **热门商品**：按 `product_sales` 累计销量 TOP10，点即加入购物车
- **会员积分**：1000 积分抵 5 元

### 数据分析
- **门店销售额占比**：饼图，按 `order` 表实时聚合
- **商品销量 TOP10**：横向柱状图
- **区域热销偏好**：门店 × 品类堆叠柱状图，分类动态从数据库读取
- **定时聚合**：`@Scheduled` 每日凌晨 2 点自动执行

### 安全
- **BCrypt 密码哈希**：不可逆加密，盐值内嵌密文
- **JWT 无状态认证**：Payload 含角色 + 门店 ID，Gateway 统一拦截
- **DataInitializer**：首次启动自动初始化默认账号

---

## 🚀 快速启动

### 环境要求
- JDK 1.8 / Maven 3.6+
- MySQL 8.0 / Redis 6.2+
- Node.js 16+
- Python 3.8+（AI 服务可选）

### 1. 后端
```bash
cd 连锁超市微服务管理系统/supermarket-cloud
mvn clean package -DskipTests

# 按顺序启动：gateway → auth → product → inventory → order → analysis
java -jar supermarket-gateway/target/supermarket-gateway-*.jar
java -jar supermarket-auth/target/supermarket-auth-*.jar
# ...
```

### 2. 前端
```bash
cd 前端/supermarket-ui
npm install
npm run dev       # 开发
npm run build     # 生产 → dist/
```

### 3. AI 服务
```bash
pip install ultralytics flask flask-cors opencv-python
# 手动运行
cd 前端 && python ai_server.py   # 端口 5000

# 或配置 systemd 开机自启（推荐）
sudo vim /etc/systemd/system/supermarket-ai.service
sudo systemctl enable --now supermarket-ai
```

### 4. 种子数据
```bash
# 导入商品数据（432 条，17 品类）
mysql -u root -p supermarket_product < product_import.sql

# 初始化库存（每商品 × 3 门店）
# 见服务器部署文档
```

---

## 📁 项目结构

```
陆铿全源码/
├── 前端/
│   ├── supermarket-ui/      # Vue3 前端项目
│   │   ├── src/views/       # 页面组件
│   │   │   ├── Login.vue    # 登录页（暗色主题 + 居中品牌标识）
│   │   │   ├── Pos.vue      # 收银台（换班 + AI 识别）
│   │   │   ├── Product.vue  # 商品定价管理
│   │   │   ├── Analysis.vue # 数据分析看板
│   │   │   └── ...
│   │   └── dist/            # 生产构建输出
│   └── ai_server.py         # Python AI 识别服务
│
└── 连锁超市微服务管理系统/
    └── supermarket-cloud/   # Spring Cloud 父工程
        ├── supermarket-gateway/
        ├── supermarket-auth/
        ├── supermarket-product/
        ├── supermarket-inventory/
        ├── supermarket-order/
        └── supermarket-analysis/
```

---

## 📋 更新日志

### v2.2 (2026-05-17)
- 渡边极简黑白 UI：Lenis 平滑滚动 + 自定义光标 + Landing 页面
- 收银员排班分析：工时计算 + 备用金 + 对账差异表
- 补货自动刷新：补货后推荐列表即时更新
- Inventory/Product/Analysis/Transfer 统一设计语言

### v2.1 (2026-05-17)
- 补货推荐算法 v4：频率×销量双因子 + ABC 帕累托分类
- 库存排序：过期→临期→缺货→正常
- 库存清零：clearInventory 仅归零不删除
- 条形码：Transfer/Pos 下拉框支持搜索，product/barcode 接口
- 分析页补货清单 + Excel 导出（xlsx）
- UTF8mb4 编码修复，保质期按品类 INSERT
- replenish_record 表记录补货历史

### v2.0 (2026-05-16)
- AI：25+ COCO 类别映射，7 种饮料颜色识别，阈值降至 0.35
- 条形码：`/product/barcode/{code}` 接口 + 前端输入框 + 扫码枪键盘监听
- 收银台：pos-mode 去全局卡片包裹，头栏精简与购物车像素对齐
- 字体：全页面放大适配答辩截图（普通顾客 16px 基准）
- 布局：摄像头回归左侧面板自适应宽度，热门商品 18px 大字体

### v1.0 (2026-05-15)
- 换班系统：shift_record 表 + 开班/交班对账
- BCrypt + Spring Security + Redis 缓存
- @Scheduled 定时数据聚合
- 商品数据：432 条 17 品类 + 条形码字段
- 订单流水号 + 门店信息 + 小票展示

## 📝 许可证

本项目仅供学习交流使用。

Copyright © 2026 陆铿全
