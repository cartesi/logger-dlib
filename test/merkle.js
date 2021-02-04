const ethers = require('ethers')
const fs = require('fs')

const emptyDataHashes = ['0x011b4d03dd8c01f1049143cf9c4c817e4b167f1d1b83e5c6f0f10d89ba1e7bce'];

/**
 * Turns buffer into an array of 8-byte data entries
 * - Last data entry is padded to an 8-byte size
 * - Array is padded with zero-filled 8-byte entries to reach a power of two and minimum size of 32 bytes
 * 
 * @param {Buffer} buffer Data to read
 * @return {Array} array of buffers for 8-byte data entries, padded with zeros to reach a length that is a power of 2
 */
function get8byteDataEntries(buffer) {
    const nDataEntries = Math.ceil(buffer.length/8);
    const dataEntries = [];
    for (let i = 0; i < nDataEntries; i++) {
        const begin = i*8;
        const end = (i+1)*8;
        if (end <= buffer.length) {
            // adds regular data entry
            dataEntries.push(Buffer.from(buffer.subarray(begin, end)));
            // console.debug(`Entry: ${ethers.utils.hexlify(dataEntries[i])}`);
        } else {
            // adds last entry with padding to fill in 8-byte size
            const paddedDataEntry = Buffer.alloc(8);
            buffer.copy(paddedDataEntry, 0, begin, end);
            dataEntries.push(paddedDataEntry);
            // console.debug(`Entry (padded): ${ethers.utils.hexlify(dataEntries[i])}`);
        }
    }
    return dataEntries;
}

/**
 * Retrieves the root hash for a tree of empty data entries.
 * 
 * @param {Number} level the level or height of the root of the tree (0 corresponds to the leaf level)
 * @return the Merkle root hash
 */
function getEmptyTreeHash(level) {
    if (emptyDataHashes[level]) {
        // returns pre-computed hash for empty data at the specified level
        return emptyDataHashes[level];
    } else {
        // computes hash for empty data at the specified level by considering a pair of hashes for empty data at level-1
        const lowerLevelHash = getEmptyTreeHash(level-1);
        const hash = ethers.utils.solidityKeccak256(["bytes32","bytes32"], [lowerLevelHash, lowerLevelHash]);
        emptyDataHashes[level] = hash;
        // console.debug(`Computed empty hash for level ${level}: ${hash}`);
        return hash;
    }
}

/**
 * Calculates the root of the Merkle tree represented by an array of 32-byte hashes
 * 
 * @param {Array} hashes array of 32-byte keccak256 hashes, whose length must be a power of 2
 * @param {Number} level the level of the tree corresponding to the hashes (0 corresponds to the leaf level)
 * @param {Number} rootLevel the level of the tree corresponding to the root (0 corresponds to the leaf level)
 * @return the Merkle root hash
 */
function computeMerkleRootHashFromHashes(hashes, level, rootLevel) {
    if (hashes.length === 1 && level === rootLevel) {
        // reached root: just returns hash
        return hashes[0];
    } else {
        // non-root level: computes hash for each pair of entries
        const upperLevelHashes = [];
        for (let i = 0; i < hashes.length; i += 2) {
            const hash1 = hashes[i];
            const hash2 = (i === hashes.length - 1) ? getEmptyTreeHash(level) : hashes[i+1];
            let hash = ethers.utils.solidityKeccak256(["bytes32","bytes32"], [hash1, hash2]);
            upperLevelHashes.push(hash);
            // console.debug(`Hash ${i}+${i+1}: ${hash}`);
        }
        return computeMerkleRootHashFromHashes(upperLevelHashes, level+1, rootLevel);
    }    
}

/**
 * Calculates the Merkle root hash for a given data Buffer.
 * - Turns buffer into an array of 8-byte data entries
 * - Pads array so that its length is a power of two, so that its entries correspond to the leaves of the Merkle tree.
 * - Computes hashes for the entries (leaves) and recursively computes the hashes of each pair up to the root.
 * 
 * @param {Buffer} buffer data for which the Merkle root hash will be computed
 * @return the Merkle root hash
 */
function computeMerkleRootHash(buffer) {
    const bufferLog2Size = Math.max(5, Math.ceil(Math.log2(buffer.length)));
    const rootLevel = bufferLog2Size - 3;
    console.debug(`BufferLength: ${buffer.length} ; BufferLog2Size: ${bufferLog2Size}`);

    // turns buffer into an array of 8-byte data entries
    const dataEntries = get8byteDataEntries(buffer);

    // computes keccak256 hash for each array entry (leaves in the merkle tree)
    const hashes = [];
    for (let i = 0; i < dataEntries.length; i++) {
        const data = ethers.utils.hexlify(dataEntries[i]);
        hashes.push(ethers.utils.solidityKeccak256(["bytes8"], [data]));
        // console.debug(`${i} - Data: '${data}' ; Hash: ${hashes[i]}`);
    }

    // calculates merkle root hash by recursively computing the keccak256 of the concatenation of each data entry pair
    const rootHash = computeMerkleRootHashFromHashes(hashes, 0, rootLevel);
    return rootHash;
}

async function main() {
    var args = process.argv.slice(2);
    if (!args.length) {
        return;
    }

    const buffer = fs.readFileSync(args[0]);
    const rootHash = computeMerkleRootHash(buffer);
    console.log(`Root Hash: ${rootHash}`);
}

// We recommend this pattern to be able to use async/await everywhere
// and properly handle errors.
main()
    .then(() => process.exit(0))
    .catch((error) => {
        console.error(error);
        process.exit(1);
    });