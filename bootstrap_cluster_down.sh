#!/bin/bash

pkill -9 client.sh

ssh -T vagrant@$node_000_network <<EOF
sudo systemctl start mariadb
EOF

ssh -T vagrant@$node_001_network <<EOF
sudo systemctl start mariadb
EOF

ssh -T vagrant@$galera_000_network <<EOF
sudo systemctl stop replication-manager
replication-manager bootstrap --clean-all
EOF

ssh -T vagrant@$node_000_network <<EOF
sudo systemctl stop mariadb
EOF

ssh -T vagrant@$node_001_network <<EOF
sudo systemctl stop mariadb
EOF

ssh -T vagrant@$galera_000_network <<EOF
sudo systemctl start replication-manager
EOF

ssh -T vagrant@$maxscale_IP <<EOF
sudo systemctl restart maxscale
EOF
