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
    serial_numbers = ["138322250306", "138322252073", "141322252627", "141322252882"]
    
    # Store transformations to align point clouds
    transforms = [
    np.eye(4),  # Camera 1 (identity, reference frame)
    np.array([[0.912,	0.037,  -0.408, 0.053], 
              [-0.005,	0.997,  0.081,  0.000], 
              [0.410,	-0.072, 0.909,  0.012],
              [0.000,	0.000,  0.000,  1.000]]),
    np.array([[1.000,   0.012,  0.004,  0.002 ], 
              [-0.012,  0.989,  0.149,  -0.027], 
              [-0.002,  -0.149, 0.989,  -0.009],
              [0.000,   0.000,  0.000,  1.000 ]]),
    np.array([[0.963,   -0.025, 0.269,  -0.026], 
              [0.025,   1.000,  0.001,  -0.001], 
              [-0.269,  0.006,  0.963,  0.002 ],
              [0.000,   0.000,  0.000,  1.000 ]])
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
    filename = f"point_clouds/reconstruction.ply"
    o3d.io.write_point_cloud(filename, pcd_combined)

