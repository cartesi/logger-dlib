const LoggerTestInstantiator = artifacts.require("LoggerTestInstantiator");

module.exports = function(deployer, network, accounts) {
  deployer.deploy(LoggerTestInstantiator, accounts[0]);
};
