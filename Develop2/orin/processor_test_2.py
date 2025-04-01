from data_processing import processor
import numpy as np
import open3d as o3d



# Store the name of raspberry pi 5s
raspberrys = ["raspi1", "raspi2", "raspi3", "raspi4"]

# Serial number of D455 camera for each raspi
serial_numbers = {"raspi1" : "138322250306",
                "raspi2" : "138322252073",
                "raspi3" : "141322252627",
                "raspi4" : "141322250372",
                "raspi5" : "141322252882"}

# Depth capture configuration setup 
depth_capture_config = {'width' : 640,
                        'height' : 480,
                        'fps' : 15}

# Colour capture configuration setup 
colour_capture_config = {'width' : 640,
                        'height' : 480,
                        'fps' : 15}

# How long in seconds is the capture done for
capture_duration = 10 #s

# Convert some depth csv to png
# image_sets = []
# for i in raspberrys:
#     frame_number = input("What depth frame number should be used for " + i + "\t")
#     image_sets.append(int(frame_number))
# processor_1.convert_csv_to_depth(image_sets)

processing_empty_crush = False

if processing_empty_crush == False:
    processor_1 = processor("25_Mar_OP_6_uploads_five_10_15/", capture_duration, depth_capture_config, 
                            colour_capture_config, raspberrys, serial_numbers, processing_empty_crush)
    
    # Do SW syncing
    print("Performing SW synchronisation now...")
    threshold = 66 #ms
    depth_framesets = processor_1.depth_software_sync(threshold)
    print(depth_framesets)
    print(len(depth_framesets))

    colour_framesets = processor_1.colour_software_sync(threshold, depth_framesets)
    print(colour_framesets)
    print(len(colour_framesets))


    # frameset = int(input("Please select the index of the frameset to process further from the given SW colour framesets \t"))
    frameset = 0 # REMOVE IN FINAL PROGRAM


    # Isolate frameset images in their own directory (processed data folder)
    print("Separating frameset images...")
    processor_1.separate_frameset_images(depth_framesets[colour_framesets[frameset][len(raspberrys)]], colour_framesets[frameset])


    # Rotate upside down images: raspi 1 and 3
    print("Rotating upside down images...")
    # Rotate raspi 1
    processor_1.rotate_image(0, depth_framesets[colour_framesets[frameset][len(raspberrys)]][0], True)
    processor_1.rotate_image(0, colour_framesets[frameset][0], False)

    # Rotate raspi 3
    processor_1.rotate_image(2, depth_framesets[colour_framesets[frameset][len(raspberrys)]][2], True)
    processor_1.rotate_image(2, colour_framesets[frameset][2], False)


    # Convert the depth images in selected frameset to pngs
    print("Converting depth image .csv files to .png images...")
    for i in range(0, len(raspberrys)):
        processor_1.convert_single_csv_to_depth(i, depth_framesets[colour_framesets[frameset][len(raspberrys)]][i])


    # Perform depth image cropping
    print("Distance cropping depth images...")
    # raspi1
    depth_cropping_threshold = 1.75
    processor_1.depth_distance_cropping(0, depth_framesets[colour_framesets[frameset][len(raspberrys)]][0], depth_cropping_threshold)
    # raspi2
    depth_cropping_threshold = 1.5
    processor_1.depth_distance_cropping(1, depth_framesets[colour_framesets[frameset][len(raspberrys)]][1], depth_cropping_threshold)
    # raspi3
    depth_cropping_threshold = 2.25
    processor_1.depth_distance_cropping(2, depth_framesets[colour_framesets[frameset][len(raspberrys)]][2], depth_cropping_threshold)
    # raspi4
    depth_cropping_threshold = 2.0
    processor_1.depth_distance_cropping(3, depth_framesets[colour_framesets[frameset][len(raspberrys)]][3], depth_cropping_threshold)
        

    # Subtract the barrier
    print("Subtracting the barriers of the images...")
    empty_images_frameset = [78, 58, 28, 27]
    for i in range(0, len(raspberrys)):
        processor_1.depth_barrier_subtraction(i, depth_framesets[colour_framesets[frameset][len(raspberrys)]][i], empty_images_frameset[i])


    # Create point clouds from depth frames in selected frameset
    print("Converting depth image .csv files to .ply point cloud files...")
    depth_scale = 1000.0
    depth_trunc = 1.5
    for i in range(0, len(raspberrys)):
        processor_1.convert_csv_to_pcd(i, depth_framesets[colour_framesets[frameset][len(raspberrys)]][i], depth_scale, depth_trunc)


    # Perform registration
    print("Performing registration...")
    
    # Load point cloud
    raw_point_clouds = [processor_1.load_point_cloud(raspi, depth_framesets[colour_framesets[frameset][len(raspberrys)]][raspi]) for raspi in range(0, len(raspberrys))]
    
    # Pre-process point clouds
    voxel_size = 0.002
    processed_pcs = [processor_1.preprocess_point_cloud(pcd, voxel_size) for pcd in raw_point_clouds]
    
    # Register point clouds with fgr
    fgr_transformations = [np.eye(4)]
    for i in range(len(processed_pcs) - 1):
        transformation = processor_1.registration_with_fgr(processed_pcs[i + 1], processed_pcs[0])
        fgr_transformations.append(transformation)
    
    # Register point clouds with icp
    icp_transformations = [np.eye(4)]
    for i in range(len(processed_pcs) - 1):
        transformation = processor_1.registration_with_icp(processed_pcs[i + 1], processed_pcs[0], voxel_size)
        icp_transformations.append(transformation)
        
    # reference_raspi = 0
    # transformations = processor_1.registration(reference_raspi, depth_framesets[colour_framesets[frameset][len(raspberrys)]], colour_framesets[frameset])


    # Perform reconstruction
    print("Performing reconstruction...")
    reference_raspi = 0
    # processor_1.reconstruction(reference_raspi, depth_framesets[colour_framesets[frameset][len(raspberrys)]], colour_framesets[frameset], transformations)
    # Combine transformations
    # Define the combined point cloud
    pcd_combined = o3d.geometry.PointCloud()
    
    # Transform point clouds
    point_clouds = []
    i = 0
    for raspi in range(0, len(raspberrys)):
        # Load the .ply file
        point_cloud = processor_1.load_point_cloud(raspi, depth_framesets[colour_framesets[frameset][len(raspberrys)]][raspi])
        
        # Transform point cloud
        point_cloud.transform(fgr_transformations[raspi])
        point_cloud.transform(icp_transformations[raspi])
        i += 1
        
        # Store transformed point cloud
        point_clouds.append(point_cloud)
        pcd_combined += point_cloud
    
    # Visualize aligned point clouds
    o3d.visualization.draw_geometries(point_clouds)
    
    # Save the combined point cloud
    filename = processor_1.processing_data_filepath + "combined_pcd.ply"
    o3d.io.write_point_cloud(filename, pcd_combined)
    print("Combined point cloud saved.")

else:
    processor_1 = processor("25_Mar_OP_8_uploads_five_15_15/", capture_duration, depth_capture_config, 
                            colour_capture_config, raspberrys, serial_numbers, processing_empty_crush)
    
    # Do SW syncing
    print("Performing SW synchronisation now...")
    threshold = 66 #ms
    depth_framesets = processor_1.depth_software_sync(threshold)
    print(depth_framesets)
    print(len(depth_framesets))

    colour_framesets = processor_1.colour_software_sync(threshold, depth_framesets)
    print(colour_framesets)
    print(len(colour_framesets))


    # frameset = int(input("Please select the index of the frameset to process further from the given SW colour framesets \t"))
    frameset = 0 # REMOVE IN FINAL PROGRAM
    
    # Isolate frameset images in their own directory (processed data folder)
    print("Separating frameset images...")
    processor_1.separate_frameset_images(depth_framesets[colour_framesets[frameset][len(raspberrys)]], colour_framesets[frameset])


    # Rotate upside down images: raspi 1 and 3
    print("Rotating upside down images...")
    # Rotate raspi 1
    processor_1.rotate_image(0, depth_framesets[colour_framesets[frameset][len(raspberrys)]][0], True)
    processor_1.rotate_image(0, colour_framesets[frameset][0], False)

    # Rotate raspi 3
    processor_1.rotate_image(2, depth_framesets[colour_framesets[frameset][len(raspberrys)]][2], True)
    processor_1.rotate_image(2, colour_framesets[frameset][2], False)


    # Convert the depth images in selected frameset to pngs
    print("Converting depth image .csv files to .png images...")
    for i in range(0, len(raspberrys)):
        processor_1.convert_single_csv_to_depth(i, depth_framesets[colour_framesets[frameset][len(raspberrys)]][i])


    # Perform depth image cropping
    print("Distance cropping depth images...")
    # raspi1
    depth_cropping_threshold = 1.75
    processor_1.depth_distance_cropping(0, depth_framesets[colour_framesets[frameset][len(raspberrys)]][0], depth_cropping_threshold)
    # raspi2
    depth_cropping_threshold = 1.5
    processor_1.depth_distance_cropping(1, depth_framesets[colour_framesets[frameset][len(raspberrys)]][1], depth_cropping_threshold)
    # raspi3
    depth_cropping_threshold = 2.25
    processor_1.depth_distance_cropping(2, depth_framesets[colour_framesets[frameset][len(raspberrys)]][2], depth_cropping_threshold)
    # raspi4
    depth_cropping_threshold = 1.5
    processor_1.depth_distance_cropping(3, depth_framesets[colour_framesets[frameset][len(raspberrys)]][3], depth_cropping_threshold)
        
