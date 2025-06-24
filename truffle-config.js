require('dotenv').config();
const HDWalletProvider = require('@truffle/hdwallet-provider');

module.exports = {
  networks: {
    development: {
      provider: () => new HDWalletProvider({
        privateKeys: [process.env.PRIVATE_KEY],
        providerOrUrl: 'http://127.0.0.1:7545',
        chainId: 1337 // Match Ganache's chain ID
      }),
      network_id: '*',
      networkCheckTimeout: 100000,
      timeoutBlocks: 500,
      skipDryRun: true
    }
  },
  compilers: {
    solc: {
      version: "0.8.0",
      settings: {
        optimizer: {
          enabled: true,
          runs: 200
        }
      }
    }
  }
};