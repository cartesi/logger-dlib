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

import grpc
import sys
import os
import time
import datetime
import json

#So the cartesi GRPC modules are in path
import sys
sys.path.insert(0,'../lib/grpc-interfaces/py')

import core_pb2
import cartesi_base_pb2
import core_pb2_grpc
import logger_high_pb2
import logger_high_pb2_grpc
import traceback
import argparse
#from IPython import embed

SLEEP_TIME = 5
DEFAULT_PORT = 50051
DEFAULT_ADD = 'localhost'
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
    parser.add_argument('--address', '-a', dest='address', default=DEFAULT_ADD, help="Logger manager server address")
    parser.add_argument('--port', '-p', type=port_number, dest='port', default=DEFAULT_PORT, help="Logger manager server port")
    parser.add_argument('--container', '-c', action="store_true", dest="container_server", help="Fixes file references for when logger manager server is running from docker container")
    parser.add_argument('--mode', '-m', dest='mode', default=DEFAULT_MODE, help="Client mode can be submit or download")
    args = parser.parse_args()

    global CONTAINER_SERVER
    CONTAINER_SERVER = args.container_server

    return (args.address, args.port, args.mode)

def run():
    responses = []
    srv_add, srv_port, mode = get_args()
    conn_str = "{}:{}".format(srv_add, srv_port)
    print("Connecting to server in " + conn_str)
    with grpc.insecure_channel(conn_str) as channel:
        stub_high = logger_high_pb2_grpc.LoggerManagerHighStub(channel)
        try:
            if mode == "submit":
                #Submit
                print("\n\n\SUBMIT TESTS\n\n\n")

                request = logger_high_pb2.FilePath(path="../submits_and_downloads/test_file")
                print("Asking to submit a new file")
                print("Server response:\n{}".format(stub_high.SubmitFile(request).content.hex()))
            elif mode == "download":
                #Download
                print("\n\n\DOWNLOAD TESTS\n\n\n")

                request = cartesi_base_pb2.Hash(content=bytes.fromhex("599b88906b87ebe8c111c26198887c218de8b16a1963b9d3a0f6eb02107c4f24"))
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
