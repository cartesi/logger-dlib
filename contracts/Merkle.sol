// Copyright 2019 Cartesi Pte. Ltd.

// Licensed under the Apache License, Version 2.0 (the "License"); you may not use
// this file except in compliance with the License. You may obtain a copy of the
// License at http://www.apache.org/licenses/LICENSE-2.0

// Unless required by applicable law or agreed to in writing, software distributed
// under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
// CONDITIONS OF ANY KIND, either express or implied. See the License for the
// specific language governing permissions and limitations under the License.

/// @title Library for Merkle proofs
pragma solidity ^0.5.0;

/// @title Merkle
/// @author Augusto Teixeira
/// @notice Implements the getRoot function for a Merkle tree


library Merkle {
    function getRoot(uint64 _position, bytes8 _value, bytes32[] memory proof) internal pure returns (bytes32) {
        require((_position & 7) == 0, "Position is not aligned");
        require(proof.length == 61, "Proof length does not match");
        bytes32 runningHash = keccak256(abi.encodePacked(_value));
        // iterate the hash with the uncle subtree provided in proof
        uint64 eight = 8;
        for (uint i = 0; i < 61; i++) {
            if ((_position & (eight << i)) == 0) {
                runningHash = keccak256(abi.encodePacked(runningHash, proof[i]));
            } else {
                runningHash = keccak256(abi.encodePacked(proof[i], runningHash));
            }
        }
        return (runningHash);
    }

    function getLog2Floor(uint256 number) internal pure returns (uint32) {

        uint32 result = 0;

        uint256 checkNumber = number;
        checkNumber = checkNumber >> 1;
        while (checkNumber > 0) {
            ++result;
            checkNumber = checkNumber >> 1;
        }

        return result;
    }

    function isPowerOf2(uint256 number) internal pure returns (bool) {

        uint256 checkNumber = number;
        if (checkNumber == 0) {
            return false;
        }

        while ((checkNumber & 1) == 0) {
            checkNumber = checkNumber >> 1;
        }

        checkNumber = checkNumber >> 1;

        if (checkNumber == 0) {
            return true;
        }

        return false;
    }

    /// @notice Calculate the root of Merkle tree from an array of power of 2 elements
    /// @param hashes The array containing power of 2 elements
    /// @return byte32 the root hash being calculated
    function calculateRootFromPowerOfTwo(bytes32[] memory hashes) internal pure returns (bytes32) {
        // revert when the input is not of power of 2
        require(isPowerOf2(hashes.length), "The input array must contain power of 2 elements");

        if (hashes.length == 1) {
            return hashes[0];
        }else {
            bytes32[] memory newHashes = new bytes32[](hashes.length >> 1);

            for (uint256 i = 0; i < hashes.length; i += 2) {
                newHashes[i >> 1] = keccak256(abi.encodePacked(hashes[i], hashes[i + 1]));
            }

            return calculateRootFromPowerOfTwo(newHashes);
        }
    }
}
