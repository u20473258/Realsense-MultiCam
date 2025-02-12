import os
import shutil
import sys
import pyrealsense2 as rs

# Deletes all the camera data directories
def delete_directories(serials):
    for i in serials:
        if os.path.exists(f"camera_{i}"):
            shutil.rmtree(f"camera_{i}")

# Creates new directories for the camera data       
def create_directories(serials):
    for i in serials:
        os.makedirs(f"camera_{i}", exist_ok=True)
        os.makedirs(f"camera_{i}/colour", exist_ok=True)
        os.makedirs(f"camera_{i}/depth", exist_ok=True)
        os.makedirs(f"camera_{i}/depth_colourised", exist_ok=True)
        os.makedirs(f"camera_{i}/colour_metadata", exist_ok=True)
        os.makedirs(f"camera_{i}/depth_metadata", exist_ok=True)


if __name__ == "__main__":
    serial_numbers = [138322250306, 141322252882]
    
    delete_directories(serial_numbers)
    create_directories(serial_numbers)