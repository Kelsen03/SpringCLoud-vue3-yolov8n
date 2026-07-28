# 修复 root 用户权限（MariaDB 数据导入后 MySQL 8.0 权限表被覆盖）
# 此脚本在 MySQL 首次初始化时自动执行
GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' WITH GRANT OPTION;
FLUSH PRIVILEGES;
