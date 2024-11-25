import open3d as o3d
import numpy as np
from PIL import Image
import pandas as pd
import pyrealsense2 as rs
import cv2

# Loads images from png file
# folder_path -> folder path to find image
# serial_number -> the serial number of the camera
# frame_number -> which frame or image number to use
# return: the depth and colour images as numpy arrays
def load_images_from_png(serial_number, frame_number):
    colour = np.array(Image.open(f"rgb_images/rgb_frame_{frame_number}_cam{serial_number}.png"))
    depth = np.array(Image.open(f"depth_images/depth_frame_{frame_number}_cam{serial_number}.png"))

    return colour, depth

# Loads the camera instrinsics for a specific camera from a .csv file
# serial_number -> the serial number of the camera
# return: fx, fy, ppx, ppy
def load_cam_intrinsics(serial_number):
    # Open the frame_metadata csv
    df = pd.read_csv("frame_metadata.csv")
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
def create_pcd(depth_image, colour_image, fx, fy, ppx, ppy, 
               transformation, depth_scale, depth_trunc):
    
    # Define intrinsic parameters for Open3D
    intrinsic = o3d.camera.PinholeCameraIntrinsic(depth_image.shape[1], depth_image.shape[0], fx, fy, ppx, ppy)
    # o3d_depth_image = o3d.geometry.Image(depth_image)
    
    # Convert depth and color images to Open3D format
    rgbd_image = o3d.geometry.RGBDImage.create_from_color_and_depth(
        o3d.geometry.Image(colour_image),
        o3d.geometry.Image(depth_image),
        depth_scale=depth_scale,
        depth_trunc=depth_trunc,  
        convert_rgb_to_intensity=False
    )

    # Create point cloud from RGBD image
    pcd = o3d.geometry.PointCloud.create_from_rgbd_image(rgbd_image, intrinsic)
    
    return pcd


if __name__ == "__main__":
    # The frame number from the software synchronisation
    frame_number = 0
        
    # Store the serial numbers
    serial_numbers = ["138322252073", "141322252882"]
    
    for device in serial_numbers:
        serial = np.int64(device)
        # Load images
        colour_image, depth_image = load_images_from_png(serial, frame_number)
        
        # Load camera instrinsics
        fx, fy, ppx, ppy = load_cam_intrinsics(serial)
        
        # Create the point cloud
        pcd = create_pcd(depth_image, colour_image, fx, fy, ppx, ppy, 1.0, 0.1)
        
        # Display point cloud
        o3d.visualization.draw_geometries([pcd])
        # Save point cloud
        o3d.io.write_point_cloud(device + ".ply", pcd)
    