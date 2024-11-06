import open3d as o3d
import numpy as np
from PIL import Image
import pandas as pd
import pyrealsense2 as rs

# Loads images from png file
# folder_path -> folder path to find image
# serial_number -> the serial number of the camera
# frame_number -> which frame or image number to use
# return: the depth and colour images as numpy arrays
def load_images_from_png(serial_number, frame_number):
    colour = np.array(Image.open(f"Testing/rgb_images/rgb_frame_{frame_number}_cam{serial_number}.png"))
    depth = np.array(Image.open(f"Testing/depth_images/depth_frame_{frame_number}_cam{serial_number}.png"))
    
    return colour, depth

# Loads the camera instrinsics for a specific camera from a .csv file
# serial_number -> the serial number of the camera
# frame_number -> which frame or image number to use
# return: fx, fy, ppx, ppy
def load_cam_intrinsics(serial_number, frame_number):
    # Open the frame_metadata csv
    df = pd.read_csv("Testing/frame_metadata.csv")
    # Search for the correct row
    row_num = 0
    while df.loc[row_num, "serial_number"] != serial_number and df.loc[row_num, "frame_number"] != frame_number:
        row_num += 1
    
    return df.loc[row_num, "fx"], df.loc[row_num, "fy"], df.loc[row_num, "ppx"], df.loc[row_num, "ppy"]

# Creates a point cloud for each camera
# serial_number -> the serial number of the camera
# depth_image -> the depth image
# colour_image -> the colour image
# fx -> focal length x
# fy -> focal length y
# ppx -> principal point x
# ppy -> principal point y
# transformation -> how to align given camera view to common reference frame
# depth_scale -> adjust according to the depth unit in your images (e.g., 1000 for mm to meters)
# depth_trunc -> how much should the depth image be truncated
def create_pcd(serial_number, depth_image, colour_image, fx, fy, ppx, ppy, 
               transformation, depth_scale, depth_trunc):
    
    # Define intrinsic parameters for Open3D
    intrinsic = o3d.camera.PinholeCameraIntrinsic(depth_image.shape[1], depth_image.shape[0], fx, fy, ppx, ppy)
    
    # Convert depth and color images to Open3D format
    rgbd_image = o3d.geometry.RGBDImage.create_from_color_and_depth(
        o3d.geometry.Image(colour_image),
        o3d.geometry.Image(depth_image),
        depth_scale=1000.0,  # Adjust according to the depth unit in your images (e.g., 1000 for mm to meters)
        depth_trunc=3.0,  # Truncate depth at 3 meters
        convert_rgb_to_intensity=False
    )

    # Create point cloud from RGBD image
    pcd = o3d.geometry.PointCloud.create_from_rgbd_image(rgbd_image, intrinsic)

    # Apply the transformation for this camera to align it in the common reference frame
    pcd.transform(transformation)
    
    return pcd


if __name__ == "__main__":
    
    # Define transformation matrices for each camera (adjust according to your setup/calibration)
    transforms = [
        np.eye(4),  # Camera 1 (identity, reference frame)
        np.array([[1, 0, 0, 0.3], [0, 1, 0, 0], [0, 0, 1, 0.1], [0, 0, 0, 1]]),  # Camera 2
        np.array([[1, 0, 0, -0.3], [0, 1, 0, 0], [0, 0, 1, -0.1], [0, 0, 0, 1]])  # Camera 3
    ]
    
    frame_numbers = [50, 50, 50]
    
    # Define the combined point cloud
    pcd_combined = o3d.geometry.PointCloud()
    
    # Get context for handling an arbitrary number of cameras
    ctx = rs.context()
    i = 0
    for device in ctx.devices:
        colour_image, depth_image = load_images_from_png(device.get_info(rs.camera_info.serial_number), frame_numbers[i])
        fx, fy, ppx, ppy = load_cam_intrinsics(device.get_info(rs.camera_info.serial_number), frame_numbers[i])
        pcd = create_pcd(device.get_info(rs.camera_info.serial_number), depth_image, colour_image, fx, fy, ppx, ppy, transforms[i], 1000.0, 3)
        
        pcd_combined += pcd
    
    # Optional: Downsample the point cloud for noise reduction and efficiency
    pcd_combined = pcd_combined.voxel_down_sample(voxel_size=0.005)

    # Save the combined point cloud
    o3d.io.write_point_cloud("3d_reconstruction.ply", pcd_combined)

    # Visualize the final combined point cloud
    o3d.visualization.draw_geometries([pcd_combined])

    print("3D reconstruction saved as 3d_reconstruction.ply")