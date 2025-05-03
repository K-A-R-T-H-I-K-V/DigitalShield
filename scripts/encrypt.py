from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad
import os
import base64

def encrypt_image(input_path, output_path):
    """Encrypt an image and return the key"""
    key = get_random_bytes(16)
    print(f"Generated encryption key: {base64.b64encode(key).decode('utf-8')}")

    with open(input_path, "rb") as f:
        img_bytes = f.read()

    print(f"Original image size: {len(img_bytes)} bytes")

    cipher = AES.new(key, AES.MODE_CBC)
    padded_data = pad(img_bytes, AES.block_size)
    ciphertext = cipher.encrypt(padded_data)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(cipher.iv + ciphertext)
    print(f"Encrypted image saved to {output_path}")
    print(f"Encrypted data size: {len(cipher.iv + ciphertext)} bytes")

    return key

# from Crypto.Cipher import AES
# from Crypto.Random import get_random_bytes
# from Crypto.Util.Padding import pad, unpad
# import os
# from dotenv import load_dotenv
# import base64

# # Load environment variables
# load_dotenv()
# input_path = "data/watermarked/sample2.png"
# output_path = "data/encrypted/encrypted_sample2.bin"  # Use .bin to avoid format confusion

# # Generate a random 128-bit key
# key = get_random_bytes(16)  # 128 bits
# print(f"Generated encryption key: {base64.b64encode(key).decode('utf-8')}")

# # Read the watermarked image as raw bytes
# with open(input_path, "rb") as f:
#     img_bytes = f.read()

# print(f"Original image size: {len(img_bytes)} bytes")

# # Encrypt the image
# cipher = AES.new(key, AES.MODE_CBC)
# padded_data = pad(img_bytes, AES.block_size)
# ciphertext = cipher.encrypt(padded_data)

# # Save the encrypted image
# with open(output_path, "wb") as f:
#     f.write(cipher.iv + ciphertext)  # Prepend IV for decryption
# print(f"Encrypted image saved to {output_path}")
# print(f"Encrypted data size: {len(cipher.iv + ciphertext)} bytes")

# # Update .env with the key
# with open(".env", "a") as f:
#     f.write(f"ENCRYPTION_KEY={base64.b64encode(key).decode('utf-8')}\n")
# print("Encryption key added to .env")