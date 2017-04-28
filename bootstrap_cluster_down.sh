#!/bin/bash

pkill -9 client.sh

ssh -T vagrant@192.168.121.14 <<EOF
sudo systemctl stop mariadb
EOF

ssh -T vagrant@192.168.121.250 <<EOF
sudo systemctl stop mariadb
EOF

ssh -T vagrant@192.168.121.83 <<EOF
sudo systemctl restart replication-manager
EOF
