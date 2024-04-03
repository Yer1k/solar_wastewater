## This is where the magic happens

 > Note: Some of the files are stored in Google Drive which is shared with the client. If you, the public, want to view the specific files, you may need to request access to the folder to view the document.

## src folder

### Tool for deleting png images


- [utils_model_training_ResNet50.py](./src/utils_model_training_ResNet50.py)

    This script is a utility script that contains the functions for the ResNet50 model for scene classification.

- [utils_delete_png.py](./src/utils_delete_png.py) 

    This script is used to delete the png images from the dataset folder. The script takes the path to the dataset folder as input and deletes all the png images from the folder. The script is used to delete the png images from the dataset folder before training the model if mass amount of png images are present in the dataset folder.


- [utils_random_sample_folder.py](./src/utils_random_sample_folder.py)

    This script is used to randomly sample a folder and copy the sampled files to a new folder. 


## tools folder

- [count_file_names_csv.ipynb](./tools/count_file_names_csv.ipynb)

    This notebook is used to count the number of files in the folder and save the file names to a csv file.


## Model Training and Validation
Please refer to [Model Training and Validation Notebook](./model_training_ResNet50_scene_classification.ipynb)

In this notebook, we trained a `ResNet50` model to classify the scenes of the images. The model was trained on the ImageNet dataset and fine-tuned on the dataset of images out team collected from Google Earth Egine based on the coordinates of the wastewater treatment plants that we have gathered from three data sources, OpenStreetMap (OSM), Environmental Protection Agency (EPA), and HydroWaste.

The model was trained on 2 classes of scenes, `Wastewater Treatment Plant` as `Yes` and `Not Wastewater Treatment Plant` as `No`. The model was trained using the transfer learning technique, where the pre-trained ResNet50 model was used as the base model and the last layer was replaced with a new layer with 2 output nodes. The model was trained using the SGD optimizer with a learning rate of 0.01 and a batch size of 32. The model was trained for 17 epochs, and the best model was saved based on the validation recall.

The best model is saved as [`best_model_50_v1_crop_320_train_both.pth`](https://drive.google.com/file/d/1bfbLdByUYXedY6bFKMzFT_dlBdxTbiAs/view?usp=drive_link) in the Google Drive folder. 

