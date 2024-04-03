import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import torchvision
from torchvision import transforms
import torchvision.models as models
from torchvision.datasets import ImageFolder
from torch.utils.data import DataLoader
import torchgeo
import torchgeo.models as geomodels

class SceneClassifier(nn.Module):
    """
    Scene Classifier Model
    """        
    def __init__(self, num_classes, pretrained_weights, freeze=False):
        """
        Initializes model
        
        Args:
        num_classes: int, number of classes in the dataset
        pretrained_weights: string, determines pretrained weights to be used
        freeze: bool, determines whether the resnet50 model layers with pretrained weights should be frozen while training
        
        Returns:
        model: Scene Classification ResNet50 model
        """  
        super(SceneClassifier, self).__init__()

        # Uses geospatial foundation resnet50 model weights pretrained on SENTINEL2 satellite images
        if pretrained_weights == "Sentinel2":
            self.features = geomodels.resnet50(weights=torchgeo.models.ResNet50_Weights.SENTINEL2_RGB_MOCO)    
        
        # Uses resnet50 weights pretrained on ImageNet
        else:
            self.features = models.resnet50(weights='ResNet50_Weights.IMAGENET1K_V1')

        # Freezes all layers of resnet50 with pretrained weights
        if freeze:
            for parameter in self.features.parameters():
                parameter.requires_grad = False

        num_ftrs = self.features.fc.in_features

        # Adds trainable final fully connected layer with linear activation
        self.features.fc = nn.Linear(num_ftrs, num_classes)

    def forward(self, x):
        """
        Runs forward pass on model
        
        Args:
        x: input tensor
        
        Returns:
        x: output tensor after forward pass
        """  
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