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
    model: Scene Classification ResNet50 model
    """        
    def __init__(self, num_classes, pretrained_weights, freeze="No"):
        super(SceneClassifier, self).__init__()
        self.features = models.resnet50(weights=pretrained_weights)
        # https://pytorch.org/vision/stable/models.html
        num_ftrs = self.features.fc.in_features
        self.features.fc = nn.Linear(num_ftrs, num_classes)

    def forward(self, x):
        x = self.features(x)
        return x

def define_transforms(crop_size):
    """
    Returns transform object with given center crop size for preprocessing and augmenting images for model input
    
    Args:
    crop_size: int, crop size for center crop of input image to model
    
    Returns:
    model: transform object
    """ 
    # Define transforms for preprocessing and augmenting the images
    transform = transforms.Compose([
        transforms.CenterCrop(crop_size), # Crop the center of the image
        transforms.Resize((224, 224)), # Resize the image to 224x224 so the model can process it
        transforms.ToTensor(), # Convert the image to a tensor
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]), # Normalize the image based on the ImageNet statistics
        transforms.RandomHorizontalFlip(),  # Randomly flip the image horizontally
        transforms.RandomRotation(10),  # Randomly rotate the image
        transforms.RandomVerticalFlip(),  # Randomly flip the image vertically
    ])

    return transform

def get_class_counts(path):

    # path = "./data/train/CA"
    # path = "./data/test/CA"

    # Get the list of classes (subdirectories)
    classes = os.listdir(path)

    # Get the list of classes (subdirectories)
    classes = [class_name for class_name in os.listdir(path)
            if os.path.isdir(os.path.join(path, class_name))]

    # Check label-folder association
    for class_idx, class_name in enumerate(classes):
        print(f"Class Index: {class_idx}, Class Name: {class_name}")

    # Create a dictionary to store the counts
    class_counts = {}

    # Iterate over each class directory and count the number of files
    for class_name in classes:
        class_path = os.path.join(path, class_name)
        file_count = len(os.listdir(class_path))
        class_counts[class_name] = file_count

    # Print the class counts
    for class_name, count in class_counts.items():
        print(f"Class: {class_name}, Number of Files: {count}")