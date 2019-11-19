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

from concurrent import futures
import time
import math
import grpc
import sys
import traceback
import argparse
import shutil
import os

#So the cartesi GRPC modules are in path
import sys
sys.path.insert(0,'../lib/grpc-interfaces/py')

import logger_high_pb2_grpc
import logger_high_pb2
import cartesi_base_pb2
import utils
from logger_registry import LoggerRegistryManager, FilePathException, HashException, NotReadyException

LOGGER = utils.get_new_logger(__name__)
LOGGER = utils.configure_log(LOGGER)

LISTENING_ADDRESS = 'localhost'
LISTENING_PORT = 50051
SLEEP_TIME = 5

class _LoggerManagerHigh(logger_high_pb2_grpc.LoggerManagerHighServicer):

    def __init__(self, logger_registry_manager):
        self.logger_registry_manager = logger_registry_manager

    def ServerShuttingDown(self, context):
        if self.logger_registry_manager.shutting_down:
            context.set_details("Server is shutting down, not accepting new requests")
            context.set_code(grpc.StatusCode.UNAVAILABLE)
            return True
        else:
            return False

    def SubmitFile(self, request, context):
        try:
            if self.ServerShuttingDown(context):
                return

            file_path = request.path
            LOGGER.info("Submit file with path: {}".format(file_path))
            
            root = self.logger_registry_manager.submit_file(file_path, request.page_log2_size, request.tree_log2_size)
            response = cartesi_base_pb2.Hash(content=bytes.fromhex(root))
            return response

        except (FilePathException, NotReadyException) as e:
            LOGGER.error(e)
            context.set_details("{}".format(e))
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
        #Generic error catch
        except Exception as e:
            LOGGER.error("An exception occurred: {}\nTraceback: {}".format(e, traceback.format_exc()))
            context.set_details('An exception with message "{}" was raised!'.format(e))
            context.set_code(grpc.StatusCode.UNKNOWN)

    def DownloadFile(self, request, context):
        try:
            if self.ServerShuttingDown(context):
                return

            root = request.root.content.hex()
            LOGGER.info("Download file with root hash: {}".format(root))

            path = self.logger_registry_manager.download_file(root, request.page_log2_size, request.tree_log2_size)
            new_path = request.path

            # move the file if is first time download
            if os.path.exists(path) and os.path.isfile(path):
                shutil.move(path, new_path)

            response = logger_high_pb2.FilePath(path=new_path)
            return response

        except (HashException, NotReadyException) as e:
            LOGGER.error(e)
            context.set_details("{}".format(e))
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
        #Generic error catch
        except Exception as e:
            LOGGER.error("An exception occurred: {}\nTraceback: {}".format(e, traceback.format_exc()))
            context.set_details('An exception with message "{}" was raised!'.format(e))
            context.set_code(grpc.StatusCode.UNKNOWN)

def serve(args):
    listening_add = args.address
    listening_port = args.port
    
    manager_address = '{}:{}'.format(listening_add, listening_port)
    logger_registry_manager = LoggerRegistryManager()
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    logger_high_pb2_grpc.add_LoggerManagerHighServicer_to_server(_LoggerManagerHigh(logger_registry_manager),
                                                      server)

    server.add_insecure_port(manager_address)
    server.start()
    LOGGER.info("Server started, listening on address {} and port {}".format(listening_add, listening_port))
    try:
        while True:
            time.sleep(SLEEP_TIME)
    except KeyboardInterrupt:
        LOGGER.info("\nIssued to shut down")

        LOGGER.debug("Acquiring logger registry global lock")
        #Acquiring lock to write on logger registry
        with logger_registry_manager.global_lock:
            LOGGER.debug("Logger registry global lock acquired")
            logger_registry_manager.shutting_down = True

        shutdown_event = server.stop(0)

        LOGGER.info("Waiting for server to stop")
        shutdown_event.wait()
        LOGGER.info("Server stopped")

if __name__ == '__main__':

    #Adding argument parser
    description = "Instantiates a logger manager server, responsible for managing and interacting with logger contract"

    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        '--address', '-a',
        dest='address',
        default=LISTENING_ADDRESS,
        help='Address to listen (default: {})'.format(LISTENING_ADDRESS)
    )
    parser.add_argument(
        '--port', '-p',
        dest='port',
        default=LISTENING_PORT,
        help='Port to listen (default: {})'.format(LISTENING_PORT)
    )
    #Getting arguments
    args = parser.parse_args()

    serve(args)
