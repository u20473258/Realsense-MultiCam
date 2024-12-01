import open3d as o3d
import numpy as np

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
    
# Downsamples point clouds to reduce computational costs, applies noise filtering and computers normals for robust alignment.
# pcd -> point cloud
# voxel_size -> size of voxel
# return: pre-processed point cloud
def preprocess_point_cloud(pcd, voxel_size):
    pcd_down = pcd.voxel_down_sample(voxel_size)
    pcd_down.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=voxel_size * 2, max_nn=30))
    return pcd_down

# Performs global registration/initial registration. Rough registration using a RANSAC-based algorithm.
# source -> point cloud to register
# target -> stationary point cloud 
# voxel_size -> size of voxel
# return: transformation matrix
def pairwise_registration(source, target, voxel_size):
    distance_threshold = voxel_size * 1.5
    source_down = source
    target_down = target
    
    # Global registration
    result = o3d.pipelines.registration.registration_icp(
        source_down, target_down, distance_threshold, 
        np.eye(4), o3d.pipelines.registration.TransformationEstimationPointToPlane())
    
    return result.transformation

    
if __name__ == "__main__":
    # Store the serial numbers
    serial_numbers = ["138322250306", "138322252073", "141322252627", "141322252882"]
    
    # Load point cloud
    point_clouds = [load_point_cloud(device) for device in serial_numbers]
    
    # Pre-process point clouds
    voxel_size = 0.02
    processed_pcs = [preprocess_point_cloud(pcd, voxel_size) for pcd in point_clouds]
    
    # Register point clouds pairwise
    transformations = [np.eye(4)]
    for i in range(len(processed_pcs) - 1):
        transformation = pairwise_registration(processed_pcs[i + 1], processed_pcs[0], voxel_size)
        transformations.append(transformation)
        
    # Apply transformations
    aligned_pcs = []
    for i, pcd in enumerate(processed_pcs):
        aligned_pcd = pcd.transform(transformations[i])
        aligned_pcs.append(aligned_pcd)
        
        # Visualize aligned point clouds
        o3d.visualization.draw_geometries(aligned_pcd)
    
    # Define the combined point cloud
    pcd_combined = o3d.geometry.PointCloud()
    for pcd in aligned_pcs:
        pcd_combined += pcd
        
    # Visualize combined point cloud
    o3d.visualization.draw_geometries(pcd_combined)
        
    # Save the combined point cloud
    filename = f"point_clouds/reconstruction.ply"
    o3d.io.write_point_cloud(filename, pcd_combined)
    
