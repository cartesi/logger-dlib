# Copyright 2019 Cartesi Pte. Ltd.

# Licensed under the Apache License, Version 2.0 (the "License"); you may not use
# this file except in compliance with the License. You may obtain a copy of the
# License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

import sys
import json
import filecmp
from web3.auto import w3

sys.path.append('../logger/')
from logger import Logger

# start of main test

fname = '../build/contracts/Logger.json'
with open(fname) as json_file:
    logger_data = json.load(json_file)

networkId = w3.net.version
print("Getting Logger contract address for network {} from {}".format(networkId, fname))
assert networkId in logger_data['networks'], "Network " + networkId + " not found in " + fname
deployed_address = logger_data['networks'][networkId]['address']
print("Using Logger({}) at network {}".format(deployed_address, networkId))

# TODO: Make endpoint and page_log2_size tree_log2_size configurable
test_logger = Logger(w3, deployed_address, logger_data['abi'])
page_log2_size = 2
tree_log2_size = 5
test_logger.instantiate(page_log2_size, tree_log2_size)

# test case 1
data = []
data.append(bytes("est95192", 'utf-8'))
data.append(bytes("51e5q1w9", 'utf-8'))
data.append(bytes("54sd984s", 'utf-8'))
data.append(bytes("df5a1ste", 'utf-8'))

(index_1, root) = test_logger.submit_data_to_logger(data)

assert root == bytes.fromhex("41635d7ab5ba446d0ffa701662a60aec0709b0f778f15745a631d070ccfa90f4"), "Hashes not match"
print("Test case 1 passed!")

# test case 2
data = []
data.append(bytes("st951925", 'utf-8'))
data.append(bytes("1e5sdqsa", 'utf-8'))
data.append(bytes("12325245", 'utf-8'))
data.append(bytes("99541234", 'utf-8'))

(index_2, root) = test_logger.submit_data_to_logger(data)

assert root == bytes.fromhex("3a908ab397101eeb698596301f50dbee1c20ec57989bf5d3f87f71eafe55730a"), "Hashes not match"
print("Test case 2 passed!")

# test case 3
indices = []
indices.append(index_1)
indices.append(index_2)
indices.append(index_1)
indices.append(index_2)
indices.append(index_1)
indices.append(index_2)
indices.append(index_1)
indices.append(index_2)

(index_3, root) = test_logger.submit_indices_to_logger(page_log2_size, indices)

assert root == bytes.fromhex("599b88906b87ebe8c111c26198887c218de8b16a1963b9d3a0f6eb02107c4f24"), "Hashes not match"
print("Test case 3 passed!")

# test case 4
input_file = "test_file"
output_file = "recovered_file"

root = test_logger.submit_file(input_file)
test_logger.download_file(root, output_file)

assert filecmp.cmp(input_file, output_file), "Files not match"
print("Test case 4 passed!")

page_log2_size = 3
test_logger.instantiate(page_log2_size, tree_log2_size)

# test case 5
data = []
data.append(bytes("est95192", 'utf-8'))
data.append(bytes("51e5q1w9", 'utf-8'))
data.append(bytes("54sd984s", 'utf-8'))
data.append(bytes("df5a1ste", 'utf-8'))
data.append(bytes("st951925", 'utf-8'))
data.append(bytes("1e5sdqsa", 'utf-8'))
data.append(bytes("12325245", 'utf-8'))
data.append(bytes("99541234", 'utf-8'))

(index_3, root) = test_logger.submit_data_to_logger(data)

assert root == bytes.fromhex("2bf37c10b1fd8c140f259f4fbbc5a6cc090cffd7edc7e4b8a4e53db7020876b6"), "Hashes not match"
print("Test case 5 passed!")

# test case 6
indices = []
indices.append(index_3)
indices.append(index_3)
indices.append(index_3)
indices.append(index_3)

(index_3, root) = test_logger.submit_indices_to_logger(page_log2_size, indices)

assert root == bytes.fromhex("599b88906b87ebe8c111c26198887c218de8b16a1963b9d3a0f6eb02107c4f24"), "Hashes not match"
print("Test case 6 passed!")

# test case 7
input_file = "test_file"
output_file = "recovered_file"

root = test_logger.submit_file(input_file)
test_logger.download_file(root, output_file)

assert filecmp.cmp(input_file, output_file), "Files not match"
print("Test case 7 passed!")

page_log2_size = 7
tree_log2_size = 17
test_logger.instantiate(page_log2_size, tree_log2_size)

# test case 8
input_file = "0-00.json.br.tar"
root = test_logger.submit_file(input_file)

assert root == bytes.fromhex("cd9665e5ea391d134dfbe45ca04a55ef8adf164dbc4c40ad31ae185f8f1af923"), "Hashes not match"
print("Test case 8 passed!")

# test case 9
input_file = "0-01.json.br.tar"
root = test_logger.submit_file(input_file)

assert root == bytes.fromhex("117fea97b997fe7e3b85dc5783aa161001c325a7e95a297c8668e087a70c282a"), "Hashes not match"
print("Test case 9 passed!")

# test case 10
input_file = "0-02.json.br.tar"
root = test_logger.submit_file(input_file)

assert root == bytes.fromhex("296833044d8a51958bf4eb4e3f20c4d070a1a96b8dbc31d7ca771c999391a8af"), "Hashes not match"
print("Test case 10 passed!")

# test case 11
input_file = "0-03.json.br.tar"
root = test_logger.submit_file(input_file)

assert root == bytes.fromhex("f188e44f55b7f05c2b746d88670f7c4c8d3728626bcaf4859cfd35a3b903f313"), "Hashes not match"
print("Test case 11 passed!")

# test case 12
input_file = "0-04.json.br.tar"
root = test_logger.submit_file(input_file)

assert root == bytes.fromhex("655382e190b6cf44f0df8a8cd97331a63e9b7c678d0a4c783fb3a176a27f5f3e"), "Hashes not match"
print("Test case 12 passed!")

# test case 13
input_file = "0-05.json.br.tar"
root = test_logger.submit_file(input_file)

assert root == bytes.fromhex("bf7fc30e5e81cc99adc3c4abcd28c8ebcd84b75314011a9cb5d331361e7782ab"), "Hashes not match"
print("Test case 13 passed!")

# test case 14
input_file = "0-06.json.br.tar"
root = test_logger.submit_file(input_file)

assert root == bytes.fromhex("3fb2f3a2da3b7016648e91f04ef78ccd5c8ac8c471bc0f2f7cf7c9517f653ce7"), "Hashes not match"
print("Test case 14 passed!")

# test case 15
input_file = "0-07.json.br.tar"
root = test_logger.submit_file(input_file)

assert root == bytes.fromhex("bff9861e078c0edaf8d7d0f164e6582d7926bc5e7c9248a95eb3d2a38bb7f0b5"), "Hashes not match"
print("Test case 15 passed!")

# end of test
print("All tests passed!")
