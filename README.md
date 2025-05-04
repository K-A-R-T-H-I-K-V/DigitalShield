DataGuardian: Secure Image Protection with AI Poisoning and Blockchain
Overview
DataGuardian is a cutting-edge solution to protect images from unauthorized AI training while ensuring user control over data access. Built for a hackathon, this project integrates AI-based image poisoning, watermarking, encryption, blockchain storage, and decentralized file management using IPFS (via Pinata). It consists of a Flask backend and a modular pipeline that ensures images are protected through three phases: poisoning, public tracking, and secure storage with revocation capabilities.
Features

Phase 1: Image Poisoning and Watermarking
Uses AI to poison images, preventing unauthorized AI training (via NightshadePoisoner).
Embeds a secret watermark for ownership verification.
Verifies poisoning and watermarking effectiveness.


Phase 2: Public Tracking (Optional)
Uploads the original image to IPFS (Pinata) and logs a record on the Sepolia blockchain with terms (e.g., "No AI training").


Phase 3: Secure Storage and Revocation
Encrypts the watermarked image using AES.
Stores the encrypted image on IPFS and the encryption key on the blockchain.
Allows revocation of access by unpinning from IPFS and marking the CID as revoked on-chain.



Tech Stack

Backend: Python, Flask
AI/ML: PyTorch, torchvision (for image poisoning)
Encryption: PyCryptodome (AES encryption)
Blockchain: Web3.py, Sepolia testnet (Ethereum)
Decentralized Storage: IPFS (via Pinata)
Dependencies: OpenCV, NumPy, Pillow, requests, python-dotenv

Directory Structure
DataGuardian/
│
├── data/
│   ├── clean/         # Original uploaded images
│   ├── poisoned/      # Poisoned images
│   ├── watermarked/   # Watermarked images
│   └── encrypted/     # Encrypted images
│
├── scripts/
│   ├── poison_generator.py   # Image poisoning logic
│   ├── verify_poisoning.py   # Poisoning verification
│   ├── watermark.py          # Watermark embedding
│   ├── verify_watermark.py   # Watermark verification
│   ├── encrypt.py            # AES encryption
│   ├── decrypt.py            # AES decryption
│   ├── upload_pinata.py      # IPFS upload via Pinata
│   ├── store_key.py          # Store encryption key on blockchain
│   ├── add_record.py         # Add public record on blockchain
│   └── revoke_access.py      # Revoke access to encrypted image
│
├── main.py          # Orchestrates the workflow
├── server.py        # Flask backend server
├── .env             # Environment variables (not included in repo)
└── README.md        # Project documentation

Setup Instructions

Clone the Repository
git clone https://github.com/your-repo/DataGuardian.git
cd DataGuardian


Install DependenciesEnsure Python 3.8+ is installed, then install the required packages:
pip install -r requirements.txt

If requirements.txt is not provided, install manually:
pip install flask torch torchvision opencv-python-headless numpy tqdm pillow pycryptodome web3 requests python-dotenv


Set Up Environment VariablesCreate a .env file in the project root with the following:
SEPOLIA_RPC_URL=https://your-sepolia-rpc-url
PRIVATE_KEY=your-wallet-private-key
CONTRACT_ADDRESS=your-deployed-contract-address
PINATA_API_KEY=your-pinata-api-key
PINATA_SECRET_KEY=your-pinata-secret-key
SECRET=your-watermark-secret


SEPOLIA_RPC_URL: URL for Sepolia testnet (e.g., Infura).
PRIVATE_KEY: Your Ethereum wallet private key.
CONTRACT_ADDRESS: Address of your deployed DataGuardian smart contract.
PINATA_API_KEY and PINATA_SECRET_KEY: Credentials from Pinata (https://pinata.cloud).
SECRET: A secret string for watermarking.


Run the BackendStart the Flask server:
python server.py

The server will run on http://localhost:5000.


API Endpoints
1. Protect an Image (/api/protect)

Method: POST
Content-Type: multipart/form-data
Parameters:
image: The image file to protect.
isPublic (optional): Set to true to enable public tracking (Phase 2).


Example:curl -X POST -F "image=@path/to/image.jpg" -F "isPublic=true" http://localhost:5000/api/protect


Response:{
  "publicCid": "Qm... (if isPublic=true)",
  "encryptedCid": "Qm..."
}



2. Revoke Access (/api/revoke)

Method: POST
Content-Type: application/json
Body:{
  "cid": "your-encrypted-cid"
}


Example:curl -X POST -H "Content-Type: application/json" -d '{"cid":"Qm..."}' http://localhost:5000/api/revoke


Response:{
  "success": true
}



Usage

Protect an Image:

Upload an image via the /api/protect endpoint.
The backend will poison, watermark, encrypt, and store the image on IPFS.
If isPublic=true, the original image is uploaded to IPFS with a blockchain record.
The response includes CIDs for the public (if applicable) and encrypted images.


Revoke Access:

Send the encrypted CID to the /api/revoke endpoint.
The backend will revoke access on-chain, unpin the file from IPFS, and delete the local encrypted file.



Smart Contract
The project uses a DataGuardian smart contract on the Sepolia testnet with the following functions:

storeKey(cid, key): Stores the encryption key for a CID.
addRecord(cid, terms): Logs a public record with terms.
revokeAccess(cid): Marks a CID as revoked.
isRevoked(cid): Checks if access is revoked.
getKey(cid): Retrieves the encryption key (fails if revoked).

Future Improvements

Add a frontend interface for easier user interaction.
Support batch processing of multiple images.
Implement user authentication for secure access.
Add more robust error handling and retry mechanisms for blockchain transactions.

Team Apotheosis

KARTHIK 
JM MUSHRAFF
KRISHNA
HIMANSHU SAHU


