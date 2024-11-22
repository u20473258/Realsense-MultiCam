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
    # depth_image = cv2.imread(f"depth_images/depth_frame_{frame_number}_cam{serial_number}.png", cv2.IMREAD_UNCHANGED)
    
    # if depth_image.dtype != np.uint16 and depth_image.dtype != np.float32:
    #     raise ValueError(f"Unsupported depth image format: {depth_image.dtype}. Expected uint16 or float32.")

    
    return colour, depth

# Loads the camera instrinsics for a specific camera from a .csv file
# serial_number -> the serial number of the camera
# frame_number -> which frame or image number to use
# return: fx, fy, ppx, ppy
def load_cam_intrinsics(serial_number, frame_number):
    # Open the frame_metadata csv
    df = pd.read_csv("frame_metadata.csv")
    # Search for the correct row
    row_num = 0
    while True:
        if df.loc[row_num, "serial_number"] == serial_number:
            if df.loc[row_num, "frame_number"] == frame_number:
                break
            else:
                row_num += 1
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
    # pcd = o3d.geometry.PointCloud.create_from_depth_image(o3d_depth_image, intrinsic, depth_scale=depth_scale, depth_trunc=depth_trunc)

    # Apply the transformation for this camera to align it in the common reference frame
    pcd.transform(transformation)
    
    return pcd


if __name__ == "__main__":
    
    # Define transformation matrices for each camera (adjust according to your setup/calibration)
    # transforms = [
    #     np.eye(4),  # Camera 1 (identity, reference frame)
    #     np.array([[0.89808895, -0.03108796, -0.43871377, 0.24462474], [-0.00126753, 0.99731164, -0.07326586, 0.00831586], [0.43981204, 0.06635535, 0.89563516, 0.07487545], [0, 0, 0, 1.0]]),  # Camera 2
    # ]
    transforms = [
    np.eye(4),  # Camera 1 (identity, reference frame)
    np.array([[0.889,	-0.012,	-0.457,	-189.380], [0.001,	1.000,	-0.024,	-1.555], [0.457,	0.021,	0.889,	-180.769],[0.000,	0.000,	0.000,	1.000]])
    ]
    
    frame_numbers = [570, 571, 50]
    
    # Define the combined point cloud
    pcd_combined = o3d.geometry.PointCloud()
    
    # Get context for handling an arbitrary number of cameras
    ctx = rs.context()
    i = 0
    serial_numbers = ["138322252073", "141322252882"]
    point_clouds = []
    for device in serial_numbers:
        # serial = np.int64(device.get_info(rs.camera_info.serial_number))
        serial = np.int64(device)
        colour_image, depth_image = load_images_from_png(serial, frame_numbers[i])
        fx, fy, ppx, ppy = load_cam_intrinsics(serial, frame_numbers[i])
        pcd = create_pcd(depth_image, colour_image, fx, fy, ppx, ppy, transforms[0], 1.0, 0.1)
        # Add generate pcd to combined one
        point_clouds.append(pcd)
        pcd_combined += pcd
        i+=1
    
    # Optional: Downsample the point cloud for noise reduction and efficiency
    # pcd_combined = pcd_combined.voxel_down_sample(voxel_size=0.005)

    # Save the combined point cloud
    o3d.io.write_point_cloud("3d_reconstruction.ply", pcd_combined)

    # Visualize the final combined point cloud
    o3d.visualization.draw_geometries([pcd_combined])

    print("3D reconstruction saved as 3d_reconstruction.ply")
    
    print("Source has color:", point_clouds[0].has_colors())
    print("Target has color:", point_clouds[1].has_colors())



    # # Downsample the point clouds for better performance and noise reduction
    # voxel_size = 0.05  # Set an appropriate voxel size based on your data
    # source_down = point_clouds[0].voxel_down_sample(voxel_size)
    # target_down = point_clouds[1].voxel_down_sample(voxel_size)

    # # Estimate normals for both point clouds (required for ColoredICP)
    # source_down.estimate_normals(o3d.geometry.KDTreeSearchParamHybrid(radius=voxel_size * 2, max_nn=30))
    # target_down.estimate_normals(o3d.geometry.KDTreeSearchParamHybrid(radius=voxel_size * 2, max_nn=30))

    # # Optional: apply an initial transformation (rough alignment) if known
    # # For example, if you have extrinsic calibration, you can transform the source point cloud:
    # trans_init = np.array([[0.89808895, -0.03108796, -0.43871377, 0.24462474], [-0.00126753, 0.99731164, -0.07326586, 0.00831586], [0.43981204, 0.06635535, 0.89563516, 0.07487545], [0, 0, 0, 1.0]])
    # source_down.transform(trans_init)

    # ransac_result = execute_fast_global_registration(source_down, target_down, )

    # # Set ColoredICP parameters
    # # Higher values for voxel size and iterations improve robustness but increase computation time
    # icp_result = o3d.pipelines.registration.registration_colored_icp(
    #     source_down, target_down, voxel_size, trans_init,
    #     o3d.pipelines.registration.TransformationEstimationForColoredICP(),
    #     o3d.pipelines.registration.ICPConvergenceCriteria(relative_fitness=1e-6,
    #                                                     relative_rmse=1e-6,
    #                                                     max_iteration=50))

    # # Print and apply the transformation
    # print("Colored ICP Transformation Matrix:")
    # print(icp_result.transformation)

    # # Apply the resulting transformation to the original source point cloud
    # point_clouds[0].transform(icp_result.transformation)

    # # Visualize the aligned point clouds
    # o3d.visualization.draw_geometries([point_clouds[0], point_clouds[1]])
