CREATE TABLE IF NOT EXISTS `user` (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  username VARCHAR(50),
  password VARCHAR(50),
  role VARCHAR(20),  -- HQ / STORE / CASHIER
  store_id INT,
  real_name VARCHAR(50)
);
