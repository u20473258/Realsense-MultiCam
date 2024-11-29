import open3d as o3d
import numpy as np
from PIL import Image
import pandas as pd
import pyrealsense2 as rs
import cv2
import os
import shutil

# Loads images from png file
# serial_number -> the serial number of the camera
# frame_number -> which frame or image number to use
# return: the depth and colour images as numpy arrays
def load_images_from_png(serial_number, frame_number):
    depth = np.array(Image.open(f"depth_images/depth_frame_{frame_number}_cam{serial_number}.png"))

    return depth


if __name__ == "__main__":
    # The frame number from the software synchronisation
    frame_set = [223, 203, 199, 225]
        
    # Store the serial numbers
    serial_numbers = ["138322250306", "138322252073", "141322252627", "141322252882"]
    
    # Create the folder to store point clouds
    if os.path.exists("point_clouds"):
        shutil.rmtree("point_clouds")
    os.makedirs("point_clouds", exist_ok=True)
    
    for device in range(0, len(serial_numbers)):
        serial = np.int64(serial_numbers[device])
        # Load images
        colour_image, depth_image = load_images_from_png(serial, frame_set[device])
        
        # Perform distance cropping
        
        
        # Segment target object
