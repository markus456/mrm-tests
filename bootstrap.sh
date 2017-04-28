#!/bin/bash

pkill -9 client.sh

ssh -T vagrant@192.168.121.14 <<EOF
sudo systemctl start mariadb
EOF

ssh -T vagrant@192.168.121.250 <<EOF
sudo systemctl start mariadb
EOF

ssh -T vagrant@192.168.121.83 <<EOF
sudo systemctl stop replication-manager
replication-manager bootstrap --clean-all
sudo systemctl start replication-manager
EOF

ssh -T vagrant@192.168.121.141 <<EOF
sudo systemctl restart maxscale
EOF
