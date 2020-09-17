# Logger DLib

Logger Dlib is the combination of the On-chain Logger and the Off-chain Logger module that together provide anyone the ability to submit their data and retrieve the data later with its merkle tree root hash. The on-chain contracts are written in Solidity, the off-chain module is written in Python, the on-chain deploy scripts are written in TypeScript (with the help of [Buidler](https://buidler.dev/plugins/buidler-deploy.html)), and the testing scripts are written in Python.

The best way to use the Logger Dlib is through the grpc interfaces, which are defined in the submodule `/grpc-interfaces/`. A grpc server and test client are implemented in Python in the `server` directory: `logger_server.py`, `test_client.py`.

## On-chain Logger
(contracts directory)

The On-chain Logger contract provides a way for anyone to prove the relationship between a merkle tree root hash and its original raw data. One can send a list of words of binary data to the on-chain logger and get the merkle tree root hash, original list of data, index of the hash stored in the contract and the log2 size of the generated merkle tree.

*Note that the merkle tree naturally requires the input list to be power of 2 size, if not, will zero-padding to the next power of 2 size. Can refer to the off-chain module see the detail usage.*

## Off-chain Logger Module
(logger directory)

The Off-chain Logger python module implements a class and multiple functions that one can easily interact with the On-chain Logger contract. Including submitting data, zero-padding the data if size is not power of 2 and retrieve the original raw data simply with the merkle tree root hash later in the future. The module also checks the On-chain Logger if the desired data is already submitted to save unnecessary gas expenditure. The details of usage please refer to the tests section.

## Testing with the On-chain contract using Off-chain module (unit test)
(test directory)

### Quick Start

Run the following command to execute tests against the Logger contract
```shell
% ./logger-tests
```

### Examples

```python
test_logger = Logger(w3, deployed_address, logger_data['abi'])
page_log2_size = 5
tree_log2_size = 8
test_logger.instantiate(page_log2_size, tree_log2_size)
```
The above codes first create an object of the Logger class with the blockchain endpoint, logger contract address and the abi definition of the contract. Then call the instantiate function with `page_log2_size` and the `tree_log2_size` to prepare the data structure for later usage. `page_log2_size` is the log2 value of the size of the leaf in the merkle tree in the unit of byte. `tree_log2_size` is the log2 value of the size of the entire merkle tree. Take above code example, the merkle tree is 256(2^8) bytes large, and the leaf is 32(2^5) bytes large.

```python
data = []
data.append(bytes("est95192", 'utf-8'))
data.append(bytes("51e5q1w9", 'utf-8'))
data.append(bytes("54sd984s", 'utf-8'))
data.append(bytes("df5a1ste", 'utf-8'))

(index, root) = test_logger.submit_data_to_logger(data)
```
The above codes call the `submit_data_to_logger` with some hard-coded data. Index and merkle tree root hash will be returned in a tuple.

```python
indices = []
indices.append(index_1)
indices.append(index_1)

(index, root) = test_logger.submit_indices_to_logger(page_log2_size, indices)
```
The above codes call the `submit_indices_to_logger` with a list of indices. The indices are the merkle trees that has been created in advance and been stored in the contract history. Index and merkle tree root hash will be returned in a tuple.

```python
input_file = "test_file"
output_file = "recovered_file"

root = test_logger.submit_file(input_file)
test_logger.download_file(root, output_file)

assert filecmp.cmp(input_file, output_file), "Files not match"
```
The above codes call the `submit_file` with a file existing on the machine. This function will automatically handles the details of submitting raw data to the On-chain Logger. A root hash of the constructed merkle tree will be returned. Then call the `download_file` with the root hash just received and the destination path to write to the file. The two files should be identical.

## Testing with the grpc server using test client (integration test)

### Requirements

- Python >= 3.6
- Python modules described in the requirements.txt file
- [grpc interfaces](https://github.com/cartesi/grpc-interfaces)

### Installing python dependencies to execute the logger manager server natively

It is highly advisable to make a separate python environment to install the dependencies for executing the logger manager server. A very popular option to do that is using virtualenv with virtualenvwrapper, on Ubuntu you can install them by executing:
```console
$ sudo apt install virtualenvwrapper
```

Install python3 in case you don't already have it
```console
$ sudo apt install python3
```

And then create a new virtual env (named "logger" in the example) that uses python3:
```console
$ mkvirtualenv -p `which python3` logger
```

Once you run this step, your terminal should exhibit the activated virtual env name right in the beginning of every line in your shell, similar to this example:
```console
(logger) stephen@laptop:~/git/logger-dlib$ _
```

And now you may install the python dependencies from the requirements file in your virtual env:
```console
$ pip install -r requirements.txt
```

In case you don't need any additional packages installed in your system to install the python modules from the step above, you are now ready to execute the logger manager server.

Once you have your virtualenv set up, you may activate it on a terminal using the command "workon":
```console
stephen@laptop:~/git/logger-dlib$ workon logger
(logger) stephen@laptop:~/git/logger-dlib$ _
```

And you may deactivate it and go back to using your system-wide python installed environment using the command "deactivate":
```console
(logger) stephen@laptop:~/git/logger-dlib$ deactivate
stephen@laptop:~/git/logger-dlib$ _
```

### Executing the logger manager server

To start the server listening on localhost and port 50051, just execute it:
```console
$ ./logger-server
```

The server has a couple of options to customize it's behavior, you can check them using the -h option:
```console
$ ./logger-server -h
usage: logger_server.py [-h] [--address ADDRESS] [--port PORT]
                        [--data_dir DATA_DIRECTORY]
                        [--contract_path CONTRACT_PATH]

Instantiates a logger manager server, responsible for managing and interacting
with logger contract

optional arguments:
  -h, --help            show this help message and exit
  --address ADDRESS, -a ADDRESS
                        Address to listen (default: localhost)
  --port PORT, -p PORT  Port to listen (default: 50051)
  --data_dir DATA_DIRECTORY, -d DATA_DIRECTORY
                        Data directory for files (default:
                        /Users/tuler/Documents/workspace/cartesi/logger-
                        dlib/logger)
  --contract_path CONTRACT_PATH, -c CONTRACT_PATH
                        Path for contract json file in buidler format
                        (default:
                        /opt/cartesi/share/blockchain/contracts/Logger.json)
```

*Note that in order to run the server natively, one needs to specify the --contract_path and --data_dir arguments, pointing to the local paths repectively. It's also required to generate the python code for the grpc interfaces from the proto files. Refer to the section in the Dockerfile*

### Executing the test client

Once you have the logger manager server up and running, you may want to test it is working correctly using the included test client, if the server is running natively and locally all you have to do is execute it with no additional arguments:
```console
$ ./test-client
```

After the client sends grpc request for the first time, the task will be executed in the background. The server will cache the result when the request is completed, and respond when the client asks again in the future. The server responds with a structure consisting of the status of the job and other data. Only when the status is `0`, job finished successfully, all other data in the structure become meaningful, Try execute the test_client multiple times and one should eventually get the result.

```
# status: 0 -> finished successfully
#         1 -> working on it, not ready yet
#         2 -> invalid argument
#         3 -> service not available, shutting down
```

The test client also has a couple of options to customize it's behavior, you may check them with the -h or --help option:
```console
$ ./test-client -h
Starting at Wed Sep 25 19:09:10 2019
usage: test_client.py [-h] [--address ADDRESS] [--port PORT] [--container]
                      [--mode MODE]

GRPC test client to the logger manager server

optional arguments:
  -h, --help            show this help message and exit
  --address ADDRESS, -a ADDRESS
                        Logger manager server address
  --port PORT, -p PORT  Logger manager server port
  --container, -c       Fixes file references for when logger manager server
                        is running from docker container
  --mode MODE, -m MODE  Client mode can be submit or download
```

## Contributing

Pull requests are welcome. When contributing to this repository, please first discuss the change you wish to make via issue, email, or any other method with the owners of this repository before making a change.

Please note we have a code of conduct, please follow it in all your interactions with the project.

## Authors

* *Stephen Chen*

## License

Note: This component currently has dependencies that are licensed under the GNU GPL, version 3, and so you should treat this component as a whole as being under the GPL version 3. But all Cartesi-written code in this component is licensed under the Apache License, version 2, or a compatible permissive license, and can be used independently under the Apache v2 license. After this component is rewritten, the entire component will be released under the Apache v2 license.
The dispatcher repository and all contributions are licensed under
[GPL 3](https://www.gnu.org/licenses/gpl-3.0.en.html). Please review our [LICENSE](COPYING) file.

## Acknowledgments

- Original work 
