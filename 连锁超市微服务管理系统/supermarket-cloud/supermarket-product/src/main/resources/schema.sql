DROP TABLE IF EXISTS product;
CREATE TABLE IF NOT EXISTS product (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(100),
  barcode VARCHAR(50),
  category VARCHAR(50),
  price DECIMAL(10,2),
  promo_price DECIMAL(10,2),
  is_local TINYINT,        -- 0 总部商品 1 门店商品
  store_id BIGINT          -- 门店商品所属门店
);
