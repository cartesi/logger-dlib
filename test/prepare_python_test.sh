#!/bin/bash

# this script will compile and migrate the contracts using truffle

# remove build directory to do a clean build
cd ../
rm ./build/ -rf
cd ./test/
truffle compile
truffle migrate --network unittests --reset
