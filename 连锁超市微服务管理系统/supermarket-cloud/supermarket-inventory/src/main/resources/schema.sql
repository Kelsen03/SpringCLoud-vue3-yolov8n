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
  create_time DATETIME
);
