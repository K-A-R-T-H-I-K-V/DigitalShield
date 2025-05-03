import requests

def upload_to_pinata(input_path, pinata_api_key, pinata_secret_key):
    """Upload a file to Pinata and return the CID"""
    if not all([pinata_api_key, pinata_secret_key]):
        raise ValueError("Missing Pinata credentials")

    with open(input_path, "rb") as f:
        files = [("file", ("encrypted_image.bin", f))]
        headers = {
            "pinata_api_key": pinata_api_key,
            "pinata_secret_api_key": pinata_secret_key
        }
        response = requests.post("https://api.pinata.cloud/pinning/pinFileToIPFS", files=files, headers=headers)

    if response.status_code == 200:
        cid = response.json()["IpfsHash"]
        print(f"Uploaded to IPFS with CID: {cid}")
        return cid
    else:
        raise Exception(f"Upload failed: {response.text}")

# import requests
# from dotenv import load_dotenv
# import os

# # Load environment variables
# load_dotenv()
# PINATA_API_KEY = os.getenv("PINATA_API_KEY")
# PINATA_SECRET_KEY = os.getenv("PINATA_SECRET_KEY")
# input_path = "data/encrypted/encrypted_sample2.bin"
# key_path = ".env"

# if not all([PINATA_API_KEY, PINATA_SECRET_KEY]):
#     raise ValueError("Missing Pinata credentials")

# # Prepare the file for upload
# with open(input_path, "rb") as f:
#     files = [("file", ("encrypted_image.bin", f))]
#     headers = {
#         "pinata_api_key": PINATA_API_KEY,
#         "pinata_secret_api_key": PINATA_SECRET_KEY
#     }
#     response = requests.post("https://api.pinata.cloud/pinning/pinFileToIPFS", files=files, headers=headers)

# if response.status_code == 200:
#     cid = response.json()["IpfsHash"]
#     print(f"Uploaded to IPFS with CID: {cid}")
#     # Update .env with CID
#     with open(key_path, "a") as f:
#         f.write(f"IMAGE_CID={cid}\n")
#     print("CID updated in .env")
# else:
#     print(f"Upload failed: {response.text}")