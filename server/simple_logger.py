# Copyright 2019 Cartesi Pte. Ltd.

# Licensed under the Apache License, Version 2.0 (the "License"); you may not use
# this file except in compliance with the License. You may obtain a copy of the
# License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

import os
import json
import argparse
from web3.auto import w3

from logger import Logger, DEFAULT_CONTRACT_PATH, DEFAULT_DATA_DIR

# Adding argument parser
description = "A simple script to interact with Logger contract"

parser = argparse.ArgumentParser(description=description)
parser.add_argument(
    '--action', '-a',
    dest='action',
    default="none",
    help='Download mode download/submit (default: {})'.format("none")
    )
parser.add_argument(
    '--param', '-p',
    dest='param',
    default="",
    help='The file path or root hash for Logger action'
    )
parser.add_argument(
    '--blob_log2_size', '-b',
    dest='blob_log2_size',
    type=int,
    required=True,
    help='The blob log2 size of the Logger'
    )
parser.add_argument(
    '--tree_log2_size', '-t',
    dest='tree_log2_size',
    type=int,
    required=True,
    help='The tree log2 size of the Logger'
    )
parser.add_argument(
    '--data_dir', '-d',
    dest='data_directory',
    default=DEFAULT_DATA_DIR,
    help='Data directory for files (default: {})'.format(DEFAULT_DATA_DIR)
    )
parser.add_argument(
    '--contract_path', '-c',
    dest='contract_path',
    default=DEFAULT_CONTRACT_PATH,
    help='Path for contract json file in truffle format (default: {})'.format(DEFAULT_CONTRACT_PATH)
)

# Getting arguments
args = parser.parse_args()

with open(args.contract_path) as json_file:
    logger_data = json.load(json_file)
    logger_abi = logger_data['abi']
    networkId = w3.net.version
    deployed_address = logger_data['networks'][networkId]['address']

test_logger = Logger(w3, deployed_address, logger_abi)
# change this to automatic way
test_logger.instantiate(args.blob_log2_size, args.tree_log2_size)

path = os.path.join(args.data_directory, "{}.{}".format(args.param, args.action))

if args.action == "download":

    test_logger.download_file(bytes.fromhex(args.param), path)

elif args.action == "submit":

    root = test_logger.submit_file(args.param)
    with open(path, "w") as f:
        f.write(root.hex())
else:
    assert False, "No action given"
