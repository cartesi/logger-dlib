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
import subprocess
import logging
import os

LOGGER = logging.getLogger(__name__)


class LoggerStatus:

    def __init__(self, result_path, p):
        self.lock = Lock()
        self.result_path = result_path
        self.is_ready = False
        self.process_object = p


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

    def submit_file(self, filename, page_log2_size, tree_log2_size):

        basename = os.path.basename(filename)
        if not basename:
            # root, status, progress
            return ("00", 2, 0)

        file_path = os.path.join(self.data_dir, basename)
        if not valid_file(file_path):
            # root, status, progress
            return ("00", 2, 0)

        (is_ready, err_msg, result_path) = self.register_action("submit", file_path, page_log2_size, tree_log2_size)

        if not is_ready:
            # root, status, progress
            return ("00", 1, 0)

        with open(result_path, "r") as f:
            # root, status, progress
            return (f.readline(), 0, 100)

    def download_file(self, root, page_log2_size, tree_log2_size):

        (is_ready, err_msg, result_path) = self.register_action("download", root, page_log2_size, tree_log2_size)

        if not is_ready:
            # path, status, progress
            return ("", 1, 0)

        return (result_path, 0, 100)

    """
    Here starts the "internal" API, use the methods bellow taking the right precautions such as holding a lock
    """

    def register_action(self, action, key, page_log2_size, tree_log2_size):

        result_path = os.path.join(self.data_dir, "{}.{}".format(key, action))
        err_msg = "Result is not yet ready for file: {}".format(result_path)
        # Acquiring global lock and releasing it when completed
        LOGGER.debug("Acquiring registry %s global lock", action)
        with self.global_lock:
            LOGGER.debug("Lock acquired")
            if key in self.registry.keys():
                # already contains the request of key
                if self.registry[key].is_ready:
                    return (True, None, self.registry[key].result_path)

                if valid_file(result_path):
                    self.registry[key].is_ready = True
                    return (True, None, result_path)

                process_terminated = self.registry[key].process_object.poll()
                if process_terminated is None:
                    return (False, err_msg, None)

                # clean cache for failing entry
                self.registry.pop(key)
                return (False, "Fail to process file: {}, code: {}".format(result_path, process_terminated), None)

            args = ["python3", "simple_logger.py", "-a", action, "-p", key, "-b", str(page_log2_size), "-t", str(tree_log2_size), "-d", self.data_dir, "-c", self.contract_path]
            LOGGER.info("Issuing: %s ...", args)
            p = subprocess.Popen(args)
            self.registry[key] = LoggerStatus(result_path, p)
            return (False, err_msg, None)
