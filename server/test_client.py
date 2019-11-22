"""
Copyright 2019 Cartesi Pte. Ltd.

Licensed under the Apache License, Version 2.0 (the "License"); you may not use
this file except in compliance with the License. You may obtain a copy of the
License at http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed
under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from __future__ import print_function

import time
import datetime
import argparse
import grpc

import cartesi_base_pb2
import logger_high_pb2
import logger_high_pb2_grpc

SLEEP_TIME = 5
DEFAULT_ADDRESS = 'localhost'
DEFAULT_PORT = 50051
DEFAULT_MODE = 'submit'


def port_number(port):
    try:
        int_port = int(port)
        if not(0 <= int_port <= 65535):
            raise argparse.ArgumentTypeError("Please provide a valid port from 0 to 65535")
    except:
        raise argparse.ArgumentTypeError("Please provide a valid port from 0 to 65535")
    return port


def get_args():
    parser = argparse.ArgumentParser(description='GRPC test client to the logger manager server')
    parser.add_argument('--address', '-a', dest='address', default=DEFAULT_ADDRESS, help="Logger manager server address")
    parser.add_argument('--port', '-p', type=port_number, dest='port', default=DEFAULT_PORT, help="Logger manager server port")
    parser.add_argument('--mode', '-m', dest='mode', default=DEFAULT_MODE, help="Client mode can be submit or download")
    args = parser.parse_args()

    return (args.address, args.port, args.mode)


def run():
    srv_add, srv_port, mode = get_args()
    conn_str = "{}:{}".format(srv_add, srv_port)
    print("Connecting to server in " + conn_str)
    with grpc.insecure_channel(conn_str) as channel:
        stub_high = logger_high_pb2_grpc.LoggerManagerHighStub(channel)
        try:
            if mode == "submit":
                # Submit
                print("\n\nSUBMIT TESTS\n\n")

                request = logger_high_pb2.SubmitFileRequest(path="../test/test_file", page_log2_size=5, tree_log2_size=5)
                print("Asking to submit a new file")
                print("Server response:\n{}".format(stub_high.SubmitFile(request).content.hex()))
            elif mode == "download":
                # Download
                print("\n\nDOWNLOAD TESTS\n\n")

                root = cartesi_base_pb2.Hash(content=bytes.fromhex("599b88906b87ebe8c111c26198887c218de8b16a1963b9d3a0f6eb02107c4f24"))
                request = logger_high_pb2.DownloadFileRequest(path="../test/recovered_file", root=root, page_log2_size=5, tree_log2_size=8)
                print("Asking to download a new file")
                print("Server response:\n{}".format(stub_high.DownloadFile(request).path))
            else:
                raise Exception("Unknown mode")

        except Exception as e:
            print("An exception occurred:")
            print(e)
            print(type(e))


if __name__ == '__main__':
    start = time.time()
    print("Starting at {}".format(time.ctime()))
    run()
    print("Ending at {}".format(time.ctime()))
    delta = time.time() - start
    print("Took {} seconds to execute".format(datetime.timedelta(seconds=delta)))
