const ethers = require('ethers')
const fs = require('fs')

/**
 * Turns buffer into an array of 8-byte data entries
 * - Last data entry is padded to an 8-byte size
 * - Array is padded with zero-filled 8-byte entries to reach a power of two and minimum size of 32 bytes
 * 
 * @param {Buffer} buffer Data to read
 * @return {Array} array of buffers for 8-byte data entries, padded with zeros to reach a length that is a power of 2
 */
function get8byteDataEntries(buffer) {
    const bufferLog2Size = Math.max(5, Math.ceil(Math.log2(buffer.length)));
    const nDataEntries = 2**(bufferLog2Size - 3);
    const dataEntries = [];
    console.log(`BufferLength: ${buffer.length} ; BufferLog2Size: ${bufferLog2Size} ; BufferNDataEntries: ${nDataEntries}`);
    const emptyDataEntry = Buffer.alloc(8);
    // console.log(`Empty: ${JSON.stringify(emptyDataEntry)}`);
    for (let i = 0; i < nDataEntries; i++) {
        const begin = i*8;
        const end = (i+1)*8;
        if (begin >= buffer.length) {
            // adds empty entry (padding)
            dataEntries.push(emptyDataEntry);
        } else if (end >= buffer.length) {
            // adds last entry with padding to fill in 8-byte size
            const paddedDataEntry = Buffer.alloc(8);
            buffer.copy(paddedDataEntry, 0, begin, end);
            dataEntries.push(paddedDataEntry);
            // console.log(`Entry (padded): ${JSON.stringify(dataEntries[i])}`);
        } else {
            // adds regular data entry
            dataEntries.push(Buffer.from(buffer.subarray(begin, end)));
            // console.log(`Entry: ${JSON.stringify(dataEntries[i])}`);
        }
    }
    return dataEntries;
}

/**
 * Calculates the root of the Merkle tree represented by an array of 32-byte hashes
 * 
 * @param {Array} hashes array of 32-byte keccak256 hashes, whose length must be a power of 2
 * @return the Merkle root hash
 */
function computeMerkleRootHashFromHashes(hashes) {
    if (hashes.length === 1) {
        return hashes[0];
    } else {
        const upperLevelHashes = [];
        for (let i = 0; i < hashes.length; i += 2) {
            let hash = ethers.utils.solidityKeccak256(["bytes32","bytes32"], [hashes[i], hashes[i+1]]);
            upperLevelHashes.push(hash);
            // console.log(`Hash ${i}+${i+1}: ${hash}`);
        }
        return computeMerkleRootHashFromHashes(upperLevelHashes);
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
    // turns buffer into an array of 8-byte data entries
    const dataEntries = get8byteDataEntries(buffer);

    // computes keccak256 hash for each array entry (leaves in the merkle tree)
    const hashes = [];
    for (let i = 0; i < dataEntries.length; i++) {
        const data = ethers.utils.hexlify(dataEntries[i]);
        hashes.push(ethers.utils.solidityKeccak256(["bytes8"], [data]));
        console.debug(`${i} - Data: '${data}' ; Hash: ${hashes[i]}`);
    }

    // calculates merkle root hash by recursively computing the keccak256 of the concatenation of each data entry pair
    const rootHash = computeMerkleRootHashFromHashes(hashes);
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