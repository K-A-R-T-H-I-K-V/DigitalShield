const hre = require("hardhat");
require("dotenv").config();

async function main() {
    const contractAddress = process.env.CONTRACT_ADDRESS;
    const cid = process.env.IMAGE_CID;
    const terms = "No AI training";

    if (!contractAddress || !cid) {
        throw new Error("CONTRACT_ADDRESS or IMAGE_CID missing in .env");
    }

    const DataGuardian = await hre.ethers.getContractFactory("DataGuardian");
    const dataGuardian = await DataGuardian.attach(contractAddress);

    const tx = await dataGuardian.addRecord(cid, terms);
    await tx.wait();

    console.log("Record added:", cid, terms);

    const [recordCid, owner, recordTerms] = await dataGuardian.getRecord(cid);
    console.log("Verified record:", recordCid, owner, recordTerms);
}

main().catch((error) => {
    console.error(error);
    process.exitCode = 1;
});