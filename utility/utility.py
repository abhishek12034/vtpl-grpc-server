import os


def count_images_in_folder(folder_path):
    image_extensions = (".jpg", ".jpeg", ".png", ".bmp", ".gif")

    image_count = 0

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(image_extensions):
                image_count += 1

    return image_count


import os
import re


def extract_number(filename):
    match = re.search(r"\d+", filename)
    return int(match.group()) if match else -1


def list_image_files(directory):
    image_extensions = [".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff"]
    files = [
        entry.name
        for entry in os.scandir(directory)
        if entry.is_file()
        and os.path.splitext(entry.name)[1].lower() in image_extensions
    ]

    return sorted(files, key=extract_number, reverse=False)


import os
import shutil


def clear_output_folder(folder_path):
    # Check if the folder exists
    if os.path.exists(folder_path):
        # Remove all files and subdirectories
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            try:
                # Check if it's a file or directory and remove it
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)  # Remove file or link
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)  # Remove directory
            except Exception as e:
                print(f"Failed to delete {file_path}. Reason: {e}")
    else:
        print(f"The folder {folder_path} does not exist.")
