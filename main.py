import os
import cv2
import numpy as np
from tqdm import tqdm
from poison_generator import NightshadePoisoner
from verify_poisoning import PoisoningVerifier

def verify_results(clean_dir, poisoned_dir):
    """Verify output files and quality"""
    clean_files = set(os.listdir(clean_dir))
    poisoned_files = set(os.listdir(poisoned_dir))
    
    print("\n=== Verification ===")
    print(f"Clean images: {len(clean_files)}")
    print(f"Poisoned images: {len(poisoned_files)}")
    
    if not poisoned_files:
        print("\nNo poisoned images were created. Possible reasons:")
        print("- All attempts failed PSNR check")
        print("- Input images were invalid")
        print("- Permission issues in output directory")
        
        # Create a test file to check permissions
        test_path = os.path.join(poisoned_dir, 'test.txt')
        try:
            with open(test_path, 'w') as f:
                f.write("test")
            os.remove(test_path)
            print("- Output directory permissions OK")
        except Exception as e:
            print(f"- Output directory error: {str(e)}")
        return 0, 0
    
    # Verify poisoning effect
    verifier = PoisoningVerifier(model_name='resnet50')
    successful_poisonings = 0
    total_psnr = 0
    verified_pairs = 0
    
    print("\nVerifying poisoning effect...")
    for clean_file in clean_files:
        if clean_file.lower().endswith(('.png', '.jpg', '.jpeg')):
            clean_path = os.path.join(clean_dir, clean_file)
            poisoned_path = os.path.join(poisoned_dir, clean_file)
            if os.path.exists(poisoned_path):
                is_successful, psnr = verifier.verify(clean_path, poisoned_path)
                if is_successful:
                    successful_poisonings += 1
                if psnr is not None:
                    total_psnr += psnr
                    verified_pairs += 1
    
    avg_psnr = total_psnr / verified_pairs if verified_pairs > 0 else 0
    print(f"\nPoisoning Verification Summary:")
    print(f"Verified pairs: {verified_pairs}")
    print(f"Successful poisonings: {successful_poisonings}")
    print(f"Average PSNR: {avg_psnr:.2f} dB")
    
    return successful_poisonings, avg_psnr

def main():
    print("=== Nightshade Image Poisoning ===")
    
    # Initialize
    poisoner = NightshadePoisoner()
    print("\nPoisoner initialized with:")
    print(f"- Device: {poisoner.device}")
    print(f"- Models: {[name for name in poisoner.models.keys()]}")
    print(f"- Parameters: {poisoner.attack_params}")
    
    # Setup directories
    os.makedirs('data/clean', exist_ok=True)
    os.makedirs('data/poisoned', exist_ok=True)
    
    # Get images
    print("\nScanning for images...")
    image_paths = []
    for f in os.listdir('data/clean'):
        if f.lower().endswith(('.png', '.jpg', '.jpeg')):
            image_paths.append(os.path.join('data/clean', f))
    
    if not image_paths:
        print("No images found - creating test image...")
        test_img = np.random.randint(0, 255, (512, 512, 3), dtype=np.uint8)
        test_path = os.path.join('data/clean', 'test.jpg')
        cv2.imwrite(test_path, test_img)
        image_paths = [test_path]
    
    print(f"Found {len(image_paths)} images to process")
    
    # Process images
    print("\nGenerating poisoned images...")
    success_count = poisoner.poison_dataset(
        image_paths,
        output_dir='data/poisoned'
    )
    
    # Verify results
    successful_poisonings, avg_psnr = verify_results('data/clean', 'data/poisoned')
    
    print("\n=== Summary ===")
    print(f"Attempted: {len(image_paths)}")
    print(f"Successful poisonings generated: {success_count}")
    print(f"Successful poisonings verified: {successful_poisonings}")
    print(f"Average PSNR: {avg_psnr:.2f} dB")
    print(f"Output directory: data/poisoned")

if __name__ == "__main__":
    main()