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

import subprocess
import logging
import logging.config
import logging.handlers
import traceback
import grpc
import json

import core_pb2_grpc
import cartesi_base_pb2
import manager_high_pb2

LOG_FILENAME = "manager.log"
UNIX = "unix"
TCP = "tcp"
SOCKET_TYPE = UNIX

def get_new_logger(name):
    return logging.getLogger(name)

def configure_log(logger):

    logger.setLevel(logging.DEBUG)

    #Setting format
    formatter = logging.Formatter('%(asctime)s %(thread)d %(levelname)-s %(name)s %(lineno)s - %(funcName)s: %(message)s')

    #File rotation log handler
    rotating_file_handler = logging.handlers.RotatingFileHandler(
              LOG_FILENAME, maxBytes=2**20, backupCount=5)
    rotating_file_handler.setFormatter(formatter)
    rotating_file_handler.setLevel(logging.DEBUG)

    #Stream log handler
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)
    stream_handler.setFormatter(formatter)

    logger.addHandler(rotating_file_handler)
    logger.addHandler(stream_handler)

    return logger

#Initializing log
LOGGER = get_new_logger(__name__)
LOGGER = configure_log(LOGGER)
