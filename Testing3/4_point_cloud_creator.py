import open3d as o3d
import numpy as np
from PIL import Image
import pandas as pd
import os
import shutil
import sys

# Loads images from png file
# folder_path -> folder path to find image
# serial_number -> the serial number of the camera
# frame_number -> which frame or image number to use
# return: the depth image as a numpy array
def load_image_from_npy(serial_number, frame_number):
    depth = np.load(f"depth_images/depth_frame_{frame_number}_cam{serial_number}.npy")

    return depth

# Loads the camera instrinsics for a specific camera from a .csv file
# serial_number -> the serial number of the camera
# return: fx, fy, ppx, ppy
def load_cam_intrinsics(serial_number):
    # Open the frame_metadata csv
    df = pd.read_csv("camera_intrinsics.csv")
    # Search for the correct row
    row_num = 0
    while True:
        if df.loc[row_num, "serial_number"] == serial_number:
            break
        else:
            row_num += 1
    
    return df.loc[row_num, "fx"], df.loc[row_num, "fy"], df.loc[row_num, "ppx"], df.loc[row_num, "ppy"]

# Creates a point cloud for each camera
# depth_image -> the depth image
# colour_image -> the colour image
# fx -> focal length x
# fy -> focal length y
# ppx -> principal point x
# ppy -> principal point y
# transformation -> how to align given camera view to common reference frame
# depth_scale -> adjust according to the depth unit in your images (e.g., 1000 for mm to meters)
# depth_trunc -> how much should the depth image be truncated
def create_pcd(depth_image, fx, fy, ppx, ppy, depth_scale, depth_trunc):
    
    # Define intrinsic parameters for Open3D
    intrinsic = o3d.camera.PinholeCameraIntrinsic(depth_image.shape[1], depth_image.shape[0], fx, fy, ppx, ppy)
    
    # Create an o3d depth image
    # o3d_depth_image = o3d.geometry.Image(depth_image)
    
    # Create point cloud from depth image
    pcd = o3d.geometry.PointCloud.create_from_depth_image(o3d.geometry.Image(depth_image), 
                                                          intrinsic, depth_scale=depth_scale, 
                                                          depth_trunc=depth_trunc)
    
    return pcd


if __name__ == "__main__":
    # The frame number from the software synchronisation
    frame_set = [197, 177]
        
    # Store the serial numbers
    # serial_numbers = ["138322250306", "138322252073", "141322252627", "141322252882"]
    serial_numbers = ["138322250306", "141322252882"]
        
    # Create the folder to store point clouds
    if os.path.exists("point_clouds"):
        shutil.rmtree("point_clouds")
    os.makedirs("point_clouds", exist_ok=True)
    
    for device in range(0, len(serial_numbers)):
        serial = np.int64(serial_numbers[device])
        # Load images
        depth_image = load_image_from_npy(serial, frame_set[device])
        
        # Load camera instrinsics
        fx, fy, ppx, ppy = load_cam_intrinsics(serial)
        
        # Create the point cloud
        pcd = create_pcd(depth_image, fx, fy, ppx, ppy, 1000.0, 1.5)
        
        # Display point cloud
        o3d.visualization.draw_geometries([pcd])
        # Save point cloud
        filename = f"point_clouds/{serial_numbers[device]}.ply"
        o3d.io.write_point_cloud(filename, pcd)
    