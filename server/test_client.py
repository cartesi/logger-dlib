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

from __future__ import print_function

import time
import datetime
import argparse
import grpc

import logger_pb2
import logger_pb2_grpc

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
        stub = logger_pb2_grpc.LoggerStub(channel)
        try:
            if mode == "submit":
                # Submit
                print("\n\nSUBMIT TESTS\n\n")

                request = logger_pb2.SubmitFileRequest(path="test_file", page_log2_size=10, tree_log2_size=20)
                print("Asking to submit a new file")
                response = stub.SubmitFile(request)
                print("Server response root:\n{}".format(response.root.content.hex()))
                print("Server response status:\n{}".format(response.status))
                print("Server response progress:\n{}".format(response.progress))
            elif mode == "download":
                # Download
                print("\n\nDOWNLOAD TESTS\n\n")

                root = logger_pb2.Hash(content=bytes.fromhex("9a8d49468b9592705f608525928c3e53771c176da25f84f78dec7433a3416bea"))
                request = logger_pb2.DownloadFileRequest(path="recovered_file", root=root, page_log2_size=10, tree_log2_size=20)
                print("Asking to download a new file")
                response = stub.DownloadFile(request)
                print("Server response path:\n{}".format(response.path))
                print("Server response status:\n{}".format(response.status))
                print("Server response progress:\n{}".format(response.progress))
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
