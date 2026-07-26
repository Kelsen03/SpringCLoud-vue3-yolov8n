-- ============================================
-- 数据库迁移脚本 (v2.0)
-- 用于将现有数据库升级到论文一致性版本
-- ============================================

-- 1. auth 库: 扩展 password 字段以支持 BCrypt (60字符)
ALTER TABLE `user` MODIFY COLUMN `password` VARCHAR(200);

-- 2. product 库: 添加 barcode 字段
ALTER TABLE `product` ADD COLUMN IF NOT EXISTS `barcode` VARCHAR(50) AFTER `name`;

-- 3. order 库: 添加 order_no 和 create_by 字段
ALTER TABLE `order` ADD COLUMN IF NOT EXISTS `order_no` VARCHAR(50) AFTER `id`;
ALTER TABLE `order` ADD COLUMN IF NOT EXISTS `create_by` VARCHAR(50) AFTER `cashier_account`;

-- 4. 注意: 旧密码为明文, BCrypt 迁移由 DataInitializer 在启动时自动处理
--    仅对默认账号(admin/store1/store2/store3)生效
--    其他已注册用户的密码需手动重置或重新注册
