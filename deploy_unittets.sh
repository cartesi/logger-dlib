#!/bin/bash

# this script will compile and migrate the contracts using truffle
truffle compile
truffle migrate --network unittests --reset