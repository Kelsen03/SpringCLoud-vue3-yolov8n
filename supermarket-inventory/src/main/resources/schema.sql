-- DROP TABLE IF EXISTS inventory;
CREATE TABLE IF NOT EXISTS inventory (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  product_id BIGINT,
  product_name VARCHAR(100),
  store_id BIGINT,
  stock INT,
  warning_stock INT
);

CREATE TABLE IF NOT EXISTS stock_transfer (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  product_id BIGINT,
  from_store BIGINT,
  to_store BIGINT,
  quantity INT,
  status VARCHAR(20) DEFAULT 'COMPLETED',
  create_time DATETIME
);

-- 补货记录表
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
);
