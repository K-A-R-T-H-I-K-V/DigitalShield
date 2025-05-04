const hre = require("hardhat");

async function main() {
  const DataGuardian = await hre.ethers.getContractFactory("DataGuardian");
  const dataGuardian = await DataGuardian.deploy();

  console.log("DataGuardian deployed to:", dataGuardian.target);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});