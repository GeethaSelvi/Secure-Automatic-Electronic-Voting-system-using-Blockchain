// migrations/2_deploy_contracts.js
const Voting = artifacts.require("Voting");

module.exports = function(deployer) {
  deployer.deploy(Voting);
};
