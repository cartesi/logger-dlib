// Copyright 2019 Cartesi Pte. Ltd.

// Licensed under the Apache License, Version 2.0 (the "License"); you may not use
// this file except in compliance with the License. You may obtain a copy of the
// License at http://www.apache.org/licenses/LICENSE-2.0

// Unless required by applicable law or agreed to in writing, software distributed
// under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
// CONDITIONS OF ANY KIND, either express or implied. See the License for the
// specific language governing permissions and limitations under the License.

pragma solidity ^0.5.0;

import "@cartesi/util/contracts/Decorated.sol";
import "@cartesi/util/contracts/Merkle.sol";
import "./LoggerInterface.sol";


/// @title Logger
/// @author Stephen Chen
/// @notice A contract that offers data availability
/// @dev This contract is not well-tested yet.
contract Logger is Decorated, LoggerInterface {
  // the caller can either provide the full data to generate the Merkle tree root
  // or combine the existing hashes in the history to a deeper tree

    struct DataEntry {
        // TODO: change the type of log2Size based on the max log size(disk size) of the DApp
        uint64 log2Size;
        bytes32 root;
    }

    mapping(bytes32 => bool) logSubmitted;
    DataEntry[] dataHistory;

    uint256 public currentIndex = 0;

    // TODO: get rid of the _data from event
    event MerkleRootCalculatedFromData(uint256 indexed _index, bytes8[] _data, bytes32 indexed _root, uint64 _log2Size);
    event MerkleRootCalculatedFromHistory(uint256 indexed _index, uint256[] _indices, bytes32 indexed _root, uint64 _log2Size);

    /// @notice Calculate the Merkle tree and return the root hash
    // @param _hashes The array of words of the file
    function calculateMerkleRootFromData(uint64 _log2Size, bytes8[] memory _data) public returns(bytes32) {
        require(_data.length > 0, "The input array cannot be empty");

        // uint64 log2Size = Merkle.getLog2Floor(_data.length);
        bytes8[] memory data = _data;
        uint256 power2Length = 2 ** (_log2Size);

        // if (!Merkle.isPowerOf2(_data.length)) {
        if (_data.length != power2Length) {
            // pad the list to length of power of 2
            bytes8[] memory paddedData = new bytes8[](power2Length);

            for (uint256 i = 0; i < _data.length; ++i) {
                paddedData[i] = _data[i];
            }
            for (uint256 i = _data.length; i < paddedData.length; ++i) {
                paddedData[i] = 0;
            }
            data = paddedData;
        }

        bytes32[] memory hashes = new bytes32[](data.length);

        for (uint256 i = 0; i<data.length; ++i) {
            hashes[i] = keccak256(abi.encodePacked(data[i]));
        }

        bytes32 root = Merkle.calculateRootFromPowerOfTwo(hashes);
        dataHistory.push(DataEntry(_log2Size, root));
        emit MerkleRootCalculatedFromData(
            currentIndex,
            _data,
            root,
            _log2Size);
        ++currentIndex;
        logSubmitted[root] = true;
        return root;
    }

    /// @notice Calculate the Merkle tree and return the root hash
    // @param _indices The array of indices of the history
    function calculateMerkleRootFromHistory(uint64 _log2Size, uint256[] memory _indices) public returns(bytes32) {
        require(Merkle.isPowerOf2(_indices.length), "The input array must contain power of 2 elements");

        // check indices exist and the value of log2Size matches
        for (uint256 i = 0; i<_indices.length; ++i) {
            require(currentIndex > _indices[i], "The index of history doesn't exist yet");
            require(_log2Size == dataHistory[_indices[i]].log2Size, "The value of log2Size doesn't match in history");
        }

        bytes32[] memory hashes = new bytes32[](_indices.length);
        for (uint256 i = 0; i<_indices.length; ++i) {
            hashes[i] = dataHistory[_indices[i]].root;
        }

        bytes32 root = Merkle.calculateRootFromPowerOfTwo(hashes);

        uint64 log2Size = Merkle.getLog2Floor(_indices.length);
        dataHistory.push(DataEntry(log2Size + _log2Size, root));
        emit MerkleRootCalculatedFromHistory(
            currentIndex,
            _indices,
            root,
            log2Size + _log2Size);
        ++currentIndex;
        logSubmitted[root] = true;
        return root;
    }

    /// @notice Getter function to check if log has been submitted for the given hash
    // @param _indices The array of indices of the history
    function isLogAvailable(bytes32 _root) public view returns(bool) {
        return logSubmitted[_root];
    }
}
