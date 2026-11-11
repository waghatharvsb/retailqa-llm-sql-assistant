#!/bin/bash
mysql -uroot -p"$MYSQL_ROOT_PASSWORD" <<SQL
CREATE USER IF NOT EXISTS 'qa_app'@'%' IDENTIFIED BY '$DB_PASSWORD';
GRANT SELECT ON atliq_tshirts.* TO 'qa_app'@'%';
FLUSH PRIVILEGES;
SQL
