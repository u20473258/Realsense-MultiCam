import numpy as np
from PIL import Image
import cv2
import os
import shutil

# Loads images from png file
# folder_path -> folder path to find image
# serial_number -> the serial number of the camera
# frame_number -> which frame or image number to use
# return: the depth image as a numpy array
def load_image_from_npy(serial_number, frame_number):
    depth = np.load(f"depth_images/depth_frame_{frame_number}_cam{serial_number}.npy")

    return depth


if __name__ == "__main__":
    # The frame number from the software synchronisation
    frame_set = [197, 177]
        
    # Store the serial numbers
    # serial_numbers = ["138322250306", "138322252073", "141322252627", "141322252882"]
    serial_numbers = ["138322250306", "141322252882"]
    
    # Create the folder to store point clouds
    if os.path.exists("greyscale_maps"):
        shutil.rmtree("greyscale_maps")
    os.makedirs("greyscale_maps", exist_ok=True)
    
    for i, device in enumerate(serial_numbers):
        serial = np.int64(device)
        
        # Load the depth image from a .npy file
        depth_image = load_image_from_npy(serial, frame_set[i])

        # Normalize the depth image to 0-255 for visualization
        depth_normalized = cv2.normalize(depth_image, None, 0, 255, cv2.NORM_MINMAX)

        # Convert to uint8 (8-bit) format
        depth_normalized = depth_normalized.astype(np.uint8)

        # Display the depth image in greyscale
        cv2.imshow("Depth Image", depth_normalized)
        
        # Save depth greyscale colourmap
        colourmap_filename = f"greyscale_maps/depth_frame_{frame_set[i]}_cam{serial}.png"
        cv2.imwrite(colourmap_filename, depth_normalized)
        
        # Perform distance cropping
        
        
        # Segment target object
