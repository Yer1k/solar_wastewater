import os
import pandas as pd

def list_file_dataset(source_directory):
    """
    List all files in the train and test dataset

    Input:
    - source_directory: str, path to the directory containing the train and test dataset

    Output:
    - df: pandas DataFrame, containing the list of files
    """

    df = pd.DataFrame(columns=['image', 'label','train or test'])
    for dataset in ['train', 'test']:
        for label in ['Yes', 'No']:
            for file in os.listdir(f'{source_directory}/{dataset}/{label}'):
                df = pd.concat(
                    [df, pd.DataFrame(
                        {'image': [file],
                         'label': [label],
                           'train or test': [dataset]})]
                           )
    return df
