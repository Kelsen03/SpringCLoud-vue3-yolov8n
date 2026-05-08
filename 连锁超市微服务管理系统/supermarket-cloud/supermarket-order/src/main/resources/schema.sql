-- 1. 订单表
-- DROP TABLE IF EXISTS `order`;
CREATE TABLE IF NOT EXISTS `order` (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  store_id BIGINT,
  member_id BIGINT,
  total_price DECIMAL(10,2),
  points INT,
  create_time DATETIME,
  cashier_account VARCHAR(50)
);

-- 兼容已有库：若历史表缺失字段则补齐（已通过重建表处理）

-- 2. 订单明细表
CREATE TABLE IF NOT EXISTS order_item (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  order_id BIGINT,
  product_id BIGINT,
  product_name VARCHAR(100),
  category VARCHAR(50),
  price DECIMAL(10,2),
  quantity INT
);

-- 3. 会员积分表
CREATE TABLE IF NOT EXISTS member (
  id BIGINT PRIMARY KEY,
  points INT DEFAULT 0
);

-- 4. 商品销量累计（按门店）
CREATE TABLE IF NOT EXISTS product_sales (
  store_id BIGINT,
  product_id BIGINT,
  total_quantity INT DEFAULT 0,
  PRIMARY KEY (store_id, product_id)
);

-- 5. 销量排行视图（依赖商品库，建议在分析服务实现，避免启动依赖）
-- 视图已移除，排行榜由 analysis-service 提供

-- 6. 门店类别销量视图（消费偏好）
-- 视图已移除，消费偏好由 analysis-service 提供
