#!/bin/sh

export CARTESI_CONCERN_KEY=`cat /opt/cartesi/etc/keys/private_key`
export CARTESI_CONCERN_ADDRESS=`cat /opt/cartesi/etc/keys/account`
/opt/cartesi/bin/logger-server -a 0.0.0.0 -d /opt/cartesi/srv/logger-server
