#!/bin/bash
set -e

mysql -uroot -p"$MYSQL_ROOT_PASSWORD" <<EOSQL
CREATE DATABASE IF NOT EXISTS ecommerce_source
  CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;

GRANT SELECT ON ecommerce_source.* TO '${MYSQL_USER}'@'%';
FLUSH PRIVILEGES;
EOSQL