from web3 import Web3
from dotenv import load_dotenv
import os

load_dotenv()
SEPOLIA_RPC_URL = os.getenv("SEPOLIA_RPC_URL")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")

w3 = Web3(Web3.HTTPProvider(SEPOLIA_RPC_URL))
account = w3.eth.account.from_key(PRIVATE_KEY)

nonce = w3.eth.get_transaction_count(account.address)
tx = {
    'to': account.address,
    'value': 0,
    'gas': 21000,
    'gasPrice': w3.to_wei('100', 'gwei'),
    'nonce': nonce,
    'chainId': 11155111  # Sepolia chain ID
}
signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
print(f"Cancel transaction sent: {tx_hash.hex()}")