const Logger = artifacts.require("Logger");

module.exports = function(deployer) {
  deployer.deploy(Logger);
};
