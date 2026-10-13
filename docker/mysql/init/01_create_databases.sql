CREATE DATABASE IF NOT EXISTS ecommerce_source
  CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;

GRANT ALL PRIVILEGES ON ecommerce_source.* TO 'dw_user'@'%';
FLUSH PRIVILEGES;