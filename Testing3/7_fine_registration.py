import open3d as o3d
import numpy as np

# Loads images from png file
# folder_path -> folder path to find image
# serial_number -> the serial number of the camera
# return: point cloud
def load_point_cloud(serial_number):
    # Load the .ply file
    file_path = f"point_clouds/{serial_number}.ply"
    pcd = o3d.io.read_point_cloud(file_path)
    
    # Check if the point cloud is loaded
    if not pcd.is_empty():
        return pcd
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
    serial_numbers = ["138322250306", "141322252882"]
    
    # Store initial transformations from Cloud Compare
    # init_transforms = [
    # np.eye(4),  # Camera 1 (identity, reference frame)
    # np.array([[0.952304544001, 0.055685926827, 0.300025220655, -0.337908239954],
    #           [-0.046863706186, 0.998233224821, -0.036527002431, 0.026966347488],
    #           [-0.301529183527, 0.020724536604, 0.953231684883, 0.041012801797],
    #           [0.000000000000, 0.000000000000, 0.000000000000, 1.000000000000]])
    # ]
    init_transforms = [
    np.eye(4),  # Camera 1 (identity, reference frame)
    np.array([[0.935887225885, -0.003083919642, 0.352286232862, -0.368943112841],
              [0.012670791030, 0.999609376345, -0.024910756250, 0.017541172967],
              [-0.352071798756, 0.027777403801, 0.935560721898, 0.053161248312],
              [0.000000000000, 0.000000000000, 0.000000000000, 1.000000000000]])
    ]
    

    
    # Load point cloud
    raw_point_clouds = [load_point_cloud(device) for device in serial_numbers]
    
    # Implement initial transformations
    point_clouds = [pcd.transform(init_transforms[i]) for i, pcd in enumerate(raw_point_clouds)]
    
    # Pre-process point clouds
    voxel_size = 0.002
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
        o3d.visualization.draw_geometries([aligned_pcd])
    
    # Define the combined point cloud
    pcd_combined = o3d.geometry.PointCloud()
    for pcd in aligned_pcs:
        pcd_combined += pcd
        
    # Visualize combined point cloud
    o3d.visualization.draw_geometries([pcd_combined])
        
    # Save the combined point cloud
    filename = f"point_clouds/fine_reconstruction.ply"
    o3d.io.write_point_cloud(filename, pcd_combined)

    
    
