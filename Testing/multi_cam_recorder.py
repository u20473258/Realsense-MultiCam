import pyrealsense2 as rs
import time
import cv2
import numpy as np
import csv
import os

# Initialize pipelines for each camera
pipelines = []
serial_numbers = []

color_intrinsics = []
depth_intrinsics = []
csv_filenames = []

ctx = rs.context()
if len(ctx.devices) == 0:
    print("No realsense devices connected.")
    exit()
else:
    for device in ctx.devices:
        # Configure camera settings
        pipeline = rs.pipeline()
        config = rs.config()
        config.enable_device(device.get_info(rs.camera_info.serial_number))
        config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
        config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
        profile = pipeline.start(config)
        pipelines.append(pipeline)
        
        # Configure settings for saving images
        os.makedirs("rgb_images", exist_ok=True)
        os.makedirs("depth_images", exist_ok=True)
        
        # Configure settings for saving images
        # Initialize CSV file for metadata
        csv_filename = "frame_metadata_" + str(device.get_info(rs.camera_info.serial_number)) + ".csv"
        with open(csv_filename, mode="w", newline="") as file:
            writer = csv.writer(file)
            # Write CSV header
            writer.writerow(["frame_number", "rgb_timestamp", "depth_timestamp", 
                            "fx", "fy", "ppx", "ppy", "width", "height"])
        csv_filenames.append(csv_filename)
        
        # Get and save camera intrinsics
        color_intrinsics.append(profile.get_stream(rs.stream.color).as_video_stream_profile().get_intrinsics())
        depth_intrinsics.append(profile.get_stream(rs.stream.depth).as_video_stream_profile().get_intrinsics())

    # Initialize frame counter
    frame_number = 0

    # Record data
    try:
        while True:
            frames = []
            for pipeline in pipelines:
                frames.append(pipeline.wait_for_frames())

            # Process frames (for example, save them to a file)
            for i, frame in enumerate(frames):
                color_frame = frame.get_color_frame()
                depth_frame = frame.get_depth_frame()
                
                # Check for valid frames
                if not depth_frame or not color_frame:
                    continue
                
                # Convert images to numpy arrays
                depth_image = np.asanyarray(depth_frame.get_data())
                color_image = np.asanyarray(color_frame.get_data())
                
                # Save RGB image
                rgb_filename = f"rgb_images/rgb_frame_{frame_number}_cam{i}.png"
                cv2.imwrite(rgb_filename, color_image)
                
                # Apply colormap on depth image (image must be converted to 8-bit per pixel first) and save
                depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)
                depth_filename = f"depth_images/depth_frame_{frame_number}_cam{i}.png"
                cv2.imwrite(depth_filename, depth_colormap)
                
                # Retrieve timestamps
                rgb_timestamp = color_frame.get_timestamp()
                depth_timestamp = depth_frame.get_timestamp()
                
                # Write metadata to CSV
                with open(csv_filenames[i], mode="a", newline="") as file:
                    writer = csv.writer(file)
                    writer.writerow([
                        frame_number, rgb_timestamp, depth_timestamp, 
                        color_intrinsics[i].fx, color_intrinsics[i].fy, 
                        color_intrinsics[i].ppx, color_intrinsics[i].ppy, 
                        color_intrinsics[i].width, color_intrinsics[i].height
                    ])
                
                # Increment frame counter
                frame_number += 1
                
                # Get the dimensions of the depth and colour map for use later
                depth_colormap_dim = depth_colormap.shape
                color_colormap_dim = color_image.shape
                
                # If depth and color resolutions are different, resize color image to match depth image for display
                if depth_colormap_dim != color_colormap_dim:
                    resized_color_image = cv2.resize(color_image, dsize=(depth_colormap_dim[1], depth_colormap_dim[0]), interpolation=cv2.INTER_AREA)
                    images = np.hstack((resized_color_image, depth_colormap))
                else:
                    images = np.hstack((color_image, depth_colormap))
                    
                cv2.namedWindow('RealSense ' + str(i), cv2.WINDOW_AUTOSIZE)
                cv2.imshow('RealSense ' + str(i), images)
                cv2.waitKey(1)
                
                # Press 'q' to exit
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                
            time.sleep(0.1)

    finally:
        # Stop all pipelines
        for pipeline in pipelines:
            pipeline.stop()
