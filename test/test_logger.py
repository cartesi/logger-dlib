# Copyright (C) 2020 Cartesi Pte. Ltd.

# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.

# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE. See the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# Note: This component currently has dependencies that are licensed under the GNU
# GPL, version 3, and so you should treat this component as a whole as being under
# the GPL version 3. But all Cartesi-written code in this component is licensed
# under the Apache License, version 2, or a compatible permissive license, and can
# be used independently under the Apache v2 license. After this component is
# rewritten, the entire component will be released under the Apache v2 license.

import sys
import json
import filecmp
import logger
from web3.auto import w3

sys.path.append('../logger/')
from logger import Logger

# start of main test

fname = '../deployments/localhost/Logger.json'
with open(fname) as json_file:
    logger_data = json.load(json_file)

networkId = w3.net.version
print("Getting Logger contract address for network {} from {}".format(networkId, fname))
deployed_address = logger_data['address']
print("Using Logger({}) at network {}".format(deployed_address, networkId))

test_logger = Logger(w3, deployed_address, logger_data['abi'], 5)
page_log2_size = 5
test_logger.instantiate(page_log2_size, page_log2_size)

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

page_log2_size = 6
test_logger.instantiate(page_log2_size, page_log2_size)

# test case 4 with auto padding
data = []
data.append(bytes("est95192", 'utf-8'))
data.append(bytes("51e5q1w9", 'utf-8'))
data.append(bytes("54sd984s", 'utf-8'))
data.append(bytes("df5a1ste", 'utf-8'))

(index_4, root) = test_logger.submit_data_to_logger(data)
assert root == bytes.fromhex("ae0df637400a5b2c22b21f6280214266fea45cd3cf58e7830a0d721662c5c946"), "Hashes not match"
print("Test case 4 passed!")

# test case 5

padded_data = data
for _ in range(4):
    padded_data.append(bytes(8))

(suc, recovered_data) = test_logger.recover_data_from_root(root)

assert suc, "Recover should succeed"
assert padded_data == recovered_data, "Recovered data should include padded zeros"
print("Test case 5 passed!")

# test case 6
indices = []
indices.append(index_4)
indices.append(index_4)

(index_6, root) = test_logger.submit_indices_to_logger(page_log2_size, indices)
assert root == bytes.fromhex("3ce0972884faae1df9a367972dc9ac262a2302306d9e51d627545775422b0793"), "Hashes not match"
print("Test case 6 passed!")

# test case 7

padded_data += padded_data

(suc, recovered_data) = test_logger.recover_data_from_root(root)

assert suc, "Recover should succeed"
assert padded_data == recovered_data, "Recovered data should include padded zeros"
print("Test case 7 passed!")

# test case 8
page_log2_size = 10
tree_log2_size = 20
test_logger.instantiate(page_log2_size, tree_log2_size)

input_file = "test_file"
output_file = "recovered_file"

root = test_logger.submit_file(input_file)
test_logger.download_file(root, output_file)

assert filecmp.cmp(input_file, output_file), "Files not match"
print("Test case 8 passed!")

page_log2_size = 3
test_logger.instantiate(page_log2_size, page_log2_size)

# test case 9
data = []
data.append(bytes("est9", 'utf-8'))

(index_3, root) = test_logger.submit_data_to_logger(data)

assert root == bytes.fromhex("c6ec4bd96e806e3794cb2c7de51c7e7c4dd319ef734557ed6b5cbe25358e5829"), "Hashes not match"
print("Test case 9 passed!")

# test case 10
indices = []
indices.append(index_3)
indices.append(index_3)
indices.append(index_3)
indices.append(index_3)

(index_3, root) = test_logger.submit_indices_to_logger(page_log2_size, indices)

assert root == bytes.fromhex("0db5d1146b631e9bf1c3f769485ad74e75225a67a02154ce8add7ac9f8a67274"), "Hashes not match"
print("Test case 10 passed!")

# test case 11
page_log2_size = 8
tree_log2_size = 20
test_logger.instantiate(page_log2_size, tree_log2_size)

input_file = "test_file"
output_file = "recovered_file"

root = test_logger.submit_file(input_file)
test_logger.download_file(root, output_file)

assert filecmp.cmp(input_file, output_file), "Files not match"
print("Test case 11 passed!")

page_log2_size = 10
tree_log2_size = 20
test_logger.instantiate(page_log2_size, tree_log2_size)

# test case 12
input_file = "0-00.json.br.tar"
root = test_logger.submit_file(input_file)

assert root == bytes.fromhex("cd9665e5ea391d134dfbe45ca04a55ef8adf164dbc4c40ad31ae185f8f1af923"), "Hashes not match"
print("Test case 12 passed!")

# test case 13
input_file = "0-01.json.br.tar"
root = test_logger.submit_file(input_file)

assert root == bytes.fromhex("117fea97b997fe7e3b85dc5783aa161001c325a7e95a297c8668e087a70c282a"), "Hashes not match"
print("Test case 13 passed!")

# test case 14
input_file = "0-02.json.br.tar"
root = test_logger.submit_file(input_file)

assert root == bytes.fromhex("296833044d8a51958bf4eb4e3f20c4d070a1a96b8dbc31d7ca771c999391a8af"), "Hashes not match"
print("Test case 14 passed!")

# test case 15
input_file = "0-03.json.br.tar"
root = test_logger.submit_file(input_file)

assert root == bytes.fromhex("f188e44f55b7f05c2b746d88670f7c4c8d3728626bcaf4859cfd35a3b903f313"), "Hashes not match"
print("Test case 15 passed!")

# test case 16
input_file = "0-04.json.br.tar"
root = test_logger.submit_file(input_file)

assert root == bytes.fromhex("655382e190b6cf44f0df8a8cd97331a63e9b7c678d0a4c783fb3a176a27f5f3e"), "Hashes not match"
print("Test case 16 passed!")

# test case 17
input_file = "0-05.json.br.tar"
root = test_logger.submit_file(input_file)

assert root == bytes.fromhex("bf7fc30e5e81cc99adc3c4abcd28c8ebcd84b75314011a9cb5d331361e7782ab"), "Hashes not match"
print("Test case 17 passed!")

# test case 18
input_file = "0-06.json.br.tar"
root = test_logger.submit_file(input_file)

assert root == bytes.fromhex("3fb2f3a2da3b7016648e91f04ef78ccd5c8ac8c471bc0f2f7cf7c9517f653ce7"), "Hashes not match"
print("Test case 18 passed!")

# test case 19
input_file = "0-07.json.br.tar"
root = test_logger.submit_file(input_file)

assert root == bytes.fromhex("bff9861e078c0edaf8d7d0f164e6582d7926bc5e7c9248a95eb3d2a38bb7f0b5"), "Hashes not match"
print("Test case 19 passed!")

page_log2_size = 10
tree_log2_size = 20
test_logger.instantiate(page_log2_size, tree_log2_size)

root = bytes.fromhex("cd9665e5ea391d134dfbe45ca04a55ef8adf164dbc4c40ad31ae185f8f1af923")
output_file = "0-00.json.br.tar.download"

test_logger.download_file(root, output_file)
print("Test case 20 passed!")

root = bytes.fromhex("117fea97b997fe7e3b85dc5783aa161001c325a7e95a297c8668e087a70c282a")
output_file = "0-01.json.br.tar.download"

test_logger.download_file(root, output_file)
print("Test case 21 passed!")

root = bytes.fromhex("296833044d8a51958bf4eb4e3f20c4d070a1a96b8dbc31d7ca771c999391a8af")
output_file = "0-02.json.br.tar.download"

test_logger.download_file(root, output_file)
print("Test case 22 passed!")

root = bytes.fromhex("f188e44f55b7f05c2b746d88670f7c4c8d3728626bcaf4859cfd35a3b903f313")
output_file = "0-03.json.br.tar.download"

test_logger.download_file(root, output_file)
print("Test case 23 passed!")

root = bytes.fromhex("655382e190b6cf44f0df8a8cd97331a63e9b7c678d0a4c783fb3a176a27f5f3e")
output_file = "0-04.json.br.tar.download"

test_logger.download_file(root, output_file)
print("Test case 24 passed!")

root = bytes.fromhex("bf7fc30e5e81cc99adc3c4abcd28c8ebcd84b75314011a9cb5d331361e7782ab")
output_file = "0-05.json.br.tar.download"

test_logger.download_file(root, output_file)
print("Test case 25 passed!")

root = bytes.fromhex("3fb2f3a2da3b7016648e91f04ef78ccd5c8ac8c471bc0f2f7cf7c9517f653ce7")
output_file = "0-06.json.br.tar.download"

test_logger.download_file(root, output_file)
print("Test case 26 passed!")

root = bytes.fromhex("bff9861e078c0edaf8d7d0f164e6582d7926bc5e7c9248a95eb3d2a38bb7f0b5")
output_file = "0-07.json.br.tar.download"

test_logger.download_file(root, output_file)
print("Test case 27 passed!")

# end of test
print("All tests passed!")
