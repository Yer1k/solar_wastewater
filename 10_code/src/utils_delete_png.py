import os
import glob

def delete_png(path):
    """
    Delete all png files in a folder

    Input:
    - path: path to folder containing png files

    Output:
    - None
    """
    if not os.path.exists(path):
        raise ValueError('path does not exist')
    if not os.path.isdir(path):
        raise ValueError('path is not a directory')
    for f in glob.glob(path+'/*.png'):
        os.remove(f)
    