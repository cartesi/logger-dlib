#!/bin/sh

set -e

if [[ -n "${KEY_SEMAPHORE}" ]]; then
    # wait for key file and read from them
    echo "Waiting for key signal at ${KEY_SEMAPHORE}"
    dockerize -wait ${KEY_SEMAPHORE} -timeout ${TIMEOUT}

    if [[ -f "/opt/cartesi/etc/keys/private_key" ]]; then
        # export private key variable if file exists
        export CARTESI_CONCERN_KEY=$(cat /opt/cartesi/etc/keys/private_key)
    fi

    if [[ -f "/opt/cartesi/etc/keys/account" ]]; then
        # export account address if file exists
        export CARTESI_CONCERN_ADDRESS=$(cat /opt/cartesi/etc/keys/account)
    fi
fi

# wait for deployment
if [[ -n "${DEPLOYMENT_SEMAPHORE}" ]]; then
    echo "Waiting for deployment signal at ${DEPLOYMENT_SEMAPHORE}"
    dockerize -wait ${DEPLOYMENT_SEMAPHORE} -timeout ${TIMEOUT}
fi

# run server
/opt/cartesi/bin/logger-server $@
