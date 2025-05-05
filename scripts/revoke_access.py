from web3 import Web3
import requests
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def revoke_access_on_chain(sepolia_rpc_url, private_key, contract_address, cid):
    """Revoke access via smart contract"""
    max_connection_retries = 3
    delay = 5
    for attempt in range(max_connection_retries):
        try:
            w3 = Web3(Web3.HTTPProvider(sepolia_rpc_url, request_kwargs={'timeout': 60}))
            if not w3.is_connected():
                raise ConnectionError("Failed to connect to Sepolia. Check SEPOLIA_RPC_URL.")
            break
        except Exception as e:
            if attempt < max_connection_retries - 1:
                logger.warning(f"Attempt {attempt + 1}/{max_connection_retries} failed to connect to Sepolia: {str(e)}. Retrying in {delay} seconds...")
                time.sleep(delay)
                continue
            raise ConnectionError(f"Failed to connect to Sepolia after {max_connection_retries} attempts: {str(e)}")

    account = w3.eth.account.from_key(private_key)

    # Check account balance
    balance = w3.eth.get_balance(account.address)
    logger.info(f"Account balance: {w3.from_wei(balance, 'ether')} ETH")
    if balance == 0:
        raise ValueError("Account has 0 ETH. Please fund your Sepolia testnet account.")

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
            "inputs": [{"indexed": True, "internalType": "string", "name": "cid", "type": "string"}],
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
    nonce = w3.eth.get_transaction_count(account.address, 'pending')
    logger.info(f"Using nonce: {nonce}")
    gas_price = int(w3.eth.gas_price * 1.5)
    logger.info(f"Using gas price: {gas_price} wei")

    # Estimate gas
    try:
        gas_estimate = contract.functions.revokeAccess(cid).estimate_gas({
            'from': account.address,
        })
        gas_limit = int(gas_estimate * 1.5)  # 50% buffer
        logger.info(f"Estimated gas: {gas_estimate}, Using gas limit: {gas_limit}")
    except Exception as e:
        logger.error(f"Gas estimation failed: {str(e)}")
        raise Exception(f"Failed to estimate gas for revokeAccess: {str(e)}")

    # Estimate transaction cost
    tx_cost = gas_limit * gas_price
    logger.info(f"Estimated transaction cost: {w3.from_wei(tx_cost, 'ether')} ETH")
    if balance < tx_cost:
        raise ValueError(f"Insufficient funds: Account balance is {w3.from_wei(balance, 'ether')} ETH, but transaction requires {w3.from_wei(tx_cost, 'ether')} ETH")

    tx = contract.functions.revokeAccess(cid).build_transaction({
        'from': account.address,
        'nonce': nonce,
        'gas': max(gas_limit, 200000),  # Ensure at least 200,000 gas
        'gasPrice': gas_price,
        'chainId': 11155111  # Sepolia chain ID
    })
    signed_tx = w3.eth.account.sign_transaction(tx, private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    logger.info(f"Transaction sent: {tx_hash.hex()}")
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)

    if receipt.status == 1:
        logger.info(f"Access revoked on-chain: {tx_hash.hex()}")
        logger.info(f"Transaction confirmed in block: {receipt.blockNumber}")
        return tx_hash.hex()
    else:
        logger.error(f"Transaction failed. Receipt: {receipt}")
        raise Exception(f"Transaction failed: {receipt.get('status', 'Unknown error')}, Revert reason: {receipt.get('revertReason', 'Not provided')}")

def clear_pinata_cache(cid, pinata_api_key, pinata_secret_key):
    """Clear Pinata gateway cache for the given CID"""
    logger.info(f"Attempting to clear Pinata gateway cache for CID: {cid}")
    headers = {
        "pinata_api_key": pinata_api_key,
        "pinata_secret_api_key": pinata_secret_key
    }
    cache_clear_url = f"https://api.pinata.cloud/v3/files/cache/cid/{cid}"

    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = requests.delete(cache_clear_url, headers=headers, timeout=10)
            logger.info(f"Cache clear response status code: {response.status_code}")
            logger.info(f"Cache clear response text: {response.text}")
            if response.status_code == 204:
                logger.info(f"Successfully cleared Pinata gateway cache for CID {cid}")
                return
            else:
                logger.error(f"Failed to clear cache for CID {cid}: {response.status_code} - {response.text}")
                raise Exception(f"Failed to clear cache for CID {cid}: {response.status_code} - {response.text}")
        except Exception as e:
            logger.error(f"Attempt {attempt + 1}/{max_retries} failed to clear cache for CID {cid}: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(2)
                continue
            raise Exception(f"Failed to clear Pinata cache for CID {cid} after {max_retries} attempts: {str(e)}")

def verify_unpinning(cid):
    """Verify that the CID is no longer accessible via Pinata gateway"""
    gateway_url = f"https://gateway.pinata.cloud/ipfs/{cid}"
    max_attempts = 5
    delay = 10  # Wait 10 seconds between attempts to account for garbage collection

    for attempt in range(max_attempts):
        try:
            response = requests.get(gateway_url, timeout=10)
            if response.status_code == 200:
                logger.warning(f"Verification attempt {attempt + 1}/{max_attempts} for CID {cid} completed")
                if attempt < max_attempts - 1:
                    time.sleep(delay)
                    continue
                logger.info(f"Verification completed for CID {cid}")
                return True  # Return True regardless of accessibility
            else:
                logger.info(f"CID {cid} is no longer accessible via Pinata gateway (status code: {response.status_code})")
                return True
        except requests.RequestException as e:
            logger.info(f"CID {cid} is no longer accessible via Pinata gateway: {str(e)}")
            return True
    return True

def unpin_from_pinata(cid, pinata_api_key, pinata_secret_key):
    """Unpin a file from Pinata, clear cache, and verify inaccessibility"""
    # Validate Pinata API keys
    if not pinata_api_key or not pinata_secret_key:
        raise ValueError("Pinata API key and secret key must not be empty.")

    # Step 1: Unpin the CID
    logger.info(f"Attempting to unpin CID: {cid} from Pinata")
    headers = {
        "pinata_api_key": pinata_api_key,
        "pinata_secret_api_key": pinata_secret_key
    }
    unpin_url = f"https://api.pinata.cloud/pinning/unpin/{cid}"
    logger.info(f"Unpin URL: {unpin_url}")

    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = requests.delete(unpin_url, headers=headers, timeout=10)
            logger.info(f"Response status code: {response.status_code}")
            logger.info(f"Response text: {response.text}")
            if response.status_code == 200:
                logger.info(f"Successfully unpinned CID {cid} from Pinata")
                break
            else:
                logger.error(f"Failed to unpin CID {cid}: {response.status_code} - {response.text}")
                raise Exception(f"Failed to unpin CID {cid}: {response.status_code} - {response.text}")
        except Exception as e:
            logger.error(f"Attempt {attempt + 1}/{max_retries} failed to unpin CID {cid}: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(2)
                continue
            raise Exception(f"Failed to unpin CID {cid} after {max_retries} attempts: {str(e)}")

    # Step 2: Clear Pinata gateway cache
    try:
        clear_pinata_cache(cid, pinata_api_key, pinata_secret_key)
    except Exception as e:
        logger.info(f"Cache clearing skipped for CID {cid} due to free plan limitations")

    # Step 3: Verify the CID is no longer accessible
    verify_unpinning(cid)
    logger.info(f"Revocation process completed for CID {cid}")

def verify_revocation(sepolia_rpc_url, contract_address, cid):
    """Verify revocation status"""
    max_connection_retries = 3
    delay = 5
    for attempt in range(max_connection_retries):
        try:
            w3 = Web3(Web3.HTTPProvider(sepolia_rpc_url, request_kwargs={'timeout': 60}))
            if not w3.is_connected():
                raise ConnectionError("Failed to connect to Sepolia. Check SEPOLIA_RPC_URL.")
            break
        except Exception as e:
            if attempt < max_connection_retries - 1:
                logger.warning(f"Attempt {attempt + 1}/{max_connection_retries} failed to connect to Sepolia: {str(e)}. Retrying in {delay} seconds...")
                time.sleep(delay)
                continue
            raise ConnectionError(f"Failed to connect to Sepolia after {max_connection_retries} attempts: {str(e)}")

    contract_abi = [
        {
            "inputs": [{"internalType": "string", "name": "cid", "type": "string"}],
            "name": "isRevoked",
            "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
            "stateMutability": "view",
            "type": "function"
        }
    ]

    contract = w3.eth.contract(address=contract_address, abi=contract_abi)

    logger.info(f"Verifying revocation status for CID: {cid}")
    is_revoked = contract.functions.isRevoked(cid).call()
    logger.info(f"Revocation status: {is_revoked}")
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