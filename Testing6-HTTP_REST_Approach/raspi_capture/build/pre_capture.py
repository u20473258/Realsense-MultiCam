import os
import shutil
import sys

# Deletes all the camera data directories
def delete_directories(pi):
    if os.path.exists(f"camera_{pi}"):
        shutil.rmtree(f"camera_{pi}")

# Creates new directories for the camera data       
def create_directories(pi):
    os.makedirs(f"{pi}", exist_ok=True)
    os.makedirs(f"{pi}/colour", exist_ok=True)
    os.makedirs(f"{pi}/depth", exist_ok=True)
    os.makedirs(f"{pi}/depth_colourised", exist_ok=True)
    os.makedirs(f"{pi}/colour_metadata", exist_ok=True)
    os.makedirs(f"{pi}/depth_metadata", exist_ok=True)


if __name__ == "__main__":
    pi_name = "raspi1"
    
    delete_directories(pi_name)
    create_directories(pi_name)