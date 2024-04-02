import os
import random
import shutil

def copy_random_files(source_dir, dest_dir, remaining_dir, num_files=100, random_seed=42):
    """
    Copy random files from a source directory to a destination directory.

    Input:
    - source_dir: str, path to source directory
    - dest_dir: str, path to destination directory
    - remaining_dir: str, path to remaining directory
    - num_files: int, number of files to copy
    - random_seed: int, random seed for reproducibility

    Output:
    - None
    """
    
    # Set random seed for reproducibility
    random.seed(random_seed)

    # Get list of files in the source directory
    files = os.listdir(source_dir)
    
    # Randomly select 'num_files' files
    random_files = random.sample(files, min(num_files, len(files)))
    
    # Create destination directory if it doesn't exist
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
    
    if not os.path.exists(remaining_dir):
        os.makedirs(remaining_dir)
    
    # Copy selected files to the destination directory
    for file_name in random_files:
        source_file = os.path.join(source_dir, file_name)
        dest_file = os.path.join(dest_dir, file_name)
        shutil.copy2(source_file, dest_file)
    
    # Copy the remaining files to the remaining directory
    for file_name in files:
        if file_name not in random_files:
            source_file = os.path.join(source_dir, file_name)
            dest_file = os.path.join(remaining_dir, file_name)
            shutil.copy2(source_file, dest_file)


