-- 生成最近 14 天测试销售数据
-- 用于补货推荐算法消融实验

INSERT INTO supermarket_order.`order` (id, order_no, store_id, member_id, total_price, points, create_time, cashier_account, create_by)
SELECT
  2000 + r.num AS id,
  CONCAT('TEST-', DATE_FORMAT(DATE_SUB(NOW(), INTERVAL r.day DAY), '%m%d'), '-', r.num) AS order_no,
  r.store_id,
  NULL AS member_id,
  0 AS total_price,
  0 AS points,
  DATE_SUB(NOW(), INTERVAL r.day DAY) + INTERVAL (r.num % 10) HOUR AS create_time,
  'test' AS cashier_account,
  'test' AS create_by
FROM (
  SELECT (@row := @row + 1) AS num,
         FLOOR(RAND() * 3) + 1 AS store_id,
         FLOOR(RAND() * 14) AS day
  FROM supermarket_product.product
  CROSS JOIN (SELECT @row := 0) r
  LIMIT 300
) r
WHERE NOT EXISTS (SELECT 1 FROM supermarket_order.`order` WHERE id = 2000 + r.num);


-- 生成 order_items（每个订单 1-3 件商品）
INSERT INTO supermarket_order.order_item (id, order_id, product_id, price, quantity)
SELECT
  3000 + r.num AS id,
  2000 + (r.num % 300) + 1 AS order_id,
  (SELECT id FROM supermarket_product.product ORDER BY RAND() LIMIT 1) AS product_id,
  (SELECT price FROM supermarket_product.product WHERE id = product_id) AS price,
  FLOOR(RAND() * 5) + 1 AS quantity
FROM (
  SELECT (@row2 := @row2 + 1) AS num
  FROM supermarket_product.product
  CROSS JOIN (SELECT @row2 := 0) r2
  LIMIT 500
) r;


-- 更新订单总价
UPDATE supermarket_order.`order` o
SET total_price = (
  SELECT COALESCE(SUM(oi.price * oi.quantity), 0)
  FROM supermarket_order.order_item oi
  WHERE oi.order_id = o.id
);
"""