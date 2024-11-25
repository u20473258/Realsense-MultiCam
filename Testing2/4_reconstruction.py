import open3d as o3d
import numpy as np
from PIL import Image
import pandas as pd
import pyrealsense2 as rs
import cv2

# Loads images from png file
# folder_path -> folder path to find image
# serial_number -> the serial number of the camera
# return: point cloud
def load_point_cloud(serial_number):
    # Load the .ply file
    file_path = f"point_clouds/{serial_number}.ply"
    point_cloud = o3d.io.read_point_cloud(file_path)

    # Check if the point cloud is loaded
    if not point_cloud.is_empty():
        return point_cloud
    else:
        print("Failed to load point cloud. Check the file path or format.")
        return None


if __name__ == "__main__":
    # Store the serial numbers
    serial_numbers = ["138322252073", "141322252882"]
    
    # Store transformations to align point clouds
    transforms = [
    np.eye(4),  # Camera 1 (identity, reference frame)
    np.array([[0.889,	-0.012,	-0.457,	-189.380], [0.001,	1.000,	-0.024,	-1.555], [0.457,	0.021,	0.889,	-180.769],[0.000,	0.000,	0.000,	1.000]])
    ]
    
    # Define the combined point cloud
    pcd_combined = o3d.geometry.PointCloud()
    
    # Transform point clouds
    point_clouds = []
    i = 0
    for device in serial_numbers:
        # Load point cloud
        pcd = load_point_cloud(device)
        
        # Transform point cloud
        pcd.transform(transforms[i])
        i += 1
        
        # Store transformed point cloud
        point_clouds.append(pcd)
        pcd_combined += pcd
    
    # Visualize aligned point clouds
    o3d.visualization.draw_geometries(point_clouds)
    
    # Save the combined point cloud
    filename = f"point_clouds/{device}.ply"
    o3d.io.write_point_cloud("reconstruction.ply", pcd_combined)

