import os
import cv2
import numpy as np
from PIL import Image
from io import BytesIO
from scripts.poison_generator import NightshadePoisoner
from scripts.verify_poisoning import PoisoningVerifier
from scripts.watermark import watermark_image
from scripts.verify_watermark import verify_watermark
from scripts.encrypt import encrypt_image
from scripts.decrypt import decrypt_image
from scripts.upload_pinata import upload_to_pinata
from scripts.store_key import store_key_on_chain
from scripts.add_record import add_record_on_chain
from scripts.revoke_access import revoke_access_on_chain, unpin_from_pinata, verify_revocation
from dotenv import load_dotenv
import base64
import logging
import time
import shutil
from web3 import Web3
from web3.exceptions import ContractLogicError

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
SEPOLIA_RPC_URL = os.getenv("SEPOLIA_RPC_URL")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")
PINATA_API_KEY = os.getenv("PINATA_API_KEY")
PINATA_SECRET_KEY = os.getenv("PINATA_SECRET_KEY")
SECRET = os.getenv("SECRET")

# Function to resize image to 224x224 while preserving aspect ratio and padding
def resize_image(image_data: bytes, target_size: tuple = (224, 224)) -> str:
    with Image.open(BytesIO(image_data)) as img:
        if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
            img = img.convert("RGB")

        original_width, original_height = img.size
        target_width, target_height = target_size
        aspect_ratio = min(target_width / original_width, target_height / original_height)

        new_width = int(original_width * aspect_ratio)
        new_height = int(original_height * aspect_ratio)
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

        new_img = Image.new("RGB", target_size, (0, 0, 0))
        offset = ((target_width - new_width) // 2, (target_height - new_height) // 2)
        new_img.paste(img, offset)

        os.makedirs("data/resized", exist_ok=True)
        resized_path = os.path.join("data/resized", "resized_image.jpg")
        new_img.save(resized_path, "JPEG")

    return resized_path

def process_image(image_path, is_public=False, secret=None):
    """Process an image through poisoning, watermarking, encryption (if private), and blockchain storage"""
    if not all([SEPOLIA_RPC_URL, PRIVATE_KEY, CONTRACT_ADDRESS, PINATA_API_KEY, PINATA_SECRET_KEY]):
        raise ValueError("Missing environment variables. Check .env file.")

    if secret is None:
        secret = SECRET
        if not secret:
            raise ValueError("No secret provided and SECRET environment variable is missing.")

    # Convert is_public to boolean if it's a string
    if isinstance(is_public, str):
        is_public = is_public.lower() == "true"
    logger.info(f"Processed isPublic: {is_public}")

    result = {}

    with open(image_path, "rb") as f:
        image_data = f.read()

    resized_path = resize_image(image_data, target_size=(224, 224))
    logger.info(f"Image resized to 224x224 and saved to: {resized_path}")

    poisoned_path = None
    watermarked_path = None
    encrypted_path = None

    try:
        poisoner = NightshadePoisoner()
        poisoned_img = poisoner.poison_image(resized_path)
        if poisoned_img is None:
            raise Exception("Failed to poison image")

        poisoned_path = os.path.join("data/poisoned", "poisoned_image.jpg")
        os.makedirs("data/poisoned", exist_ok=True)
        cv2.imwrite(poisoned_path, cv2.cvtColor(poisoned_img, cv2.COLOR_RGB2BGR))
        logger.info(f"Poisoned image saved to: {poisoned_path}")

        verifier = PoisoningVerifier()
        is_successful, psnr = verifier.verify(resized_path, poisoned_path)
        if not is_successful:
            raise Exception("Poisoning verification failed")
        logger.info(f"Poisoning verification successful with PSNR: {psnr:.2f} dB")

        watermarked_path = os.path.join("data/watermarked", "watermarked_image.png")
        os.makedirs("data/watermarked", exist_ok=True)
        watermark_image(poisoned_path, watermarked_path, secret)
        logger.info(f"Image watermarked and saved to: {watermarked_path}")

        if not verify_watermark(watermarked_path, secret):
            raise Exception("Watermark verification failed")
        logger.info("Watermark verification successful")

        if is_public:
            # For public images, upload the watermarked image directly to IPFS
            public_cid = upload_to_pinata(watermarked_path, PINATA_API_KEY, PINATA_SECRET_KEY)
            try:
                # Use a placeholder terms string
                terms = "public_image_terms"
                tx_hash = add_record_on_chain(SEPOLIA_RPC_URL, PRIVATE_KEY, CONTRACT_ADDRESS, public_cid, terms)
                logger.info(f"Record added on chain for public CID {public_cid}, Transaction Hash: {tx_hash}")
                result["publicCid"] = public_cid
            except Exception as e:
                logger.error(f"Failed to add record on chain for public CID {public_cid}: {str(e)}")
                result["publicCid"] = public_cid
                result["publicChainError"] = str(e)
        else:
            # For private images, encrypt and store the key on-chain
            encrypted_dir = "data/encrypted"
            os.makedirs(encrypted_dir, exist_ok=True)
            encrypted_path = os.path.join(encrypted_dir, "encrypted_" + os.path.basename(image_path) + ".bin")
            key = encrypt_image(watermarked_path, encrypted_path)
            encoded_key = base64.b64encode(key).decode('utf-8')
            logger.info(f"Encryption key: {encoded_key}")

            encrypted_cid = upload_to_pinata(encrypted_path, PINATA_API_KEY, PINATA_SECRET_KEY)
            result["encryptedCid"] = encrypted_cid
            result["encryptionKey"] = encoded_key

            try:
                tx_hash = store_key_on_chain(SEPOLIA_RPC_URL, PRIVATE_KEY, CONTRACT_ADDRESS, encrypted_cid, encoded_key)
                logger.info(f"Stored encryption key on chain for CID: {encrypted_cid}, Transaction Hash: {tx_hash}")
            except Exception as e:
                logger.error(f"Failed to store encryption key on chain for CID {encrypted_cid}: {str(e)}")
                result["chainError"] = str(e)

    finally:
        if poisoned_path and os.path.exists(poisoned_path):
            os.remove(poisoned_path)
            logger.info(f"Cleaned up poisoned file: {poisoned_path}")
        poisoned_dir = "data/poisoned"
        if os.path.exists(poisoned_dir) and not os.listdir(poisoned_dir):
            shutil.rmtree(poisoned_dir)
            logger.info(f"Removed empty directory: {poisoned_dir}")

        if watermarked_path and os.path.exists(watermarked_path):
            os.remove(watermarked_path)
            logger.info(f"Cleaned up watermarked file: {watermarked_path}")
        watermarked_dir = "data/watermarked"
        if os.path.exists(watermarked_dir) and not os.listdir(watermarked_dir):
            shutil.rmtree(watermarked_dir)
            logger.info(f"Removed empty directory: {watermarked_dir}")

        if encrypted_path and os.path.exists(encrypted_path):
            os.remove(encrypted_path)
            logger.info(f"Cleaned up encrypted file: {encrypted_path}")
        encrypted_dir = "data/encrypted"
        if os.path.exists(encrypted_dir) and not os.listdir(encrypted_dir):
            shutil.rmtree(encrypted_dir)
            logger.info(f"Removed empty directory: {encrypted_dir}")

        if resized_path and os.path.exists(resized_path):
            os.remove(resized_path)
            logger.info(f"Cleaned up resized file: {resized_path}")
        resized_dir = "data/resized"
        if os.path.exists(resized_dir) and not os.listdir(resized_dir):
            shutil.rmtree(resized_dir)
            logger.info(f"Removed empty directory: {resized_dir}")

    return result

def revoke_access(cid):
    """Revoke access to an image"""
    if not all([SEPOLIA_RPC_URL, PRIVATE_KEY, CONTRACT_ADDRESS, PINATA_API_KEY, PINATA_SECRET_KEY]):
        raise ValueError("Missing environment variables. Check .env file.")

    logger.info(f"Revoking access for CID: {cid}")
    result = {}

    # Step 1: Check if the CID is private or public
    w3 = Web3(Web3.HTTPProvider(SEPOLIA_RPC_URL))
    if not w3.is_connected():
        raise ConnectionError("Failed to connect to Sepolia. Check SEPOLIA_RPC_URL.")

    contract_abi = [
        {
            "inputs": [{"internalType": "string", "name": "cid", "type": "string"}],
            "name": "getKey",
            "outputs": [{"internalType": "string", "name": "", "type": "string"}],
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
        }
    ]
    contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=contract_abi)

    logger.info(f"Checking CID {cid} with contract address: {CONTRACT_ADDRESS}")
    is_private = False
    try:
        key = contract.functions.getKey(cid).call()
        logger.info(f"CID {cid} has a key; treating as private CID")
        is_private = True
        # Check if already revoked
        if contract.functions.isRevoked(cid).call():
            logger.info(f"CID {cid} is already revoked")
            return
        try:
            tx_hash = revoke_access_on_chain(SEPOLIA_RPC_URL, PRIVATE_KEY, CONTRACT_ADDRESS, cid)
            logger.info(f"Access revoked on chain for CID {cid}, Transaction Hash: {tx_hash}")
        except Exception as e:
            logger.error(f"Error during on-chain revocation for CID {cid}: {str(e)}")
            result["chainError"] = str(e)
    except ContractLogicError as e:
        if "No key found for this CID" in str(e):
            logger.info(f"CID {cid} has no key; treating as public CID")
        elif "Access to this CID has been revoked" in str(e):
            logger.info(f"CID {cid} is already revoked")
            return  # Exit early if already revoked
        else:
            logger.error(f"Unexpected error checking key for CID {cid}: {str(e)}")
            result["chainError"] = str(e)
    except Exception as e:
        logger.error(f"Unexpected error checking key for CID {cid}: {str(e)}")
        result["chainError"] = str(e)

    # Step 2: Unpin from Pinata (for both public and private CIDs)
    try:
        unpin_from_pinata(cid, PINATA_API_KEY, PINATA_SECRET_KEY)
        logger.info(f"File unpinned from Pinata for CID {cid}")
    except Exception as e:
        logger.error(f"Error during unpinning for CID {cid}: {str(e)}")
        result["unpinError"] = str(e)

    # Step 3: Verify revocation status for private CIDs
    if is_private and 'chainError' not in result:
        try:
            is_revoked = verify_revocation(SEPOLIA_RPC_URL, CONTRACT_ADDRESS, cid)
            if is_revoked:
                logger.info(f"Revocation verified successfully for CID {cid}")
            else:
                logger.error(f"Revocation verification failed for CID {cid}: CID not marked as revoked")
                result["verificationError"] = "CID not marked as revoked"
        except Exception as e:
            logger.error(f"Error during revocation verification for CID {cid}: {str(e)}")
            result["verificationError"] = str(e)
    else:
        logger.info(f"Skipping revocation verification for CID {cid} (public or error occurred)")

    # Step 4: Clean up local file if exists
    local_path = f"data/encrypted/encrypted_{os.path.basename(cid)}.bin"
    if os.path.exists(local_path):
        os.remove(local_path)
        logger.info(f"Local encrypted file deleted for CID {cid}")

    if result:
        raise Exception(f"Revocation process encountered errors: {result}")
    logger.info(f"Access revocation completed successfully for CID {cid}")

if __name__ == "__main__":
    os.makedirs('data/clean', exist_ok=True)
    test_img = np.random.randint(0, 255, (512, 512, 3), dtype=np.uint8)
    test_path = os.path.join('data/clean', 'test.jpg')
    cv2.imwrite(test_path, test_img)

    result = process_image(test_path, is_public=True)
    print("Result:", result)
    
# import os
# import cv2
# import numpy as np
# from PIL import Image
# from io import BytesIO
# from scripts.poison_generator import NightshadePoisoner
# from scripts.verify_poisoning import PoisoningVerifier
# from scripts.watermark import watermark_image
# from scripts.verify_watermark import verify_watermark
# from scripts.encrypt import encrypt_image
# from scripts.decrypt import decrypt_image
# from scripts.upload_pinata import upload_to_pinata
# from scripts.store_key import store_key_on_chain
# from scripts.add_record import add_record_on_chain
# from scripts.revoke_access import revoke_access_on_chain, unpin_from_pinata, verify_revocation
# from dotenv import load_dotenv
# import base64
# import logging
# import time
# import shutil
# from web3 import Web3
# from web3.exceptions import ContractLogicError

# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# logger = logging.getLogger(__name__)

# # Load environment variables
# load_dotenv()
# SEPOLIA_RPC_URL = os.getenv("SEPOLIA_RPC_URL")
# PRIVATE_KEY = os.getenv("PRIVATE_KEY")
# CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")
# PINATA_API_KEY = os.getenv("PINATA_API_KEY")
# PINATA_SECRET_KEY = os.getenv("PINATA_SECRET_KEY")
# SECRET = os.getenv("SECRET")

# # Function to resize image to 224x224 while preserving aspect ratio and padding
# def resize_image(image_data: bytes, target_size: tuple = (224, 224)) -> str:
#     with Image.open(BytesIO(image_data)) as img:
#         if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
#             img = img.convert("RGB")

#         original_width, original_height = img.size
#         target_width, target_height = target_size
#         aspect_ratio = min(target_width / original_width, target_height / original_height)

#         new_width = int(original_width * aspect_ratio)
#         new_height = int(original_height * aspect_ratio)
#         img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

#         new_img = Image.new("RGB", target_size, (0, 0, 0))
#         offset = ((target_width - new_width) // 2, (target_height - new_height) // 2)
#         new_img.paste(img, offset)

#         os.makedirs("data/resized", exist_ok=True)
#         resized_path = os.path.join("data/resized", "resized_image.jpg")
#         new_img.save(resized_path, "JPEG")

#     return resized_path

# def process_image(image_path, is_public=False, secret=None):
#     """Process an image through poisoning, watermarking, encryption (if private), and blockchain storage"""
#     if not all([SEPOLIA_RPC_URL, PRIVATE_KEY, CONTRACT_ADDRESS, PINATA_API_KEY, PINATA_SECRET_KEY]):
#         raise ValueError("Missing environment variables. Check .env file.")

#     if secret is None:
#         secret = SECRET
#         if not secret:
#             raise ValueError("No secret provided and SECRET environment variable is missing.")

#     # Convert is_public to boolean if it's a string
#     if isinstance(is_public, str):
#         is_public = is_public.lower() == "true"
#     logger.info(f"Processed isPublic: {is_public}")

#     result = {}

#     with open(image_path, "rb") as f:
#         image_data = f.read()

#     resized_path = resize_image(image_data, target_size=(224, 224))
#     logger.info(f"Image resized to 224x224 and saved to: {resized_path}")

#     poisoned_path = None
#     watermarked_path = None
#     encrypted_path = None

#     try:
#         poisoner = NightshadePoisoner()
#         poisoned_img = poisoner.poison_image(resized_path)
#         if poisoned_img is None:
#             raise Exception("Failed to poison image")

#         poisoned_path = os.path.join("data/poisoned", "poisoned_image.jpg")
#         os.makedirs("data/poisoned", exist_ok=True)
#         cv2.imwrite(poisoned_path, cv2.cvtColor(poisoned_img, cv2.COLOR_RGB2BGR))
#         logger.info(f"Poisoned image saved to: {poisoned_path}")

#         verifier = PoisoningVerifier()
#         is_successful, psnr = verifier.verify(resized_path, poisoned_path)
#         if not is_successful:
#             raise Exception("Poisoning verification failed")
#         logger.info(f"Poisoning verification successful with PSNR: {psnr:.2f} dB")

#         watermarked_path = os.path.join("data/watermarked", "watermarked_image.png")
#         os.makedirs("data/watermarked", exist_ok=True)
#         watermark_image(poisoned_path, watermarked_path, secret)
#         logger.info(f"Image watermarked and saved to: {watermarked_path}")

#         if not verify_watermark(watermarked_path, secret):
#             raise Exception("Watermark verification failed")
#         logger.info("Watermark verification successful")

#         if is_public:
#             # For public images, upload the watermarked image directly to IPFS
#             public_cid = upload_to_pinata(watermarked_path, PINATA_API_KEY, PINATA_SECRET_KEY)
#             try:
#                 # Use a placeholder terms string since user_id is removed
#                 terms = "public_image_terms"
#                 tx_hash = add_record_on_chain(SEPOLIA_RPC_URL, PRIVATE_KEY, CONTRACT_ADDRESS, public_cid, terms)
#                 logger.info(f"Record added on chain for public CID {public_cid}, Transaction Hash: {tx_hash}")
#                 result["publicCid"] = public_cid
#             except Exception as e:
#                 logger.error(f"Failed to add record on chain for public CID {public_cid}: {str(e)}")
#                 result["publicCid"] = public_cid
#                 result["publicChainError"] = str(e)
#         else:
#             # For private images, encrypt and store the key on-chain
#             encrypted_dir = "data/encrypted"
#             os.makedirs(encrypted_dir, exist_ok=True)
#             encrypted_path = os.path.join(encrypted_dir, "encrypted_" + os.path.basename(image_path) + ".bin")
#             key = encrypt_image(watermarked_path, encrypted_path)
#             encoded_key = base64.b64encode(key).decode('utf-8')
#             logger.info(f"Encryption key: {encoded_key}")

#             encrypted_cid = upload_to_pinata(encrypted_path, PINATA_API_KEY, PINATA_SECRET_KEY)
#             result["encryptedCid"] = encrypted_cid
#             result["encryptionKey"] = encoded_key

#             try:
#                 tx_hash = store_key_on_chain(SEPOLIA_RPC_URL, PRIVATE_KEY, CONTRACT_ADDRESS, encrypted_cid, encoded_key)
#                 logger.info(f"Stored encryption key on chain for CID: {encrypted_cid}, Transaction Hash: {tx_hash}")
#             except Exception as e:
#                 logger.error(f"Failed to store encryption key on chain for CID {encrypted_cid}: {str(e)}")
#                 result["chainError"] = str(e)

#     finally:
#         if poisoned_path and os.path.exists(poisoned_path):
#             os.remove(poisoned_path)
#             logger.info(f"Cleaned up poisoned file: {poisoned_path}")
#         poisoned_dir = "data/poisoned"
#         if os.path.exists(poisoned_dir) and not os.listdir(poisoned_dir):
#             shutil.rmtree(poisoned_dir)
#             logger.info(f"Removed empty directory: {poisoned_dir}")

#         if watermarked_path and os.path.exists(watermarked_path):
#             os.remove(watermarked_path)
#             logger.info(f"Cleaned up watermarked file: {watermarked_path}")
#         watermarked_dir = "data/watermarked"
#         if os.path.exists(watermarked_dir) and not os.listdir(watermarked_dir):
#             shutil.rmtree(watermarked_dir)
#             logger.info(f"Removed empty directory: {watermarked_dir}")

#         if encrypted_path and os.path.exists(encrypted_path):
#             os.remove(encrypted_path)
#             logger.info(f"Cleaned up encrypted file: {encrypted_path}")
#         encrypted_dir = "data/encrypted"
#         if os.path.exists(encrypted_dir) and not os.listdir(encrypted_dir):
#             shutil.rmtree(encrypted_dir)
#             logger.info(f"Removed empty directory: {encrypted_dir}")

#         if resized_path and os.path.exists(resized_path):
#             os.remove(resized_path)
#             logger.info(f"Cleaned up resized file: {resized_path}")
#         resized_dir = "data/resized"
#         if os.path.exists(resized_dir) and not os.listdir(resized_dir):
#             shutil.rmtree(resized_dir)
#             logger.info(f"Removed empty directory: {resized_dir}")

#     return result

# def revoke_access(cid):
#     """Revoke access to an image"""
#     if not all([SEPOLIA_RPC_URL, PRIVATE_KEY, CONTRACT_ADDRESS, PINATA_API_KEY, PINATA_SECRET_KEY]):
#         raise ValueError("Missing environment variables. Check .env file.")

#     result = {}
#     w3 = Web3(Web3.HTTPProvider(SEPOLIA_RPC_URL))
#     if not w3.is_connected():
#         raise ConnectionError("Failed to connect to Sepolia. Check SEPOLIA_RPC_URL.")

#     contract_abi = [
#         {
#             "inputs": [{"internalType": "string", "name": "cid", "type": "string"}],
#             "name": "getKey",
#             "outputs": [{"internalType": "string", "name": "", "type": "string"}],
#             "stateMutability": "view",
#             "type": "function"
#         },
#         {
#             "inputs": [{"internalType": "string", "name": "cid", "type": "string"}],
#             "name": "isRevoked",
#             "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
#             "stateMutability": "view",
#             "type": "function"
#         },
#         {
#             "inputs": [{"internalType": "string", "name": "cid", "type": "string"}],
#             "name": "revokeAccess",
#             "outputs": [],
#             "stateMutability": "nonpayable",
#             "type": "function"
#         },
#         {
#             "anonymous": False,
#             "inputs": [{"indexed": True, "internalType": "string", "name": "cid", "type": "string"}],
#             "name": "AccessRevoked",
#             "type": "event"
#         }
#     ]
#     contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=contract_abi)

#     logger.info(f"Checking CID {cid} with contract address: {CONTRACT_ADDRESS}")
#     is_private = False
#     try:
#         key = contract.functions.getKey(cid).call()
#         logger.info(f"CID {cid} has a key; treating as private CID")
#         is_private = True
#         try:
#             tx_hash = revoke_access_on_chain(SEPOLIA_RPC_URL, PRIVATE_KEY, CONTRACT_ADDRESS, cid)
#             logger.info(f"Access revoked on chain for CID {cid}, Transaction Hash: {tx_hash}")
#         except Exception as e:
#             logger.error(f"Error during on-chain revocation for CID {cid}: {str(e)}")
#             result["chainError"] = str(e)
#     except ContractLogicError as e:
#         if "No key found for this CID" in str(e):
#             logger.info(f"CID {cid} has no key; treating as public CID")
#         elif "Access to this CID has been revoked" in str(e):
#             logger.info(f"CID {cid} is already revoked")
#             return  # Exit early if already revoked
#         else:
#             logger.error(f"Unexpected error checking key for CID {cid}: {str(e)}")
#             result["chainError"] = str(e)
#     except Exception as e:
#         logger.error(f"Unexpected error checking key for CID {cid}: {str(e)}")
#         result["chainError"] = str(e)

#     # Always try to unpin from Pinata with retry logic
#     max_retries = 3
#     for attempt in range(max_retries):
#         try:
#             unpin_from_pinata(cid, PINATA_API_KEY, PINATA_SECRET_KEY)
#             logger.info(f"File unpinned from Pinata for CID {cid}")
#             break
#         except Exception as e:
#             logger.error(f"Error during unpinning for CID {cid} (attempt {attempt + 1}/{max_retries}): {str(e)}")
#             if attempt < max_retries - 1:
#                 time.sleep(2)  # Wait before retrying
#                 continue
#             result["unpinError"] = str(e)

#     # Verify revocation status for private CIDs
#     if is_private and 'chainError' not in result:
#         try:
#             is_revoked = contract.functions.isRevoked(cid).call()
#             if is_revoked:
#                 logger.info(f"Revocation verified successfully for CID {cid}")
#             else:
#                 logger.error(f"Revocation verification failed for CID {cid}: CID not marked as revoked")
#                 result["verificationError"] = "CID not marked as revoked"
#         except Exception as e:
#             logger.error(f"Error during revocation verification for CID {cid}: {str(e)}")
#             result["verificationError"] = str(e)
#     else:
#         logger.info(f"Skipping revocation verification for CID {cid} (public or error occurred)")

#     # Clean up local file if exists
#     local_path = f"data/encrypted/encrypted_{os.path.basename(cid)}.bin"
#     if os.path.exists(local_path):
#         os.remove(local_path)
#         logger.info(f"Local encrypted file deleted for CID {cid}")

#     if result:
#         raise Exception(f"Revocation process encountered errors: {result}")
#     logger.info(f"Access revocation completed successfully for CID {cid}")

# if __name__ == "__main__":
#     os.makedirs('data/clean', exist_ok=True)
#     test_img = np.random.randint(0, 255, (512, 512, 3), dtype=np.uint8)
#     test_path = os.path.join('data/clean', 'test.jpg')
#     cv2.imwrite(test_path, test_img)

#     result = process_image(test_path, is_public=True)
#     print("Result:", result)


# import os
# import cv2
# import numpy as np
# from PIL import Image
# from scripts.poison_generator import NightshadePoisoner
# from scripts.verify_poisoning import PoisoningVerifier
# from scripts.watermark import watermark_image
# from scripts.verify_watermark import verify_watermark
# from scripts.encrypt import encrypt_image
# from scripts.decrypt import decrypt_image
# from scripts.upload_pinata import upload_to_pinata
# from scripts.store_key import store_key_on_chain
# from scripts.add_record import add_record_on_chain
# from scripts.revoke_access import revoke_access_on_chain, unpin_from_pinata, verify_revocation
# from dotenv import load_dotenv
# import base64
# import logging
# import time

# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# logger = logging.getLogger(__name__)

# load_dotenv()
# SEPOLIA_RPC_URL = os.getenv("SEPOLIA_RPC_URL")
# PRIVATE_KEY = os.getenv("PRIVATE_KEY")
# CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")
# PINATA_API_KEY = os.getenv("PINATA_API_KEY")
# PINATA_SECRET_KEY = os.getenv("PINATA_SECRET_KEY")
# SECRET = os.getenv("SECRET")

# # Function to resize image to 224x224 while preserving aspect ratio and padding
# def resize_and_pad_image(input_path: str, output_path: str, target_size: tuple = (224, 224)):
#     with Image.open(input_path) as img:
#         # Convert to RGB if the image has an alpha channel (e.g., PNG)
#         if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
#             img = img.convert("RGB")

#         # Calculate the aspect ratio
#         original_width, original_height = img.size
#         target_width, target_height = target_size
#         aspect_ratio = min(target_width / original_width, target_height / original_height)

#         # Resize while preserving aspect ratio
#         new_width = int(original_width * aspect_ratio)
#         new_height = int(original_height * aspect_ratio)
#         img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

#         # Create a new image with the target size and a black background
#         new_img = Image.new("RGB", target_size, (0, 0, 0))  # Black padding
#         # Paste the resized image in the center
#         offset = ((target_width - new_width) // 2, (target_height - new_height) // 2)
#         new_img.paste(img, offset)

#         # Save the resized and padded image
#         new_img.save(output_path, "JPEG")

# def process_image(image_path, is_public=False, secret=None):
#     """Process an image through poisoning, watermarking, encryption, and blockchain storage"""
#     if not all([SEPOLIA_RPC_URL, PRIVATE_KEY, CONTRACT_ADDRESS, PINATA_API_KEY, PINATA_SECRET_KEY]):
#         raise ValueError("Missing environment variables. Check .env file.")

#     # Use the provided secret, or fall back to the SECRET environment variable
#     if secret is None:
#         secret = SECRET
#         if not secret:
#             raise ValueError("No secret provided and SECRET environment variable is missing.")

#     result = {}

#     # Step 0: Resize the image to 224x224 for poisoning compatibility
#     resized_dir = "data/resized"
#     os.makedirs(resized_dir, exist_ok=True)
#     resized_path = os.path.join(resized_dir, "resized_" + os.path.basename(image_path))
#     resize_and_pad_image(image_path, resized_path, target_size=(224, 224))  # Fixed: Changed input_path to image_path
#     logger.info(f"Image resized to 224x224 and saved to {resized_path}")

#     # Update image_path to point to the resized image
#     image_path = resized_path

#     # Step 1: Poison the image
#     poisoned_dir = "data/poisoned"
#     poisoner = NightshadePoisoner()
#     poisoned_path = os.path.join(poisoned_dir, os.path.basename(image_path))
#     poisoned_img = poisoner.poison_image(image_path)
#     if poisoned_img is None:
#         raise Exception("Failed to poison image")
#     os.makedirs(poisoned_dir, exist_ok=True)
#     cv2.imwrite(poisoned_path, cv2.cvtColor(poisoned_img, cv2.COLOR_RGB2BGR))

#     # Step 2: Verify poisoning
#     verifier = PoisoningVerifier()
#     is_successful, psnr = verifier.verify(image_path, poisoned_path)
#     if not is_successful:
#         raise Exception("Poisoning verification failed")
#     logger.info(f"Poisoning verification successful with PSNR: {psnr:.2f} dB")

#     # Step 3: Watermark the poisoned image with the provided secret
#     watermarked_dir = "data/watermarked"
#     watermarked_path = os.path.join(watermarked_dir, os.path.basename(image_path))
#     watermark_image(poisoned_path, watermarked_path, secret)

#     # Step 4: Verify watermark
#     if not verify_watermark(watermarked_path, secret):
#         raise Exception("Watermark verification failed")
#     logger.info("Watermark verification successful")

#     # Step 5: Handle Phase 2 (Public Tracking) if requested
#     if is_public:
#         public_cid = upload_to_pinata(image_path, PINATA_API_KEY, PINATA_SECRET_KEY)
#         try:
#             add_record_on_chain(SEPOLIA_RPC_URL, PRIVATE_KEY, CONTRACT_ADDRESS, public_cid)
#             result["publicCid"] = public_cid
#         except Exception as e:
#             logger.error(f"Failed to add record on chain for public CID {public_cid}: {str(e)}")
#             result["publicCid"] = public_cid
#             result["publicChainError"] = str(e)
#     else:
#         # Step 6: Encrypt the watermarked image (Phase 3) - Only if is_public is False
#         encrypted_dir = "data/encrypted"
#         encrypted_path = os.path.join(encrypted_dir, "encrypted_" + os.path.basename(image_path) + ".bin")
#         key = encrypt_image(watermarked_path, encrypted_path)
#         encoded_key = base64.b64encode(key).decode('utf-8')

#         # Step 7: Upload encrypted image to Pinata
#         encrypted_cid = upload_to_pinata(encrypted_path, PINATA_API_KEY, PINATA_SECRET_KEY)
#         result["encryptedCid"] = encrypted_cid
#         result["encryptionKey"] = encoded_key

#         # Step 8: Store the encryption key on the blockchain (optional step)
#         try:
#             store_key_on_chain(SEPOLIA_RPC_URL, PRIVATE_KEY, CONTRACT_ADDRESS, encrypted_cid, encoded_key)
#             logger.info(f"Stored encryption key on chain for CID: {encrypted_cid}")
#         except Exception as e:
#             logger.error(f"Failed to store encryption key on chain for CID {encrypted_cid}: {str(e)}")
#             result["chainError"] = str(e)

#         # Step 9: Update .env with the latest CID and key (optional, only if blockchain succeeds)
#         if "chainError" not in result:
#             with open(".env", "a") as f:
#                 f.write(f"IMAGE_CID={encrypted_cid}\n")
#                 f.write(f"ENCRYPTION_KEY={encoded_key}\n")

#     return result

# def revoke_access(cid):
#     """Revoke access to an encrypted image"""
#     if not all([SEPOLIA_RPC_URL, PRIVATE_KEY, CONTRACT_ADDRESS, PINATA_API_KEY, PINATA_SECRET_KEY]):
#         raise ValueError("Missing environment variables. Check .env file.")

#     revoke_access_on_chain(SEPOLIA_RPC_URL, PRIVATE_KEY, CONTRACT_ADDRESS, cid)
#     time.sleep(5)
#     unpin_from_pinata(cid, PINATA_API_KEY, PINATA_SECRET_KEY)
#     is_revoked = verify_revocation(SEPOLIA_RPC_URL, CONTRACT_ADDRESS, cid)

#     local_path = f"data/encrypted/encrypted_{os.path.basename(cid)}.bin"
#     if os.path.exists(local_path):
#         os.remove(local_path)
#         logger.info("Local encrypted file deleted")

#     if not is_revoked:
#         raise Exception("Revocation verification failed")

# if __name__ == "__main__":
#     # For testing locally
#     os.makedirs('data/clean', exist_ok=True)
#     test_img = np.random.randint(0, 255, (512, 512, 3), dtype=np.uint8)
#     test_path = os.path.join('data/clean', 'test.jpg')
#     cv2.imwrite(test_path, test_img)

#     result = process_image(test_path, is_public=True)
#     print("Result:", result)
