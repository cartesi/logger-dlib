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

from concurrent import futures
import time
import argparse
import shutil
import os
import logging
import logging.config
import logging.handlers
import grpc

import logger_high_pb2_grpc
import logger_high_pb2
import cartesi_base_pb2
from logger_registry import LoggerRegistryManager
from logger import DEFAULT_CONTRACT_PATH, DEFAULT_DATA_DIR

LISTENING_ADDRESS = 'localhost'
LISTENING_PORT = 50051
SLEEP_TIME = 5

LOGGER = logging.getLogger(__name__)

# status: 0 -> finished successfully
#         1 -> working on it, not ready yet
#         2 -> invalid argument
#         3 -> service not available, shutting down   

class _LoggerManagerHigh(logger_high_pb2_grpc.LoggerManagerHighServicer):

    def __init__(self, logger_registry_manager):
        self.logger_registry_manager = logger_registry_manager

    def ServerShuttingDown(self, context):
        if self.logger_registry_manager.shutting_down:
            context.set_details("Server is shutting down, not accepting new requests")
            context.set_code(grpc.StatusCode.UNAVAILABLE)
            return True
        return False

    def SubmitFile(self, request, context):
        try:
            if self.ServerShuttingDown(context):
                return logger_high_pb2.SubmitFileResponse(status=3)

            file_path = request.path
            LOGGER.info("Submit file with path: %s", file_path)

            (root, status, progress) = self.logger_registry_manager.submit_file(file_path, request.page_log2_size, request.tree_log2_size)
            return logger_high_pb2.SubmitFileResponse(root=cartesi_base_pb2.Hash(content=bytes.fromhex(root)), status=status, progress=progress)

        # Generic error catch
        except Exception as e:
            context.set_details('An exception with message "{}" was raised!'.format(e))
            context.set_code(grpc.StatusCode.UNKNOWN)
            raise e

    def DownloadFile(self, request, context):
        try:
            if self.ServerShuttingDown(context):
                return logger_high_pb2.DownloadFileResponse(status=3)

            root = request.root.content.hex()
            LOGGER.info("Download file with root hash: %s", root)

            (path, status, progress) = self.logger_registry_manager.download_file(root, request.page_log2_size, request.tree_log2_size)
            new_path = os.path.join(self.logger_registry_manager.data_dir, request.path)

            # move the file if is first time download
            if os.path.exists(path) and os.path.isfile(path):
                shutil.move(path, new_path)

            if os.path.exists(new_path) and os.path.isfile(new_path):
                return logger_high_pb2.DownloadFileResponse(path=new_path, status=status, progress=progress)

            return logger_high_pb2.DownloadFileResponse(path=path, status=status, progress=progress)

        # Generic error catch
        except Exception as e:
            context.set_details('An exception with message "{}" was raised!'.format(e))
            context.set_code(grpc.StatusCode.UNKNOWN)
            raise e


def configure_log():
    # Setting formatter
    formatter = logging.Formatter(
        '%(asctime)s %(thread)d %(levelname)-s %(name)s %(lineno)s - %(funcName)s: %(message)s')

    # Stream log handler
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)
    stream_handler.setFormatter(formatter)

    # Configuring root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(stream_handler)


def check_data_directory(directory):
    data_dir = os.path.realpath(os.path.expanduser(os.path.expandvars(directory)))
    if not os.path.exists(data_dir):
        raise FileNotFoundError("Data directory doesn't exist: {}".format(directory))
    if not os.path.isdir(data_dir):
        raise NotADirectoryError("Data path is not a directory: {}".format(directory))
    if not os.access(data_dir, os.W_OK):
        raise PermissionError("Cannot write to Data directory: {}".format(directory))
    return data_dir


def serve(arguments):
    configure_log()

    data_dir = check_data_directory(arguments.data_directory)

    # TODO: include a validation for the contract file
    logger_registry_manager = LoggerRegistryManager(data_dir, arguments.contract_path)
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    logger_high_pb2_grpc.add_LoggerManagerHighServicer_to_server(_LoggerManagerHigh(logger_registry_manager), server)

    LOGGER.info("Starting Server at %s:%s", arguments.address, arguments.port)
    server.add_insecure_port('{}:{}'.format(arguments.address, arguments.port))
    server.start()
    LOGGER.info("Server started successfully")
    try:
        while True:
            time.sleep(SLEEP_TIME)
    except KeyboardInterrupt:
        LOGGER.info("\nIssued to shut down")

        LOGGER.debug("Acquiring logger registry global lock")
        # Acquiring lock to write on logger registry
        with logger_registry_manager.global_lock:
            LOGGER.debug("Logger registry global lock acquired")
            logger_registry_manager.shutting_down = True

        shutdown_event = server.stop(0)

        LOGGER.info("Waiting for server to stop")
        shutdown_event.wait()
        LOGGER.info("Server stopped")


if __name__ == '__main__':

    # Adding argument parser
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

    serve(parser.parse_args())
