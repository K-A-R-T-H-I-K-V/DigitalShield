from web3 import Web3
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def add_record_on_chain(sepolia_rpc_url, private_key, contract_address, cid, terms="No AI training", retries=3, delay=5):
    """Add a record to the blockchain with retry logic"""
    w3 = Web3(Web3.HTTPProvider(sepolia_rpc_url))
    if not w3.is_connected():
        raise ConnectionError("Failed to connect to Sepolia. Check SEPOLIA_RPC_URL.")

    account = w3.eth.account.from_key(private_key)

    contract_abi = [
        {
            "inputs": [
                {"internalType": "string", "name": "cid", "type": "string"},
                {"internalType": "string", "name": "terms", "type": "string"}
            ],
            "name": "addRecord",
            "outputs": [],
            "stateMutability": "nonpayable",
            "type": "function"
        }
    ]

    contract = w3.eth.contract(address=contract_address, abi=contract_abi)

    for attempt in range(retries):
        try:
            # Get the latest nonce, including pending transactions
            nonce = w3.eth.get_transaction_count(account.address, 'pending')
            logger.info(f"Using nonce: {nonce} for attempt {attempt + 1}")

            # Use dynamic gas price, increased by 50%
            gas_price = int(w3.eth.gas_price * 1.5)
            logger.info(f"Using gas price: {gas_price} wei")

            tx = contract.functions.addRecord(cid, terms).build_transaction({
                'from': account.address,
                'nonce': nonce,
                'gas': 200000,
                'gasPrice': gas_price,
                'chainId': 11155111  # Sepolia chain ID
            })

            # Sign and send the transaction
            signed_tx = w3.eth.account.sign_transaction(tx, private_key)
            tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)  # Updated to raw_transaction
            receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)

            if receipt.status == 1:
                logger.info(f"Record added on-chain: {tx_hash.hex()}")
                return tx_hash.hex()
            else:
                raise Exception("Transaction failed")

        except Exception as e:
            if "replacement transaction underpriced" in str(e) and attempt < retries - 1:
                logger.warning(f"Attempt {attempt + 1} failed with underpriced error. Retrying in {delay} seconds...")
                time.sleep(delay)
                continue
            raise Exception(f"Failed to add record on chain after {retries} attempts: {str(e)}")