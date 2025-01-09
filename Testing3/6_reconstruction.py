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
    serial_numbers = ["138322250306", "141322252882"]
    
    # Store transformations to align point clouds
    transforms = [
    np.eye(4),  # Camera 1 (identity, reference frame)
    np.array([[0.952304544001, 0.055685926827, 0.300025220655, -0.337908239954],
              [-0.046863706186, 0.998233224821, -0.036527002431, 0.026966347488],
              [-0.301529183527, 0.020724536604, 0.953231684883, 0.041012801797],
              [0.000000000000, 0.000000000000, 0.000000000000, 1.000000000000]])
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
    filename = f"point_clouds/manual_registration.ply"
    o3d.io.write_point_cloud(filename, pcd_combined)

