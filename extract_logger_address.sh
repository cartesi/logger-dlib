#!/bin/sh
CONTRACT_KEY=`cat $1 | jq '.networks' | jq 'keys[0]' | sed 's/"//g'`
LOGGER_ADD=`cat $1 | jq ".networks[\"$CONTRACT_KEY\"].address"`
echo "Logger contract address is $LOGGER_ADD, writting to file $2"
echo $LOGGER_ADD > $2
