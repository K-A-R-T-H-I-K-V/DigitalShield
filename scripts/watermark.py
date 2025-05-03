from PIL import Image
import numpy as np
import os
import io

def watermark_image(input_path, output_path, secret):
    """Watermark an image with a secret"""
    if not secret:
        raise ValueError("SECRET not provided")

    img = Image.open(input_path)
    width, height = img.size
    capacity_bits = width * height * 3
    capacity_bytes = capacity_bits // 8
    print(f"Image capacity (approximate): {capacity_bytes} bytes")
    print(f"Secret length: {len(secret)} bytes")

    if len(secret) > capacity_bytes:
        raise ValueError("Secret too large for image!")

    img = img.convert("RGB")
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format="PNG")
    img_byte_arr.seek(0)

    img = Image.open(img_byte_arr)
    img_array = np.array(img, dtype=np.uint8)

    sync_marker = "10101010"
    secret_bytes = secret.encode('utf-8')
    secret_bits = ''.join(format(byte, '08b') for byte in secret_bytes)
    total_bits = sync_marker + secret_bits + '00000000'

    flat_img = img_array.flatten()
    bit_idx = 0
    for bit in total_bits:
        if bit_idx >= len(flat_img):
            raise ValueError("Image too small to hold secret!")
        flat_img[bit_idx] = (flat_img[bit_idx] & 0xFE) | int(bit)
        bit_idx += 1

    watermarked_array = flat_img.reshape(img_array.shape)
    watermarked_img = Image.fromarray(watermarked_array)
    watermarked_img.save(output_path, format="PNG")
    print("Watermark embedded successfully!")
    return output_path   


# from PIL import Image
# import numpy as np
# from dotenv import load_dotenv
# import os
# import io

# # Load secret from .env
# load_dotenv()
# secret = os.getenv("SECRET")
# if not secret:
#     raise ValueError("SECRET not found in .env")

# # Paths
# input_path = "data/poisoned/sample2.png"
# output_path = "data/watermarked/sample2.png"

# # Calculate capacity (approximate)
# img = Image.open(input_path)
# width, height = img.size
# capacity_bits = width * height * 3  # RGB channels
# capacity_bytes = capacity_bits // 8
# print(f"Image capacity (approximate): {capacity_bytes} bytes")
# print(f"Secret length: {len(secret)} bytes")

# if len(secret) > capacity_bytes:
#     raise ValueError("Secret too large for image!")

# # Convert JPEG to PNG in memory
# img = img.convert("RGB")  # Ensure RGB format
# img_byte_arr = io.BytesIO()
# img.save(img_byte_arr, format="PNG")
# img_byte_arr.seek(0)

# # Load the in-memory PNG as a numpy array
# img = Image.open(img_byte_arr)
# img_array = np.array(img, dtype=np.uint8)

# # Convert secret to binary with sync marker
# sync_marker = "10101010"  # 8-bit sync pattern
# secret_bytes = secret.encode('utf-8')
# secret_bits = ''.join(format(byte, '08b') for byte in secret_bytes)
# total_bits = sync_marker + secret_bits + '00000000'  # Sync + secret + null terminator

# # Embed secret using LSB
# flat_img = img_array.flatten()
# bit_idx = 0
# for bit in total_bits:
#     if bit_idx >= len(flat_img):
#         raise ValueError("Image too small to hold secret!")
#     flat_img[bit_idx] = (flat_img[bit_idx] & 0xFE) | int(bit)
#     bit_idx += 1

# # Reshape and save the watermarked image
# watermarked_array = flat_img.reshape(img_array.shape)
# watermarked_img = Image.fromarray(watermarked_array)
# watermarked_img.save(output_path, format="PNG")
# print("Watermark embedded successfully!")

