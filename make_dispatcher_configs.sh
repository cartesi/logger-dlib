users=`cat ./blockchain_files/wallets.yaml | grep address | awk -F\' '{print $2}'`
count=0
for user in $users; do
    python3 dispatcher_config_generator.py -ua $user -o dispatcher_config_${count}.yaml
    count=$((count + 1))
done
