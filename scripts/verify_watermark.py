from PIL import Image
import numpy as np

def verify_watermark(input_path, expected_secret):
    """Verify the watermark in an image"""
    if not expected_secret:
        raise ValueError("Expected SECRET not provided")

    img = Image.open(input_path).convert("RGB")
    img_array = np.array(img, dtype=np.uint8)

    flat_img = img_array.flatten()
    bits = ''
    for pixel in flat_img:
        bits += str(pixel & 1)
        if len(bits) >= 8:
            byte = bits[-8:]
            if byte == '10101010':
                bits = bits[-8:]
                break

    print("Bits after sync marker:", bits)

    extracted_bits = ''
    for pixel in flat_img[len(bits):]:
        extracted_bits += str(pixel & 1)
        if len(extracted_bits) % 8 == 0:
            byte = extracted_bits[-8:]
            if byte == '00000000':
                extracted_bits = extracted_bits[:-8]
                break

    print("Extracted bits (before decoding):", extracted_bits)

    secret_bytes = bytearray()
    for i in range(0, len(extracted_bits), 8):
        byte = extracted_bits[i:i+8]
        secret_bytes.append(int(byte, 2))
    try:
        extracted_secret = secret_bytes.decode('utf-8')
    except UnicodeDecodeError:
        extracted_secret = "Decoding failed"

    print("Extracted watermark:", extracted_secret)
    print("Expected watermark:", expected_secret)
    if extracted_secret == expected_secret:
        print("Watermark verification successful!")
        return True
    else:
        print("Watermark verification failed!")
        return False

# from PIL import Image
# import numpy as np
# from dotenv import load_dotenv
# import os

# # Load expected secret
# load_dotenv()
# expected_secret = os.getenv("SECRET")
# if not expected_secret:
#     raise ValueError("SECRET not found in .env")

# # Paths
# input_path = "data/watermarked/sample2.png"

# # Load the watermarked image
# img = Image.open(input_path).convert("RGB")
# img_array = np.array(img, dtype=np.uint8)

# # Extract bits using LSB
# flat_img = img_array.flatten()
# bits = ''
# for pixel in flat_img:
#     bits += str(pixel & 1)  # Extract LSB
#     if len(bits) >= 8:
#         byte = bits[-8:]
#         if byte == '10101010':  # Sync marker
#             bits = bits[-8:]
#             break

# # Debug: Print the bits after sync marker
# print("Bits after sync marker:", bits)

# # Continue extracting until null terminator
# extracted_bits = ''
# for pixel in flat_img[len(bits):]:
#     extracted_bits += str(pixel & 1)
#     if len(extracted_bits) % 8 == 0:
#         byte = extracted_bits[-8:]
#         if byte == '00000000':  # Null terminator
#             extracted_bits = extracted_bits[:-8]
#             break

# # Debug: Print the extracted bits
# print("Extracted bits (before decoding):", extracted_bits)

# # Convert bits back to string
# secret_bytes = bytearray()
# for i in range(0, len(extracted_bits), 8):
#     byte = extracted_bits[i:i+8]
#     secret_bytes.append(int(byte, 2))
# try:
#     extracted_secret = secret_bytes.decode('utf-8')
# except UnicodeDecodeError:
#     extracted_secret = "Decoding failed"

# # Verify
# print("Extracted watermark:", extracted_secret)
# print("Expected watermark:", expected_secret)
# if extracted_secret == expected_secret:
#     print("Watermark verification successful!")
# else:
#     print("Watermark verification failed!")

