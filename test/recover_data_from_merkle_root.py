import os
import sys
import json
from web3 import Web3
from solcx import install_solc
from solcx import get_solc_version, set_solc_version, compile_files

def recover_data_from_root(w3, root):

    try:
        merkle_filter = da.events.MerkleRootCalculatedFromData.createFilter(fromBlock=0, argument_filters={'_root':root})

        if(not len(merkle_filter.get_all_entries()) == 0):
            return (True, merkle_filter.get_all_entries()[0]['args']['_data'])
        
        data = []
        merkle_filter = da.events.MerkleRootCalculatedFromHistory.createFilter(fromBlock=0, argument_filters={'_root':root})

        if(not len(merkle_filter.get_all_entries()) == 0):
            for index in merkle_filter.get_all_entries()[0]['args']['_indices']:

                retrieve_filter = da.events.MerkleRootCalculatedFromData.createFilter(fromBlock=0, argument_filters={'_index':index})
                if(len(retrieve_filter.get_all_entries()) == 0):
                    retrieve_filter = da.events.MerkleRootCalculatedFromHistory.createFilter(fromBlock=0, argument_filters={'_index':index})
                root_at_index = retrieve_filter.get_all_entries()[0]['args']['_root']

                (ret_at_index, data_at_index) = recover_data_from_root(w3, root_at_index)
                data += data_at_index

            return (True, data)
        return (False, [])

    except ValueError as e:
        print(str(e))

# start of main test

if len(sys.argv) != 2:
    print("Usage: python recover_data_from_merkle_root.py <root hash>")
    sys.exit(1)

#Connecting to node
endpoint = "http://127.0.0.1:8545"
w3 = Web3(Web3.HTTPProvider(endpoint, request_kwargs={'timeout': 60}))

if (not w3.isConnected()):
    print("Couldn't connect to node, exiting")
    sys.exit(1)

with open('../build/contracts/DataAvailability.json') as json_file:
    da_data = json.load(json_file)

with open('./deployedAddresses.json') as json_file:
    deployedAddresses = json.load(json_file)

da = w3.eth.contract(address=deployedAddresses["da_address"], abi=da_data['abi'])

(succ, data) = recover_data_from_root(w3, bytes.fromhex(sys.argv[1]))

if(succ):
    print("data is: " + str(data))
    with open("recover_file", "wb") as f:
        for b in data:
            f.write(b)
else:
    # TODO: output data to a file
    print("The Merkle root is not found in the DataAvailability history")
