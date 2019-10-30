#!/bin/sh

export CARTESI_CONCERN_KEY=`cat /opt/cartesi/logger/config/private_key`
export CARTESI_CONCERN_ADDRESS=`cat /opt/cartesi/logger/config/account`
cd /opt/cartesi/manager_server
python3 manager_server.py -a 0.0.0.0 -ba ganache
