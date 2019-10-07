require('dotenv').config();
const fs = require('fs');
const yaml = require('js-yaml');

//Contracts
var LoggerTestInstantiator = artifacts.require("./LoggerTestInstantiator.sol");

// Read environment variable to set user address
module.exports = function(deployer, network, accounts) {
  //Deploy libraries
  deployer.then(async () => {

    var user = accounts[0];
    if (typeof process.env.WALLETS_FILE_PATH !== "undefined") {
        var accts = yaml.safeLoad(fs.readFileSync(process.env.WALLETS_FILE_PATH, 'utf8'));
        user = accts[0]["address"];
    }

    await deployer.deploy(LoggerTestInstantiator, user)
  });
};
