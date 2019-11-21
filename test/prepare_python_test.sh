#!/bin/bash

# this script will compile and migrate the contracts using truffle

# remove build directory to do a clean build
cd ../
rm ./build/ -rf
cd ./test/
truffle compile
truffle migrate --network unittests --reset

# prepare account information for the logger
### for geth dev mode ###
### geth --dev --rpc --rpcapi admin,debug,web3,eth,personal,miner,net,txpool ###
keyfile=<path of the key store>
passphrase=<passphrase of the key store>
account=`web3 account extract --keyfile "$keyfile" --password "$passphrase"`

address=`echo $account | grep address | awk -F"\: " '{print $2}'`
key=`echo $account | grep key | awk -F"\: " '{print $2}' | cut -c 3-`
export CARTESI_CONCERN_ADDRESS=$address
export CARTESI_CONCERN_KEY=$key

### for ganache ###
# export CARTESI_CONCERN_ADDRESS=<account address>
# export CARTESI_CONCERN_KEY=<account key>