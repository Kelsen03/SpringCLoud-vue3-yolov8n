# 连锁超市微服务管理系统

基于 **Spring Cloud Alibaba + Vue3 + YOLOv8 + ONNX** 的连锁超市综合管理平台，涵盖商品管理、多门店库存隔离、跨店调拨、智能收银、AI 视觉识别、数据分析及收银员换班等完整业务链路。

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

### AI 识别服务（Python + ONNX）

| 技术 | 说明 |
|------|------|
| Flask | RESTful API（端口 5000） |
| YOLOv8n | 自建 1219 张 10 类数据集迁移学习微调 |
| ONNX Runtime | 推理引擎，内存 < 300MB，无 PyTorch 依赖 |
| OpenCV | 图像预处理、边缘检测、颜色分析 |
| Systemd | 开机自启，异常自动重启 |

> **v4.0 起**：推理引擎由 PyTorch 替换为 ONNX Runtime，内存占用降低 40%（500MB → 300MB），适配 2 核 2G 边缘服务器。模型基于 1219 张自建数据集训练，2521 个标注实例，验证集 mAP@0.5 = 0.929。

---

## 🧠 AI 识别核心特性

### 模型训练
- **数据集**：1219 张图片（手机实拍 + 视频抽帧），2521 个多边形标注框，7:2:1 分层拆分
- **10 类商品**：可口可乐、百事可乐、雪碧、芬达、农夫山泉、王老吉、红牛、脉动、乐事、康师傅
- **增强策略**：Mosaic、Mixup(0.15)、Copy-Paste(0.1)、±45°旋转、透视变换、缩放抖动
- **训练配置**：YOLOv8n，640×640，80 epochs，RTX 4060 GPU，AMP 混合精度
- **mAP@0.5 = 0.929**，mAP@0.5:0.95 = 0.834

### 推理优化
- **ONNX Runtime**：模型导出为 ONNX 格式（11.7MB），onnxruntime 推理，自动回退 PyTorch
- **F1-最优置信度校准**：在验证集 234 张图上逐类计算 P-R 曲线，取 F1 最大值对应的置信度作为该类阈值（0.19~0.78），替代人工手调
- **分级阈值体系**：脉动 0.78（最严）→ 可口可乐 0.68 → 康师傅 0.72 → 百事可乐 0.20（默认）→ 农夫山泉 0.45

### 后处理策略
- **Canny 纹理过滤**：对百事可乐/脉动/红牛等易误检类，检测边界框内边缘密度 < 2% 判定为纯色背景误检
- **遮挡救援机制**：首轮检出 < 3 个时，对未检出类别置信度阈值自动减半二次检索
- **HSV 颜色分析**：乐事薯片检测后，依据包装主色调区分原味（黄色）与青柠味（绿色）
- **NAME_MAP 映射**：英文类名精确映射到数据库商品全名（含规格）

---

## ✨ 核心功能

### 库存管理
- **行级锁原子扣减**：`UPDATE ... SET stock = stock - #{count} WHERE stock >= #{count}` 下沉至 InnoDB 引擎层，杜绝超卖
- **7 级保质期自动填充**：烘焙 1 月 / 乳制品 6 月 / 饮品冷冻 9 月 / 零食熟食 12 月 / 主粮干货 18 月 / 调味品罐头 24 月 / 纸品个护酒类 36 月
- **库存四级排序**：过期(红) → 临期 30 天(橙) → 低于预警线(黄) → 正常(绿)，DATEDIFF 实时计算
- **跨店调拨**：源店扣减 + 目标店增加 + 流水记录，`@Transactional` 事务保障
- **FIFO 日期合并**：调拨时按先进先出原则保留最早生产日期
- **自动可见性修复**：调拨后自动将私有商品升级为全局商品，解决跨店数据孤岛
- **补货记录持久化**：replenish_record 表记录每次补货的商品、数量、生产日期、保质期及操作时间

### 商品管理
- **统配/自营隔离**：`isLocal` + SQL 动态条件（`is_local=0 OR store_id=#{storeId}`），数据级权限过滤
- **store 门店表**：独立门店档案表，OrderMapper 跨库查询门店名称
- **条形码支持**：EAN-13 规范，适配扫码枪，`/product/barcode/{code}` 接口
- **Redis 缓存**：商品列表 30 分钟过期，`@CacheEvict(allEntries=true)` 自动清缓存

### 智能收银（POS）
- **换班系统**：开班输入备用金 → 收银 → 交班自动对账（理论现金 vs 实际现金）
- **AI 视觉识别**：YOLOv8n + ONNX 推理，端到端识别 10 类商品，含纹理过滤、遮挡救援、颜色子类分析
- **条形码扫描**：扫码枪键盘输入自动识别，输入框手动查找
- **热门商品**：按 `product_sales` 累计销量 TOP10，点即加入购物车
- **会员积分**：1000 积分抵 5 元，散客/会员双模式

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
- Python 3.8+（AI 服务）

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

### 3. AI 服务（ONNX 模式，推荐）
```bash
pip install flask flask-cors opencv-python onnxruntime

# 确保 best.onnx 与 ai_server.py 同目录
cd 前端 && python ai_server.py   # 端口 5000

# 或配置 systemd 开机自启
sudo vim /etc/systemd/system/supermarket-ai.service
sudo systemctl enable --now supermarket-ai
```

> 若 ONNX 加载失败，自动回退 PyTorch（需额外安装 `ultralytics`）。

### 4. 种子数据
```bash
# 导入商品数据（432 条，17 品类）
mysql -u root -p supermarket_product < product_import.sql
```

---

## 📁 项目结构

```
陆铿全源码/
├── 前端/
│   ├── supermarket-ui/      # Vue3 前端项目
│   │   ├── src/views/       # 页面组件
│   │   │   ├── Login.vue    # 登录页
│   │   │   ├── Pos.vue      # 收银台（AI 识别 + 换班）
│   │   │   ├── Product.vue  # 商品定价管理
│   │   │   ├── Analysis.vue # 数据分析看板
│   │   │   └── ...
│   │   └── dist/            # 生产构建输出
│   ├── ai_server.py         # AI 识别服务（ONNX）
│   ├── best.onnx            # ONNX 推理模型（11.7MB）
│   └── best.pt              # PyTorch 模型备份
│
├── 连锁超市微服务管理系统/
│   └── supermarket-cloud/   # Spring Cloud 父工程
│       ├── supermarket-gateway/
│       ├── supermarket-auth/
│       ├── supermarket-product/
│       ├── supermarket-inventory/
│       ├── supermarket-order/
│       └── supermarket-analysis/
```

---

## 📋 更新日志

### v4.0 (2026-06-22)
- **ONNX 推理引擎**：模型导出 ONNX 格式，onnxruntime 推理，内存降低 40%，移除生产环境 PyTorch 依赖
- **v5 模型**：自建数据集扩增至 1219 张图片、2521 标注实例，mAP@0.5 = 0.929
- **F1-最优置信度校准**：验证集 234 张图逐类计算最优阈值（0.19~0.78），替代人工手调
- **Canny 纹理过滤**：边缘密度 < 2% 判定为纯色背景误检，解决百事可乐/脉动/红牛"看颜色猜商品"问题
- **遮挡救援机制**：检出 < 3 个时自动二次检索，阈值减半捞回被遮挡商品
- **HSV 颜色子类分析**：乐事薯片根据包装主色调区分原味（黄）与青柠味（绿）
- **NAME_MAP 精确化**：映射至数据库商品全名（含规格），如"可口可乐 500ml"

### v3.1 (2026-05-21)
- **store 门店表**：新增 `store` 表 + Store 实体 + StoreMapper
- **7 级保质期分类**：由 3 大类升级为 7 级精细分类
- **DataInitializer**：新增门店自动初始化（旗舰店/社区店/生鲜店）

### v3.0 (2026-05-20)
- YOLOv8n 迁移学习微调：自建 218 张数据集，端到端识别替代 HSV 颜色分析
- NAME_MAP 英文类名→中文商品名映射
- 训练损失曲线 + 混淆矩阵

### v2.x (2026-05-16~17)
- 补货推荐算法 v4：频率×销量双因子 + ABC 帕累托分类
- 库存四级排序、跨店调拨 FIFO
- AI：COCO 类别映射 + 颜色识别初级方案
- 换班系统、条形码支持、会员积分

---

## 📝 许可证

本项目仅供学习交流使用。

Copyright © 2026 陆铿全
