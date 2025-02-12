import os
import shutil
import sys

# Deletes all the camera data directories
def delete_directories(serial):
    if os.path.exists(f"camera_{serial}"):
        shutil.rmtree(f"camera_{serial}")

# Creates new directories for the camera data       
def create_directories(serial):
    os.makedirs(f"camera_{serial}", exist_ok=True)
    os.makedirs(f"camera_{serial}/colour", exist_ok=True)
    os.makedirs(f"camera_{serial}/depth", exist_ok=True)
    os.makedirs(f"camera_{serial}/depth_colourised", exist_ok=True)
    os.makedirs(f"camera_{serial}/colour_metadata", exist_ok=True)
    os.makedirs(f"camera_{serial}/depth_metadata", exist_ok=True)


if __name__ == "__main__":
    serial_numbers = "138322250306"
    
    delete_directories(serial_numbers)
    create_directories(serial_numbers)