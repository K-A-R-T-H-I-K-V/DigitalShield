import torch
import torchvision.models as models
from config import Config

def load_surrogate_model():
    """Load pretrained surrogate model"""
    model = models.resnet50(pretrained=True)
    model.eval()
    model.to(Config.DEVICE)
    return model

def get_feature_extractor(model):
    """Extract feature layers from model"""
    layers = list(model.children())[:-1]  # Remove final classification layer
    return torch.nn.Sequential(*layers).to(Config.DEVICE)