# Copyright 2019 Cartesi Pte. Ltd.

# Licensed under the Apache License, Version 2.0 (the "License"); you may not use
# this file except in compliance with the License. You may obtain a copy of the
# License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

import sys
sys.path.append('../logger/')
import json
from logger import Logger
import yaml
import argparse

#Adding argument parser
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
    '--url', '-u',
    dest='url',
    default="127.0.0.1:8545",
    help='Url of the blockchain (default: {})'.format("127.0.0.1:8545")
)

#Getting arguments
args = parser.parse_args()

with open('../blockchain_files/Logger.json') as json_file:
    logger_abi = json.load(json_file)['abi']

with open('../blockchain_files/deployed_contracts.yaml') as deployed_file:
    deployed_address = yaml.safe_load(deployed_file)["Logger"]

blockchain_url = "http://{}".format(args.url)

# TODO: Make endpoint and page_log2_size tree_log2_size configurable
test_logger = Logger(blockchain_url, deployed_address, logger_abi)
# change this to automatic way
test_logger.instantiate(2, 5)

if (args.action == "download"):

    test_logger.download_file(bytes.fromhex(args.param), args.param + ".download")

elif (args.action == "submit"):

    root = test_logger.submit_file(args.param)
    with open(args.param + ".submit", "w") as f:
        f.write(root.hex())
else:
    assert False, "No action given"