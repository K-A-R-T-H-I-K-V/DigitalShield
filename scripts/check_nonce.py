from web3 import Web3
from dotenv import load_dotenv
import os

load_dotenv()
SEPOLIA_RPC_URL = os.getenv("SEPOLIA_RPC_URL")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")

w3 = Web3(Web3.HTTPProvider(SEPOLIA_RPC_URL))
account = w3.eth.account.from_key(PRIVATE_KEY)
nonce = w3.eth.get_transaction_count(account.address)
pending_nonce = w3.eth.get_transaction_count(account.address, "pending")

print(f"Account: {account.address}")
print(f"Nonce: {nonce}")
print(f"Pending Nonce: {pending_nonce}")