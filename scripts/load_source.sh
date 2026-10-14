#!/bin/sh
set -e

for f in Couriers Riders Users Products Orders OrderItems; do
  echo "Loading faker_$f.sql ..."
  mysql -uroot -p"$MYSQL_ROOT_PASSWORD" ecommerce_source < /data/faker_$f.sql
done

echo "Done."