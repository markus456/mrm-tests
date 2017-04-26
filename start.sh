#!/bin/bash

target=node_00$1_network
ssh vagrant@${!target} "sudo systemctl start mariadb"
