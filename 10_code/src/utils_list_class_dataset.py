import os

def list_class(path):
    """
    List the number of files in each class directory.

    Args:
        path (str): The path to the directory containing the class directories (subdirectories.

    Returns:
        None
    """
    

    classes = os.listdir(path)

    # Get the list of classes (subdirectories)
    classes = [class_name for class_name in os.listdir(path)
            if os.path.isdir(os.path.join(path, class_name))]

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

    for class_idx, class_name in enumerate(classes):
        print(f"Class Index: {class_idx}, Class Name: {class_name}")