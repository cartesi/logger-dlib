const fs = require('fs');

//Contracts
var LoggerTestInstantiator = artifacts.require("./LoggerTestInstantiator.sol");

// Read environment variable to set user address
module.exports = function(deployer, network, accounts) {
  //Deploy libraries
  deployer.then(async () => {

    var user = accounts[0];
    await deployer.deploy(LoggerTestInstantiator, user)
  });
};
