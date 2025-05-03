from web3 import Web3
from web3.exceptions import ContractLogicError
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
SEPOLIA_RPC_URL = os.getenv("SEPOLIA_RPC_URL")
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")
IMAGE_CID = os.getenv("IMAGE_CID")

# Debug: Print loaded values
print(f"Using CONTRACT_ADDRESS: {CONTRACT_ADDRESS}")
print(f"Using IMAGE_CID: {IMAGE_CID}")

if not all([SEPOLIA_RPC_URL, CONTRACT_ADDRESS, IMAGE_CID]):
    raise ValueError("Missing environment variables. Check .env file.")

# Connect to Sepolia
w3 = Web3(Web3.HTTPProvider(SEPOLIA_RPC_URL))
if not w3.is_connected():
    raise ConnectionError("Failed to connect to Sepolia. Check SEPOLIA_RPC_URL.")

# Load contract ABI
contract_abi = [
    {
        "inputs": [],
        "name": "owner",
        "outputs": [{"internalType": "address", "name": "", "type": "address"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "string", "name": "cid", "type": "string"}],
        "name": "isRevoked",
        "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "string", "name": "cid", "type": "string"}],
        "name": "getKey",
        "outputs": [{"internalType": "string", "name": "", "type": "string"}],
        "stateMutability": "view",
        "type": "function"
    }
]

contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=contract_abi)

# Check the owner
try:
    owner = contract.functions.owner().call()
    print(f"Contract owner: {owner}")
except ContractLogicError as e:
    print(f"Failed to retrieve owner: {str(e)}")

# Check revocation status
try:
    is_revoked = contract.functions.isRevoked(IMAGE_CID).call()
    print(f"Is CID revoked? {is_revoked}")
except ContractLogicError as e:
    print(f"Failed to check revocation status: {str(e)}")
    print("The contract may not have an isRevoked function, or no data exists for this CID.")

# Attempt to retrieve the key
try:
    key = contract.functions.getKey(IMAGE_CID).call()
    print(f"Retrieved key: {key}")
except ContractLogicError as e:
    print(f"Failed to retrieve key: {str(e)}")