from web3 import Web3
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def store_key_on_chain(sepolia_rpc_url, private_key, contract_address, cid, key, retries=3, delay=5):
    """Store an encryption key on the blockchain with retry logic and detailed error logging"""
    max_connection_retries = 3
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
            "inputs": [
                {"internalType": "string", "name": "cid", "type": "string"},
                {"internalType": "string", "name": "key", "type": "string"}
            ],
            "name": "storeKey",
            "outputs": [],
            "stateMutability": "nonpayable",
            "type": "function"
        },
        {
            "anonymous": False,
            "inputs": [
                {"indexed": True, "internalType": "string", "name": "cid", "type": "string"},
                {"indexed": False, "internalType": "string", "name": "key", "type": "string"}
            ],
            "name": "KeyStored",
            "type": "event"
        }
    ]

    contract = w3.eth.contract(address=contract_address, abi=contract_abi)

    logger.info(f"Storing key for CID: {cid}")

    for attempt in range(retries):
        try:
            nonce = w3.eth.get_transaction_count(account.address, 'pending')
            logger.info(f"Using nonce: {nonce} for attempt {attempt + 1}")
            gas_price = int(w3.eth.gas_price * 1.5)
            logger.info(f"Using gas price: {gas_price} wei")

            # Estimate gas and increase the limit
            gas_estimate = contract.functions.storeKey(cid, key).estimate_gas({
                'from': account.address,
            })
            gas_limit = int(gas_estimate * 1.5)  # 50% buffer
            logger.info(f"Estimated gas: {gas_estimate}, Using gas limit: {gas_limit}")

            tx = contract.functions.storeKey(cid, key).build_transaction({
                'from': account.address,
                'nonce': nonce,
                'gas': max(gas_limit, 300000),  # Ensure at least 300,000 gas
                'gasPrice': gas_price,
                'chainId': 11155111  # Sepolia chain ID
            })

            # Estimate transaction cost
            tx_cost = gas_limit * gas_price
            logger.info(f"Estimated transaction cost: {w3.from_wei(tx_cost, 'ether')} ETH")
            if balance < tx_cost:
                raise ValueError(f"Insufficient funds: Account balance is {w3.from_wei(balance, 'ether')} ETH, but transaction requires {w3.from_wei(tx_cost, 'ether')} ETH")

            signed_tx = w3.eth.account.sign_transaction(tx, private_key)
            tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)

            if receipt.status == 1:
                logger.info(f"Key stored on-chain for CID {cid}: {tx_hash.hex()}")
                return tx_hash.hex()
            else:
                logger.error(f"Transaction failed. Receipt: {receipt}")
                raise Exception(f"Transaction failed: {receipt.get('status', 'Unknown error')}, Revert reason: {receipt.get('revertReason', 'Not provided')}")

        except Exception as e:
            if "replacement transaction underpriced" in str(e) and attempt < retries - 1:
                logger.warning(f"Attempt {attempt + 1} failed with underpriced error. Retrying in {delay} seconds...")
                time.sleep(delay)
                continue
            logger.error(f"Failed to store key on chain after {retries} attempts: {str(e)}")
            raise Exception(f"Failed to store key on chain after {retries} attempts: {str(e)}")
        
# from web3 import Web3
# from dotenv import load_dotenv
# import os

# # Load environment variables
# load_dotenv()
# SEPOLIA_RPC_URL = os.getenv("SEPOLIA_RPC_URL")
# PRIVATE_KEY = os.getenv("PRIVATE_KEY")
# CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")
# IMAGE_CID = os.getenv("IMAGE_CID")
# ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")

# # Debug: Print loaded values
# print(f"Using CONTRACT_ADDRESS: {CONTRACT_ADDRESS}")
# print(f"Using IMAGE_CID: {IMAGE_CID}")
# print(f"Using ENCRYPTION_KEY: {ENCRYPTION_KEY}")

# if not all([SEPOLIA_RPC_URL, PRIVATE_KEY, CONTRACT_ADDRESS, IMAGE_CID, ENCRYPTION_KEY]):
#     raise ValueError("Missing environment variables. Check .env file.")

# # Connect to Sepolia
# w3 = Web3(Web3.HTTPProvider(SEPOLIA_RPC_URL))
# if not w3.is_connected():
#     raise ConnectionError("Failed to connect to Sepolia. Check SEPOLIA_RPC_URL.")

# account = w3.eth.account.from_key(PRIVATE_KEY)

# # Load contract ABI
# contract_abi = [
#     {
#         "inputs": [
#             {"internalType": "string", "name": "cid", "type": "string"},
#             {"internalType": "string", "name": "key", "type": "string"}
#         ],
#         "name": "storeKey",
#         "outputs": [],
#         "stateMutability": "nonpayable",
#         "type": "function"
#     }
# ]

# contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=contract_abi)

# # Store the key
# nonce = w3.eth.get_transaction_count(account.address)
# tx = contract.functions.storeKey(IMAGE_CID, ENCRYPTION_KEY).build_transaction({
#     'from': account.address,
#     'nonce': nonce,
#     'gas': 200000,
#     'gasPrice': w3.to_wei('20', 'gwei')
# })
# signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
# tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
# receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)

# print(f"Encryption key stored on-chain: {tx_hash.hex()}")