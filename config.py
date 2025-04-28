import torch

class Config:
    # Poisoning parameters
    POISON_RATIO = 0.1  # Percentage of images to poison
    EPSILON = 20/255     # Maximum perturbation (L∞ norm)
    ALPHA = 4/255       # Attack step size
    ITERATIONS = 20     # Number of attack iterations
    
    # Model parameters
    TARGET_CLASSES = 1000
    INPUT_SIZE = (224, 224)
    
    # Device configuration
    DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    # Paths
    CLEAN_DATA_DIR = 'data/clean'
    POISONED_DATA_DIR = 'data/poisoned'
    MODEL_WEIGHTS = 'weights/surrogate_model.pth'