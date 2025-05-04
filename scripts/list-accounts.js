const hre = require("hardhat");

async function main() {
  const accounts = await hre.ethers.getSigners();
  console.log("Accounts:", accounts.map((acc) => acc.address));
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});