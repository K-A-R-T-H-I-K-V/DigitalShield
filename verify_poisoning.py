import torch
from torchvision import transforms, models
import cv2
import numpy as np
from PIL import Image
import requests
import json

class PoisoningVerifier:
    def __init__(self, model_name='resnet50', device='cuda' if torch.cuda.is_available() else 'cpu'):
        self.device = device
        self.model = self._load_model(model_name)
        self.transform = self._get_transform()
        self.imagenet_classes = self._load_imagenet_classes()

    def _load_model(self, model_name):
        """Load a pretrained model"""
        if model_name == 'resnet50':
            model = models.resnet50(weights='IMAGENET1K_V1').eval().to(self.device)
        else:
            raise ValueError(f"Unsupported model: {model_name}")
        return model

    def _get_transform(self):
        """Define image preprocessing (same as poisoning pipeline)"""
        return transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406],
                               std=[0.229, 0.224, 0.225])
        ])

    def _load_imagenet_classes(self):
        """Load ImageNet class names"""
        url = "https://raw.githubusercontent.com/anishathalye/imagenet-simple-labels/master/imagenet-simple-labels.json"
        try:
            response = requests.get(url)
            return json.loads(response.text)
        except Exception as e:
            print(f"Error loading ImageNet classes: {str(e)}")
            return {i: f"class_{i}" for i in range(1000)}  # Fallback

    def preprocess_image(self, image_path):
        """Load and preprocess an image"""
        try:
            img = Image.open(image_path).convert('RGB')
            img_tensor = self.transform(img).unsqueeze(0).to(self.device)
            return img_tensor
        except Exception as e:
            print(f"Error loading {image_path}: {str(e)}")
            return None

    def predict(self, img_tensor):
        """Run inference and return top prediction"""
        with torch.no_grad():
            outputs = self.model(img_tensor)
            probs = torch.softmax(outputs, dim=1)
            top_prob, top_index = probs.max(dim=1)
        return top_prob.cpu().item(), top_index.cpu().item()

    def compute_psnr(self, clean_path, poisoned_path):
        """Compute PSNR between clean and poisoned images"""
        try:
            clean_img = cv2.imread(clean_path)
            poisoned_img = cv2.imread(poisoned_path)
            if clean_img is None or poisoned_img is None:
                return None
            clean_img = cv2.cvtColor(clean_img, cv2.COLOR_BGR2RGB)
            poisoned_img = cv2.cvtColor(poisoned_img, cv2.COLOR_RGB2BGR)
            return cv2.PSNR(clean_img, poisoned_img)
        except Exception as e:
            print(f"Error computing PSNR: {str(e)}")
            return None

    def verify(self, clean_path, poisoned_path):
        """Verify poisoning by comparing model predictions"""
        print(f"\nVerifying: {clean_path} vs {poisoned_path}")
        
        # Process clean image
        clean_tensor = self.preprocess_image(clean_path)
        if clean_tensor is None:
            print("Skipping verification due to clean image error")
            return False, None
        
        clean_prob, clean_index = self.predict(clean_tensor)
        clean_class = self.imagenet_classes[clean_index]
        print(f"Clean image prediction:")
        print(f"Class: {clean_class}, Confidence: {clean_prob:.4f}")

        # Process poisoned image
        poisoned_tensor = self.preprocess_image(poisoned_path)
        if poisoned_tensor is None:
            print("Skipping verification due to poisoned image error")
            return False, None
        
        poisoned_prob, poisoned_index = self.predict(poisoned_tensor)
        poisoned_class = self.imagenet_classes[poisoned_index]
        print(f"Poisoned image prediction:")
        print(f"Class: {poisoned_class}, Confidence: {poisoned_prob:.4f}")

        # Compare predictions
        is_successful = False
        if clean_index != poisoned_index:
            print("Poisoning successful: Different predicted class!")
            print(f"Clean: {clean_class} (Confidence: {clean_prob:.4f})")
            print(f"Poisoned: {poisoned_class} (Confidence: {poisoned_prob:.4f})")
            is_successful = True
        elif clean_prob > poisoned_prob + 0.1:
            print("Poisoning partially successful: Reduced confidence!")
            print(f"Clean: {clean_class} (Confidence: {clean_prob:.4f})")
            print(f"Poisoned: {poisoned_class} (Confidence: {poisoned_prob:.4f})")
            is_successful = True
        else:
            print("Poisoning may be ineffective: Similar predictions.")
            print(f"Clean: {clean_class} (Confidence: {clean_prob:.4f})")
            print(f"Poisoned: {poisoned_class} (Confidence: {poisoned_prob:.4f})")
        
        # Compute PSNR
        psnr = self.compute_psnr(clean_path, poisoned_path)
        if psnr is not None:
            print(f"PSNR: {psnr:.2f} dB")
            if psnr >= 30:
                print("Visual imperceptibility confirmed (PSNR ≥ 30 dB).")
            else:
                print("Warning: Poisoned image may be visually distinguishable (PSNR < 30 dB).")
        
        return is_successful, psnr