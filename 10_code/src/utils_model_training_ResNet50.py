import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import torchvision
from torchvision import transforms
import torchvision.models as models
from torchvision.datasets import ImageFolder
from torch.utils.data import DataLoader

class SceneClassifier(nn.Module):
    """
    Scene Classifier Model
    
    Args:
    num_classes: int, number of classes in the dataset
    
    Returns:
    model: Scene Classification PyTorch model
    """        
    def __init__(self, num_classes):
        super(SceneClassifier, self).__init__()
        self.features = models.resnet50(weights='ResNet50_Weights.IMAGENET1K_V1')
        # https://pytorch.org/vision/stable/models.html
        num_ftrs = self.features.fc.in_features
        self.features.fc = nn.Linear(num_ftrs, num_classes)

    def forward(self, x):
        x = self.features(x)
        return x