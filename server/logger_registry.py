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

from threading import Lock
from concurrent import futures
import subprocess
import logging
import os

import json
from web3.auto import w3
from logger import Logger

LOGGER = logging.getLogger(__name__)
ZERO_HASH = "0000000000000000000000000000000000000000000000000000000000000000"


class LoggerStatus:

    def __init__(self, result_path, logger_if, job):
        self.result_path = result_path
        self.logger_if = logger_if
        self.job = job


def valid_file(path):
    return os.path.exists(path) and os.path.isfile(path)


class LoggerRegistryManager:

    def __init__(self, directory, contract_path):
        if directory is None:
            raise ValueError()
        self.data_dir = directory
        self.contract_path = contract_path
        self.global_lock = Lock()
        self.registry = {}
        self.shutting_down = False
        self.executor = futures.ThreadPoolExecutor(max_workers=10)

    def submit_file(self, filename, page_log2_size, tree_log2_size):

        basename = os.path.basename(filename)
        if not basename:
            # root, status, progress
            return (ZERO_HASH, 2, 0, "Base name not found")

        file_path = os.path.join(self.data_dir, basename)
        if not valid_file(file_path):
            # root, status, progress
            return (ZERO_HASH, 2, 0, "Invalid file path error")

        (is_ready, result_path, progress) = self.register_action("submit", file_path, page_log2_size, tree_log2_size)

        if not is_ready:
            # root, status, progress
            return (ZERO_HASH, 1, progress, "Submission in progress")

        with open(result_path, "r") as f:
            # root, status, progress
            return (f.readline(), 0, progress, "Submission done")

    def download_file(self, root, page_log2_size, tree_log2_size):

        (is_ready, result_path, progress) = self.register_action("download", root, page_log2_size, tree_log2_size)

        if not is_ready:
            # path, status, progress
            return ("", 1, progress, "Download in progress")

        return (result_path, 0, progress, "Download done")

    """
    Here starts the "internal" API, use the methods bellow taking the right precautions such as holding a lock
    """

    def register_action(self, action, key, page_log2_size, tree_log2_size):

        result_path = os.path.join(self.data_dir, "{}.{}".format(key, action))
        # Acquiring global lock and releasing it when completed
        LOGGER.debug("Acquiring registry %s global lock", action)
        with self.global_lock:
            LOGGER.debug("Lock acquired")
            if key in self.registry.keys():
                # already contains the request of key
                if self.registry[key].job is not None and self.registry[key].job.done():
                    if self.registry[key].job.result():
                        if action == "submit":
                            root = self.registry[key].job.result()
                            with open(result_path, "w") as f:
                                f.write(root.hex())

                        self.registry[key].job = None
                        self.registry[key].logger_if = None
                        return (True, result_path, 100)
                    else:
                        LOGGER.error("Logger failed to complete task")

                if valid_file(result_path):
                    return (True, result_path, 100)

                if self.registry[key].logger_if:
                    progress = 0
                    if action == "submit":
                        progress = self.registry[key].logger_if.get_submission_progress()
                    else:
                        progress = self.registry[key].logger_if.get_download_progress()

                    return (False, result_path, progress)

            with open(self.contract_path) as json_file:
                logger_data = json.load(json_file)
                logger_abi = logger_data['abi']
                deployed_address = logger_data['address']

            logger_if = Logger(w3, deployed_address, logger_abi)
            logger_if.instantiate(page_log2_size, tree_log2_size)

            job = None
            if action == "download":
                job = self.executor.submit(logger_if.download_file, bytes.fromhex(key), result_path)
            else:
                job = self.executor.submit(logger_if.submit_file, os.path.join(self.data_dir, key))

            self.registry[key] = LoggerStatus(result_path, logger_if, job)
            return (False, result_path, 0)
