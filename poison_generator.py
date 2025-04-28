import torch
import torch.nn as nn
import numpy as np
from tqdm import tqdm
from torchvision import transforms, models
import cv2
import os
import random
import io
from PIL import Image

class NightshadePoisoner:
    def __init__(self, device='cuda' if torch.cuda.is_available() else 'cpu'):
        self.device = device
        if self.device == 'cpu':
            print("WARNING: Using CPU, which is slower. Consider enabling GPU for <0.8s processing.")
        self.models = self._load_models()
        self.transform = self._get_transform()
        self.augmentation = self._get_augmentation()
        self.attack_params = {
            'epsilon': 16/255,      # Balanced perturbation
            'alpha': 4.0/255,       # Aggressive step size
            'iterations': 20,        # Minimal iterations
            'num_classes': 1000,
            'min_psnr': 28,         # Strict visual quality
            'feature_weight': 0.0,  # No feature-space loss
            'pixel_reg': 0.1,       # Minimal regularization
            'max_retries': 3,       # Retry with scaled-down perturbations
            'augment_prob': 0.15,   # Ultra-light augmentations
            'target_weight': 12.0   # Strong target loss
        }
        self.verifier = self._load_verifier()

    def _load_models(self):
        """Load single pretrained model"""
        resnet = models.resnet50(weights='IMAGENET1K_V1').eval().to(self.device)
        return {'resnet': resnet}

    def _load_verifier(self):
        """Load ResNet50 for verification"""
        model = models.resnet50(weights='IMAGENET1K_V1').eval().to(self.device)
        return model

    def _get_transform(self):
        """Basic image transform"""
        return transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406],
                               std=[0.229, 0.224, 0.225])
        ])

    def _get_augmentation(self):
        """Define ultra-light augmentations"""
        return transforms.Compose([
            transforms.RandomHorizontalFlip(),
            transforms.RandomRotation(1),
            transforms.Lambda(lambda img: self._jpeg_compression(img))
        ])

    def _jpeg_compression(self, img):
        """Simulate JPEG compression"""
        img_pil = transforms.ToPILImage()(img)
        buffer = io.BytesIO()
        img_pil.save(buffer, format="JPEG", quality=85)
        img_compressed = Image.open(buffer).convert('RGB')
        return transforms.ToTensor()(img_compressed)

    def _predict_class(self, img_tensor):
        """Predict top class and confidence"""
        with torch.no_grad():
            outputs = self.verifier(img_tensor)
            probs = torch.softmax(outputs, dim=1)
            top_prob, top_index = probs.max(dim=1)
        return top_index.item(), top_prob.item()

    def _get_target_class(self, clean_class):
        """Select a random target class different from the clean class"""
        return random.choice([i for i in range(self.attack_params['num_classes']) if i != clean_class])

    def _generate_perturbation(self, img_tensor, scale=1.0):
        """Generate targeted perturbation using PGD"""
        original = img_tensor.clone()
        perturbation = torch.zeros_like(img_tensor, requires_grad=True)
        clean_class, clean_prob = self._predict_class(original)
        target_class = self._get_target_class(clean_class)
        target_class_tensor = torch.tensor([target_class]).to(self.device)
        print(f"Clean prediction: Class {clean_class}, Confidence {clean_prob:.4f}, Targeting: Class {target_class}")

        for i in range(self.attack_params['iterations']):
            perturbed = original + perturbation

            # Apply augmentation
            if random.random() < self.attack_params['augment_prob']:
                perturbed_aug = self.augmentation(perturbed.squeeze(0)).unsqueeze(0).to(self.device)
            else:
                perturbed_aug = perturbed

            # PGD: Targeted cross-entropy + original class penalty + confidence boost
            total_loss = 0
            for model_name, model in self.models.items():
                outputs = model(perturbed_aug)
                target_loss = -self.attack_params['target_weight'] * torch.nn.functional.cross_entropy(outputs, target_class_tensor)
                original_loss = torch.nn.functional.cross_entropy(outputs, torch.tensor([clean_class]).to(self.device))
                target_prob = torch.softmax(outputs, dim=1)[0, target_class]
                confidence_loss = -torch.log(target_prob + 1e-6)
                total_loss += target_loss + 0.8 * original_loss + 0.6 * confidence_loss

            # Pixel regularization
            pixel_loss = torch.norm(perturbation, p=2)
            total_loss += self.attack_params['pixel_reg'] * pixel_loss

            # Backpropagate
            perturbation.grad = None
            total_loss.backward()
            perturbation.data = perturbation.data + self.attack_params['alpha'] * scale * perturbation.grad.sign()
            perturbation.data = torch.clamp(perturbation.data,
                                         -self.attack_params['epsilon'] * scale,
                                         self.attack_params['epsilon'] * scale)
            perturbation.grad.zero_()

            # In-loop verification
            poisoned_class, poisoned_prob = self._predict_class(perturbed)
            print(f"Iteration {i}: Perturbation norm = {torch.norm(perturbation).item():.4f}, "
                  f"Loss = {total_loss.item():.4f}, "
                  f"Poisoned prediction: Class {poisoned_class}, Confidence {poisoned_prob:.4f}")

            # Early stopping if target class achieved
            if poisoned_class == target_class and poisoned_prob > 0.7:
                print(f"Target class {target_class} achieved at iteration {i}")
                break

            # Save debug image only if target not reached
            if i == self.attack_params['iterations'] - 1 and poisoned_class != target_class:
                intermediate_img = self._tensor_to_image(perturbed.detach())
                cv2.imwrite(f"debug_intermediate_final.png", cv2.cvtColor(intermediate_img, cv2.COLOR_RGB2BGR))

        return perturbation.detach()

    def poison_image(self, image_path):
        """Create poisoned image with retries"""
        try:
            img = cv2.imread(image_path)
            if img is None:
                raise ValueError("Could not read image")
            if img.shape[0] < 50 or img.shape[1] < 50:
                raise ValueError(f"Image too small: {img.shape}")
            if len(img.shape) != 3 or img.shape[2] != 3:
                raise ValueError(f"Invalid image format: {img.shape}")

            original = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            h, w = original.shape[:2]
            print(f"Input image shape: {original.shape}, range: {original.min()}-{original.max()}")

            img_resized = cv2.resize(original, (224, 224), interpolation=cv2.INTER_CUBIC)
            img_tensor = self.transform(img_resized).unsqueeze(0).to(self.device)
            print(f"Tensor range after transform: {img_tensor.min().item():.4f}-{img_tensor.max().item():.4f}")

            for attempt in range(self.attack_params['max_retries']):
                scale = 1.0 / (2.0 ** attempt)
                print(f"Attempt {attempt + 1} with scale {scale:.2f}")

                perturbation = self._generate_perturbation(img_tensor, scale=scale)
                poisoned_tensor = img_tensor + perturbation
                print(f"Poisoned tensor range: {poisoned_tensor.min().item():.4f}-{poisoned_tensor.max().item():.4f}")

                poisoned_small = self._tensor_to_image(poisoned_tensor)
                original_small = cv2.resize(original, (224, 224), interpolation=cv2.INTER_CUBIC)
                psnr_small = cv2.PSNR(original_small, poisoned_small)
                print(f"PSNR (224x224): {psnr_small:.2f} dB")

                poisoned = cv2.resize(poisoned_small, (w, h), interpolation=cv2.INTER_CUBIC)
                pixel_diff = np.abs(original.astype(float) - poisoned.astype(float))
                pixel_diff_mean = pixel_diff.mean()
                pixel_diff_channels = pixel_diff.mean(axis=(0, 1))
                print(f"Pixel difference (mean): {pixel_diff_mean:.4f}")
                print(f"Pixel difference (R,G,B): {pixel_diff_channels}")

                psnr = cv2.PSNR(original, poisoned)
                print(f"PSNR (original size): {psnr:.2f} dB")
                if psnr >= self.attack_params['min_psnr']:
                    return poisoned

                debug_path = f"debug_poisoned_attempt_{attempt + 1}.png"
                cv2.imwrite(debug_path, cv2.cvtColor(poisoned, cv2.COLOR_RGB2BGR))
                print(f"PSNR too low ({psnr:.2f} dB), saved debug image at {debug_path}, retrying with reduced scale...")

            raise ValueError(f"Could not achieve required PSNR after {self.attack_params['max_retries']} attempts")

        except Exception as e:
            print(f"Error processing {image_path}: {str(e)}")
            return None

    def _tensor_to_image(self, tensor):
        """Convert tensor to numpy image"""
        tensor = tensor.squeeze(0).cpu()
        inv_normalize = transforms.Normalize(
            mean=[-0.485/0.229, -0.456/0.224, -0.406/0.225],
            std=[1/0.229, 1/0.224, 1/0.225]
        )
        img = inv_normalize(tensor).permute(1, 2, 0).numpy()
        print(f"Tensor range before scaling: {img.min():.4f}-{img.max():.4f}")
        img = (img * 255).clip(0, 255).astype(np.uint8)
        print(f"Output image range: {img.min()}-{img.max()}")
        return img

    def poison_dataset(self, image_paths, output_dir='poisoned'):
        """Process multiple images"""
        os.makedirs(output_dir, exist_ok=True)
        success_count = 0

        for img_path in tqdm(image_paths, desc="Poisoning"):
            try:
                poisoned_img = self.poison_image(img_path)
                if poisoned_img is not None:
                    out_path = os.path.join(output_dir, os.path.basename(img_path))
                    cv2.imwrite(out_path, cv2.cvtColor(poisoned_img, cv2.COLOR_RGB2BGR))
                    success_count += 1
            except Exception as e:
                print(f"\nFailed on {img_path}: {str(e)}")
                continue

        return success_count