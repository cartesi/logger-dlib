# Copyright 2019 Cartesi Pte. Ltd.

# Licensed under the Apache License, Version 2.0 (the "License"); you may not use
# this file except in compliance with the License. You may obtain a copy of the
# License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

import sys
sys.path.append('./logger/')
import json
import filecmp
from logger import Logger

# start of main

if len(sys.argv) != 3:
    print("Usage: python simple_logger.py submit <file_path>,")
    print("Or: python simple_logger.py download <root hash>")
    sys.exit(1)

with open('./build/contracts/Logger.json') as json_file:
    logger_data = json.load(json_file)

with open('./test/deployedAddresses.json') as json_file:
    deployed_address = json.load(json_file)

# TODO: Make endpoint and page_log2_size tree_log2_size configurable
test_logger = Logger("http://127.0.0.1:8545", deployed_address["logger_address"], logger_data['abi'])
# change this to automatic way
test_logger.instantiate(2, 5)

if (sys.argv[1] == "download"):

    test_logger.download_file(bytes.fromhex(sys.argv[2]), sys.argv[2] + ".download")

elif (sys.argv[1] == "submit"):

    root = test_logger.submit_file(sys.argv[2])
    with open(sys.argv[2] + ".submit", "w") as f:
        f.write(root.hex())
else:
    assert False, "Unknown command"