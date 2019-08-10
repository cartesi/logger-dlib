require('dotenv').config();
const fs = require('fs');

//Libraries

//Contracts
var Logger = artifacts.require("./Logger.sol");

// Read environment variable to decide if it should instantiate MM or get the address
module.exports = function(deployer) {
  //Deploy libraries
  deployer.then(async () => {

    await deployer.deploy(Logger)

    // Write address to file
    let addr_json = "{\"logger_address\":\"" + Logger.address + "\"}";

    fs.writeFile('../test/deployedAddresses.json', addr_json, (err) => {
      if (err) console.log("couldnt write to file");
    });

    if (process.env.STEP_ADD_FILE_PATH) {
        fs.writeFileSync(process.env.STEP_ADD_FILE_PATH, Step.address);
    }
  });
};
