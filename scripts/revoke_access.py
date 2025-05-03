from web3 import Web3
import requests
import os
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def revoke_access_on_chain(sepolia_rpc_url, private_key, contract_address, cid):
    """Revoke access via smart contract"""
    w3 = Web3(Web3.HTTPProvider(sepolia_rpc_url))
    if not w3.is_connected():
        raise ConnectionError("Failed to connect to Sepolia. Check SEPOLIA_RPC_URL.")

    account = w3.eth.account.from_key(private_key)

    contract_abi = [
        {
            "inputs": [{"internalType": "string", "name": "cid", "type": "string"}],
            "name": "revokeAccess",
            "outputs": [],
            "stateMutability": "nonpayable",
            "type": "function"
        },
        {
            "anonymous": False,
            "inputs": [{"indexed": False, "internalType": "string", "name": "cid", "type": "string"}],
            "name": "AccessRevoked",
            "type": "event"
        },
        {
            "inputs": [{"internalType": "string", "name": "cid", "type": "string"}],
            "name": "isRevoked",
            "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
            "stateMutability": "view",
            "type": "function"
        }
    ]

    contract = w3.eth.contract(address=contract_address, abi=contract_abi)

    logger.info(f"Attempting to revoke access for CID: {cid}")
    nonce = w3.eth.get_transaction_count(account.address)
    logger.info(f"Using nonce: {nonce}")
    tx = contract.functions.revokeAccess(cid).build_transaction({
        'from': account.address,
        'nonce': nonce,
        'gas': 300000,
        'gasPrice': w3.to_wei('50', 'gwei')
    })
    signed_tx = w3.eth.account.sign_transaction(tx, private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    logger.info(f"Transaction sent: {tx_hash.hex()}")
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
    logger.info(f"Access revoked on-chain: {tx_hash.hex()}")
    logger.info(f"Transaction confirmed in block: {receipt.blockNumber}")
    # record_action(cid, "revoked", f"Transaction hash: {tx_hash.hex()}")
    return tx_hash.hex()

def unpin_from_pinata(cid, pinata_api_key, pinata_secret_key):
    """Unpin a file from Pinata"""
    logger.info(f"Attempting to unpin CID: {cid} from Pinata")
    headers = {
        "pinata_api_key": pinata_api_key,
        "pinata_secret_api_key": pinata_secret_key
    }
    response = requests.delete(f"https://api.pinata.cloud/pinning/unpin/{cid}", headers=headers)
    if response.status_code == 200:
        logger.info(f"Successfully unpinned CID {cid} from Pinata")
        # record_action(cid, "unpinned", "Removed from Pinata")
    else:
        logger.error(f"Failed to unpin CID {cid}: {response.status_code} - {response.text}")
        # record_action(cid, "unpin_failed", f"Error: {response.status_code} - {response.text}")
    return response.status_code == 200

def verify_revocation(sepolia_rpc_url, contract_address, cid):
    """Verify revocation status"""
    w3 = Web3(Web3.HTTPProvider(sepolia_rpc_url))
    if not w3.is_connected():
        raise ConnectionError("Failed to connect to Sepolia. Check SEPOLIA_RPC_URL.")

    contract_abi = [
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

    contract = w3.eth.contract(address=contract_address, abi=contract_abi)

    logger.info(f"Verifying revocation status for CID: {cid}")
    is_revoked = contract.functions.isRevoked(cid).call()
    logger.info(f"Revocation status: {is_revoked}")
    try:
        key = contract.functions.getKey(cid).call()
        logger.info(f"Retrieved key: {key}")
        # record_action(cid, "key_access", "Unexpected key retrieval after revocation")
    except Exception as e:
        logger.info(f"Key retrieval failed (as expected after revocation): {e}")
        # record_action(cid, "key_access_failed", "Key access blocked as expected")
    return is_revoked

# from web3 import Web3
# import requests
# from dotenv import load_dotenv
# import os
# import time
# import logging
# from record_action import record_action

# # Set up logging
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# logger = logging.getLogger(__name__)

# # Load environment variables
# load_dotenv()
# SEPOLIA_RPC_URL = os.getenv("SEPOLIA_RPC_URL")
# PRIVATE_KEY = os.getenv("PRIVATE_KEY")
# CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")
# CID = os.getenv("IMAGE_CID")
# PINATA_API_KEY = os.getenv("PINATA_API_KEY")
# PINATA_SECRET_KEY = os.getenv("PINATA_SECRET_KEY")

# # Debug: Print loaded values
# print(f"Using CONTRACT_ADDRESS: {CONTRACT_ADDRESS}")
# print(f"Using CID: {CID}")

# if not all([SEPOLIA_RPC_URL, PRIVATE_KEY, CONTRACT_ADDRESS, CID, PINATA_API_KEY, PINATA_SECRET_KEY]):
#     raise ValueError("Missing environment variables. Check .env file.")

# # Connect to Sepolia
# w3 = Web3(Web3.HTTPProvider(SEPOLIA_RPC_URL))
# if not w3.is_connected():
#     raise ConnectionError("Failed to connect to Sepolia. Check SEPOLIA_RPC_URL.")

# account = w3.eth.account.from_key(PRIVATE_KEY)

# # Load contract ABI
# contract_abi = [
#     {
#         "inputs": [{"internalType": "string", "name": "cid", "type": "string"}],
#         "name": "revokeAccess",
#         "outputs": [],
#         "stateMutability": "nonpayable",
#         "type": "function"
#     },
#     {
#         "anonymous": False,
#         "inputs": [{"indexed": False, "internalType": "string", "name": "cid", "type": "string"}],
#         "name": "AccessRevoked",
#         "type": "event"
#     },
#     {
#         "inputs": [{"internalType": "string", "name": "cid", "type": "string"}],
#         "name": "isRevoked",
#         "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
#         "stateMutability": "view",
#         "type": "function"
#     }
# ]

# contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=contract_abi)

# # Revoke access via smart contract
# def revoke_access_on_chain():
#     logger.info(f"Attempting to revoke access for CID: {CID}")
#     nonce = w3.eth.get_transaction_count(account.address)
#     logger.info(f"Using nonce: {nonce}")  # Debug nonce
#     tx = contract.functions.revokeAccess(CID).build_transaction({
#         'from': account.address,
#         'nonce': nonce,
#         'gas': 300000,  # Increased from 200,000
#         'gasPrice': w3.to_wei('50', 'gwei')  # Increased from 20 Gwei
#     })
#     signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
#     tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
#     logger.info(f"Transaction sent: {tx_hash.hex()}")
#     receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)  # Increased to 300 seconds
#     logger.info(f"Access revoked on-chain: {tx_hash.hex()}")
#     logger.info(f"Transaction confirmed in block: {receipt.blockNumber}")
#     record_action(CID, "revoked", f"Transaction hash: {tx_hash.hex()}")

# # Unpin from Pinata
# def unpin_from_pinata():
#     logger.info(f"Attempting to unpin CID: {CID} from Pinata")
#     headers = {
#         "pinata_api_key": PINATA_API_KEY,
#         "pinata_secret_api_key": PINATA_SECRET_KEY
#     }
#     response = requests.delete(f"https://api.pinata.cloud/pinning/unpin/{CID}", headers=headers)
#     if response.status_code == 200:
#         logger.info(f"Successfully unpinned CID {CID} from Pinata")
#         record_action(CID, "unpinned", "Removed from Pinata")
#     else:
#         logger.error(f"Failed to unpin CID {CID}: {response.status_code} - {response.text}")
#         record_action(CID, "unpin_failed", f"Error: {response.status_code} - {response.text}")

# # Verify revocation
# def verify_revocation():
#     logger.info(f"Verifying revocation status for CID: {CID}")
#     is_revoked = contract.functions.isRevoked(CID).call()
#     logger.info(f"Revocation status: {is_revoked}")
#     try:
#         key = contract.functions.getKey(CID).call()
#         logger.info(f"Retrieved key: {key}")
#         record_action(CID, "key_access", "Unexpected key retrieval after revocation")
#     except Exception as e:
#         logger.info(f"Key retrieval failed (as expected after revocation): {e}")
#         record_action(CID, "key_access_failed", "Key access blocked as expected")

# def revoke_access():
#     logger.info(f"Starting revocation process for CID: {CID}")
#     try:
#         revoke_access_on_chain()
#         time.sleep(5)
#         unpin_from_pinata()
#         verify_revocation()
#         local_path = "data/encrypted_image.bin"
#         if os.path.exists(local_path):
#             os.remove(local_path)
#             logger.info("Local encrypted file deleted")
#             record_action(CID, "local_file_deleted", "Local encrypted file removed")
#         logger.info("Kill switch activated successfully!")
#     except Exception as e:
#         logger.error(f"Revocation failed: {e}")
#         record_action(CID, "revocation_failed", f"Error: {str(e)}")

# if __name__ == "__main__":
#     revoke_access()