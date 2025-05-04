from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import base64
import os

def decrypt_image(input_path, output_path, encryption_key):
    """Decrypt an image using the provided key"""
    key = base64.b64decode(encryption_key)

    with open(input_path, "rb") as f:
        iv = f.read(16)
        ciphertext = f.read()

    print(f"Encrypted data size: {len(iv + ciphertext)} bytes")

    cipher = AES.new(key, AES.MODE_CBC, iv=iv)
    padded_data = cipher.decrypt(ciphertext)
    img_bytes = unpad(padded_data, AES.block_size)

    print(f"Decrypted image size: {len(img_bytes)} bytes")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(img_bytes)

    print(f"Decrypted image saved to {output_path}")

# from Crypto.Cipher import AES
# from Crypto.Util.Padding import unpad
# import os
# from dotenv import load_dotenv
# import base64

# # Load environment variables
# load_dotenv()
# input_path = "data/encrypted/encrypted_sample2.bin"
# output_path = "data/decrypted/decrypted_sample2.png"
# encryption_key = os.getenv("ENCRYPTION_KEY")
# if not encryption_key:
#     raise ValueError("ENCRYPTION_KEY not found in .env")

# # Decode the base64 key
# key = base64.b64decode(encryption_key)

# # Read the encrypted image
# with open(input_path, "rb") as f:
#     iv = f.read(16)  # First 16 bytes are IV
#     ciphertext = f.read()

# print(f"Encrypted data size: {len(iv + ciphertext)} bytes")

# # Decrypt the image
# cipher = AES.new(key, AES.MODE_CBC, iv=iv)
# padded_data = cipher.decrypt(ciphertext)
# img_bytes = unpad(padded_data, AES.block_size)

# print(f"Decrypted image size: {len(img_bytes)} bytes")

# # Save the decrypted image
# with open(output_path, "wb") as f:
#     f.write(img_bytes)

# print(f"Decrypted image saved to {output_path}")