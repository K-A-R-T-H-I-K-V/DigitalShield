import torch
import numpy as np
from config import Config

def calculate_perturbation(grad, alpha):
    """Calculate perturbation with L∞ constraint"""
    perturbation = alpha * torch.sign(grad)
    return torch.clamp(perturbation, -Config.EPSILON, Config.EPSILON)

def feature_collision_loss(clean_features, target_features):
    """Calculate feature space collision loss"""
    return torch.nn.MSELoss()(clean_features, target_features)

def targeted_misclassification_loss(outputs, target_class):
    """Calculate targeted misclassification loss"""
    return torch.nn.CrossEntropyLoss()(outputs, target_class)