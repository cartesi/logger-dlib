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
    help='Path for contract json file in buidler format (default: {})'.format(DEFAULT_CONTRACT_PATH)
)

# Getting arguments
args = parser.parse_args()

with open(args.contract_path) as json_file:
    logger_data = json.load(json_file)
    logger_abi = logger_data['abi']
    deployed_address = logger_data['address']

test_logger = Logger(w3, deployed_address, logger_abi, 5)
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
