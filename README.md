# Logger D-Lib

Logger Dlib is the combination of the On-chain Logger and the Off-chain Logger module that together provide anyone to submit their data and retrieve the data later with its merkle tree root hash. The on-chain contracts are written in Solidity, the off-chain module is written in Python, the migration script is written in Javascript (with the help of [Truffle](https://github.com/trufflesuite/truffle)), and the testing scripts are written in Python.

## On-chain Logger
(contracts directory)

The On-chain Logger contract provides a way for anyone to prove the relationship between a merkle tree root hash and its original raw data. One can send a list of words of binary data to the on-chain logger and get the merkle tree root hash, original list of data, index of the hash stored in the contract and the log2 size of the generated merkle tree.

*Note that the merkle tree naturally requires the input list to be power of 2 size, if not, will zero-padding to the next power of 2 size. Can refer to the off-chain module see the detail usage.*

## Off-chain Logger Module
(logger directory)

The Off-chain Logger python module implements a class and multiple functions that one can easily interact with the On-chain Logger contract. Including submitting data, zero-padding the data if size is not power of 2 and retrieve the original raw data simply with the merkle tree root hash later in the future. The details of usage please refer to the tests section.

## Testing with the On-chain contract using Off-chain module
(test directory)

### Quick Start

Run the following command to execute tests against the Logger contract
```shell
python test_logger.py
```

### Examples

```python
test_logger = Logger("http://127.0.0.1:8545", deployed_address["logger_address"], logger_data['abi'])
test_logger.instantiate(2, 5)
```
The above codes first create an object of the Logger class with the blockchain endpoint, logger contract address and the abi definition of the contract. Then call the instantiate function with `page_log2_size` and the `tree_log2_size` to prepare the data structure for later usage.

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

(index, root) = test_logger.submit_indices_to_logger(indices)
```
The above codes call the `submit_indices_to_logger` with a list of indices. The indices are the merkle trees that has been created in advance and been stored in the contract history. Index and merkle tree root hash will be returned in a tuple.

```python
input_file = "test_file"
output_file = "recovered_file"

root = test_logger.upload_file(input_file)
test_logger.download_file(root, output_file)

assert filecmp.cmp(input_file, output_file), "Files not match"
```
The above codes call the `upload_file` with a file existing on the machine. This function will automatically handles the details of submitting raw data to the On-chain Logger. A root hash of the constructed merkle tree will be returned. Then call the `download_file` with the root hash just received and the destination path to write to the file. The two files should be identical.

## Contributing

Pull requests are welcome. When contributing to this repository, please first discuss the change you wish to make via issue, email, or any other method with the owners of this repository before making a change.

Please note we have a code of conduct, please follow it in all your interactions with the project.

## Authors

* *Stephen Chen*

## License

- TODO

## Acknowledgments

- Original work 
