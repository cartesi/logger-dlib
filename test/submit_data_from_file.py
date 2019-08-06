import os
import sys
import json
from web3 import Web3
from solcx import install_solc
from solcx import get_solc_version, set_solc_version, compile_files

def bytes_from_file(filename, chunksize):
    with open(filename, "rb") as f:
        while True:
            chunk = f.read(chunksize)
            if chunk:
                yield chunk
            else:
                break
                        
def submit_indices_to_da(w3, indices):

    try:
        tx_hash = da.functions.calculateMerkleRootFromHistory(page_log_2_size, indices).transact({'from': w3.eth.coinbase, 'gas': 6283185})
        tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
        if tx_receipt['status'] == 0:
            raise ValueError(receipt['transactionHash'].hex())
        merkle_filter = da.events.MerkleRootCalculatedFromHistory.createFilter(fromBlock='latest')
        merkle_root = merkle_filter.get_all_entries()[0]['args']['_root']
        merkle_log2 = merkle_filter.get_all_entries()[0]['args']['_log2Size']
        merkle_indices = merkle_filter.get_all_entries()[0]['args']['_indices']
        merkle_index = merkle_filter.get_all_entries()[0]['args']['_index']
        print("root is: " + merkle_root.hex())
        print("log2 is: " + str(merkle_log2))
        print("indices is: " + str(merkle_indices))
        print("index in the history is: " + str(merkle_index))
        return merkle_index
    except ValueError as e:
        print("calculateMerkleRoot REVERT transaction: " + str(e))
                        
def submit_data_to_da(w3, data):

    try:
        tx_hash = da.functions.calculateMerkleRootFromData(page_log_2_size, data).transact({'from': w3.eth.coinbase, 'gas': 6283185})
        tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
        if tx_receipt['status'] == 0:
            raise ValueError(receipt['transactionHash'].hex())
        merkle_filter = da.events.MerkleRootCalculatedFromData.createFilter(fromBlock='latest')
        merkle_root = merkle_filter.get_all_entries()[0]['args']['_root']
        merkle_log2 = merkle_filter.get_all_entries()[0]['args']['_log2Size']
        merkle_data = merkle_filter.get_all_entries()[0]['args']['_data']
        merkle_index = merkle_filter.get_all_entries()[0]['args']['_index']
        print("root is: " + merkle_root.hex())
        print("log2 is: " + str(merkle_log2))
        print("data is: " + str(merkle_data))
        print("index in the history is: " + str(merkle_index))
        return merkle_index
    except ValueError as e:
        print("calculateMerkleRoot REVERT transaction: " + str(e))
        
def submit_file_to_da(w3, filename):

    data = []
    indices = []
    count = 2**(tree_log_2_size - page_log_2_size)
    for b in bytes_from_file(filename, bytes_of_word):
        data.append(b)
        if(len(data) == page_size):
            index = submit_data_to_da(w3, data)
            indices.append(index)
            data = []
            count -= 1

    if(len(data) != 0):
        index = submit_data_to_da(w3, data)
        indices.append(index)
        count -= 1

    data = []
    for x in range(page_size):
        data.append(bytes(bytes_of_word))

    while(count > 0):
        index = submit_data_to_da(w3, data)
        indices.append(index)
        count -= 1

    if(len(indices) > 1):
        submit_indices_to_da(w3, indices)


# start of main test
if len(sys.argv) != 2:
    print("Usage: python test_merkle_root.py <file path>")
    sys.exit(1)

page_log_2_size = 3
tree_log_2_size = 4
bytes_of_word = 8
page_size = 2**page_log_2_size
tree_size = 2**tree_log_2_size

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

submit_file_to_da(w3, sys.argv[1])
#test_merkle_root_from_data(w3)
#test_merkle_root_from_history(w3)
