#!/bin/bash

#
# This is a simple client that creates a table and inserts data into it
# every second
#

user=skysql
password=skysql
host=192.168.121.141
port=4006

table_def="CREATE OR REPLACE TABLE test.t1 (id INT)"
table_insert="INSERT INTO test.t1 VALUES (1)"

mysql -u $user -p$password -h $host -P $port -e "$table_def"


while true
do
    mysql -u $user -p$password -h $host -P $port -e "$table_insert"
    sleep 1
done
