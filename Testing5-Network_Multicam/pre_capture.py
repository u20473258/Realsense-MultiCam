import os
import shutil
import sys

# Deletes all the camera data directories
def delete_directories(num_camera):
    for i in range(num_camera):
        if os.path.exists(f"camera_{i}"):
            shutil.rmtree(f"camera_{i}")

# Creates new directories for the camera data       
def create_directories(num_camera):
    for i in range(num_camera):
        os.makedirs(f"camera_{i}", exist_ok=True)
        os.makedirs(f"camera_{i}/colour", exist_ok=True)
        os.makedirs(f"camera_{i}/depth", exist_ok=True)
        os.makedirs(f"camera_{i}/colour_metadata", exist_ok=True)
        os.makedirs(f"camera_{i}/depth_metadata", exist_ok=True)


if __name__ == "__main__":
    num_cameras = sys.argv[1]
    
    delete_directories(num_cameras)
    create_directories(num_cameras)