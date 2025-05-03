const hre = require("hardhat");
require("dotenv").config();

async function main() {
  const [signer] = await hre.ethers.getSigners();
  const balance = await hre.ethers.provider.getBalance(signer.address);
  console.log("Account:", signer.address);
  console.log("Balance:", hre.ethers.formatEther(balance), "ETH");
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});