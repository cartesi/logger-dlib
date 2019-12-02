#!/bin/sh

set -e

if [[ -z "${MNEMONIC}" ]]; then
    # does not have mnemonic env variable, wait for keys in directory /opt/cartesi/etc/keys/
    dockerize -wait file://$BASE/etc/keys/keys_done -timeout ${TIMEOUT}
fi

if [[ -f "/opt/cartesi/etc/keys/private_key" ]]; then
    # export private key variable if file exists
    export CARTESI_CONCERN_KEY=$(cat /opt/cartesi/etc/keys/private_key)
fi

if [[ -f "/opt/cartesi/etc/keys/account" ]]; then
    # export account address if file exists
    export CARTESI_CONCERN_ADDRESS=$(cat /opt/cartesi/etc/keys/account)
fi

# wait for deployment
dockerize -wait file://$BASE/share/blockchain/contracts/deploy_done -timeout ${TIMEOUT}

# run server
/opt/cartesi/bin/logger-server -a 0.0.0.0 -d /opt/cartesi/srv/logger-server
