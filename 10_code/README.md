## Experiments

 
 > Note: Some of the files are stored in Google Drive which is shared with the client. If you, the public, want to view the specific files, you may need to request access to the folder to view the document.

### Stage 1: Parameter Tuning

The parameters we tuned for are as follows:

Crop size of image: We center crop the input images to remove surrounding geographical structures that may not be a part of the WWTP. The crop sizes used are: 224x224, 320x320, 512x512, 2228x2228 (original).   

The results of the experiments are as follows:

| Weights      | Crop Size          | F1 Score | AUC       |
|--------------|--------------------|----------|-----------|
| ImageNet     | Original           | 0.5198   | 0.87      |
| ImageNet     | 512x512            | 0.5075   | 0.92      |
| ImageNet     | 320x320            | 0.6554   | 0.93      |
| ImageNet     | 224x224            | 0.5198   | 0.87      |

From the above table we see that the model trained on ImageNet weights, with crop size of 320 performed the best with an AUC of 0.93. We choose this model for the next stage.

### Stage 2: Within Domain vs Cross Domain Performance

| Training on / Validation on       | Texas                      | California                   |
|-----------------------------------|----------------------------|------------------------------|
| Texas                             | AUC:0.93, Max F1: 0.8454   | AUC:0.89, Max F1: 0.5482     |
| California                        | AUC:0.75, Max F1: 0.6175   | AUC:0.91, Max F1: 0.6139     |

While there is a performance drop when running cross domain, the max F1 scores and AUC scores are still high, demonstrating the model's generalizability.

## src folder

### Tools for Model Training

- [utils_model_training_ResNet50.py](./src/utils_model_training_ResNet50.py)

    This script is a utility script that contains the functions for the ResNet50 model for scene classification.

- [utils_random_sample_folder.py](./src/utils_random_sample_folder.py)

    This script is used to randomly sample a folder and copy the sampled files to a new folder. 

- [utils_list_class_dataset.py](./src/utils_list_class_dataset.py)

    This script is used to list the number of files in each class directory and the class index.

- [utils_list_file_dataset.py](./src/utils_list_file_dataset.py)

    This script is used to list the number of files in the training and testing dataset folders.

### Tool for deleting png images

- [utils_delete_png.py](./src/utils_delete_png.py) 

    This script is used to delete the png images from the dataset folder. The script takes the path to the dataset folder as input and deletes all the png images from the folder. The script is used to delete the png images from the dataset folder before training the model if mass amount of png images are present in the dataset folder.


## tools folder

- [count_file_names_csv.ipynb](./tools/count_file_names_csv.ipynb)

    This notebook is used to count the number of files in the folder and save the file names to a csv file.

- [tagging_tool.py](./tools/tagging_tool.py)

    This Streamlit-based application, `tagging_tool.py`, allows users to efficiently tag images for the presence of WWTP and Solar Panels within datasets organized by state. It's designed for simplicity and ease of use.

    #### How to Use
    1. Start the Application: Launch the tool in your browser by running the command below.
    ```streamlit run tagging_tool.py```
    2. Enter State Name: Type the state's name for which you intend to tag images.
    3. Select Image: Choose the initial image from the dropdown menu.
    4. Confirm Selection: Click "Confirm and Proceed!" to load the image.
    5. Tagging: Determine the presence of WWTP or Solar Panels for each image and select the corresponding button.
    6. Navigation: Move through images using "Previous" and "Next". You'll be notified upon reaching the last image.
    7. Reset: To restart or switch states, use the "Reset" button.

    #### Data Structure
    To use this tool, your dataset should be organized as follows:

    - ```data/<state_name>```: Contains the images.
    - ```data/predictions_best_<state_name>.csv```: Spreadsheet listing filenames and initial predictions.
    - The ```tagging_tool.py``` script should be located in the same folder as the data directory.

    Replace <state_name> with the actual state name.



## Model Training and Validation
Please refer to [Model Training and Validation Notebook](./model_training_ResNet50_scene_classification.ipynb)

In this notebook, we trained a `ResNet50` model to classify the scenes of the images. The model was trained on the ImageNet dataset and fine-tuned on the dataset of images out team collected from Google Earth Egine based on the coordinates of the wastewater treatment plants that we have gathered from three data sources, OpenStreetMap (OSM), Environmental Protection Agency (EPA), and HydroWaste.

The model was trained on 2 classes of scenes, `Wastewater Treatment Plant` as `Yes` and `Not Wastewater Treatment Plant` as `No`. The model was trained using the transfer learning technique, where the pre-trained ResNet50 model was used as the base model and the last layer was replaced with a new layer with 2 output nodes. The model was trained using the SGD optimizer with a learning rate of 0.01 and a batch size of 32. The model was trained for 17 epochs, and the best model was saved based on the validation recall.

The best model is saved as [`best_model_50_v1_crop_320_train_both.pth`](https://drive.google.com/file/d/1bfbLdByUYXedY6bFKMzFT_dlBdxTbiAs/view?usp=drive_link) in the Google Drive folder. 

