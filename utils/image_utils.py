import cv2
import numpy as np
import torch
from torchvision import transforms

def load_image(image_path):
    """Load and preprocess image"""
    img = cv2.imread(image_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = cv2.resize(img, Config.INPUT_SIZE)
    return img

def image_to_tensor(img):
    """Convert image to normalized tensor"""
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                            std=[0.229, 0.224, 0.225])
    ])
    return transform(img).unsqueeze(0).to(Config.DEVICE)

def tensor_to_image(tensor):
    """Convert tensor back to image"""
    tensor = tensor.squeeze(0).cpu().detach()
    inv_normalize = transforms.Normalize(
        mean=[-0.485/0.229, -0.456/0.224, -0.406/0.225],
        std=[1/0.229, 1/0.224, 1/0.225]
    )
    tensor = inv_normalize(tensor)
    return tensor.permute(1, 2, 0).numpy() * 255

def save_image(image, path):
    """Save image to disk"""
    image = cv2.cvtColor(image.astype(np.uint8), cv2.COLOR_RGB2BGR)
    cv2.imwrite(path, image)