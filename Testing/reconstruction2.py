import open3d as o3d
import numpy as np
import cv2

# Camera intrinsics for both cameras (using average focal length values for simplicity)
fx1, fy1 = 382.2030, 388.7367  # Camera 1 focal lengths
cx1, cy1 = 317.0201, 243.9064  # Camera 1 principal points

fx2, fy2 = 392.6607, 394.1234  # Camera 2 focal lengths
cx2, cy2 = 315.2463, 246.4275  # Camera 2 principal points

# Intrinsic matrix for Camera 1
K1 = np.array([[fx1, 0, cx1],
               [0, fy1, cy1],
               [0, 0, 1]])

# Intrinsic matrix for Camera 2
K2 = np.array([[fx2, 0, cx2],
               [0, fy2, cy2],
               [0, 0, 1]])

# Transformation matrix (extrinsics) from Camera 1 to Camera 2
T = np.array([[0.8905, -0.0015,  0.4550, 251.0631],
              [-0.0087, 0.9998, 0.0204, 3.0915],
              [-0.4549, -0.0222, 0.8903, 74.1394],
              [0, 0, 0, 1]])

# Load depth and color images (placeholders; replace with actual paths to your images)
depth_image1 = cv2.imread("rgb_images/depth_frame_570_cam138322252073.png", cv2.IMREAD_UNCHANGED)
color_image1 = cv2.imread("depth_images/rgb_frame_570_cam138322252073.png")
depth_image2 = cv2.imread("rgb_images/depth_frame_571_cam138322252073.png", cv2.IMREAD_UNCHANGED)
color_image2 = cv2.imread("depth_images/rgb_frame_571_cam138322252073.png")

# Create Open3D point clouds from the depth images
def create_point_cloud_from_depth_image(depth_image, color_image, intrinsic_matrix):
    # Create Open3D RGBD image
    color = o3d.geometry.Image(cv2.cvtColor(color_image, cv2.COLOR_BGR2RGB))
    depth = o3d.geometry.Image(depth_image)
    rgbd_image = o3d.geometry.RGBDImage.create_from_color_and_depth(color, depth, convert_rgb_to_intensity=False)
    
    # Create intrinsic parameters object
    intrinsics = o3d.camera.PinholeCameraIntrinsic()
    intrinsics.set_intrinsics(depth_image.shape[1], depth_image.shape[0], intrinsic_matrix[0, 0], intrinsic_matrix[1, 1],
                              intrinsic_matrix[0, 2], intrinsic_matrix[1, 2])

    # Generate point cloud
    point_cloud = o3d.geometry.PointCloud.create_from_rgbd_image(rgbd_image, intrinsics)
    return point_cloud

# Generate point clouds for both cameras
pcd1 = create_point_cloud_from_depth_image(depth_image1, color_image1, K1)
pcd2 = create_point_cloud_from_depth_image(depth_image2, color_image2, K2)

# Transform the second point cloud to align with the first point cloud
pcd2.transform(T)

# Combine the point clouds
pcd_combined = pcd1 + pcd2

# Save the combined point cloud
o3d.io.write_point_cloud("3d_reconstruction.ply", pcd_combined)

# Visualize the combined point cloud
o3d.visualization.draw_geometries([pcd_combined], window_name="3D Reconstruction", width=800, height=600)

print("3D reconstruction saved as 3d_reconstruction.ply")
