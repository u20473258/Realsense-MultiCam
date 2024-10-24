import pyrealsense2 as rs
import time
import cv2
import numpy as np

# Initialize pipelines for each camera
pipelines = []
serial_numbers = []

ctx = rs.context()
if len(ctx.devices) == 0:
    print("No realsense devices connected.")
    exit()
else:
    for device in ctx.devices:
        pipeline = rs.pipeline()
        config = rs.config()
        config.enable_device(device.get_info(rs.camera_info.serial_number))
        config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
        config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
        pipeline.start(config)
        pipelines.append(pipeline)

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
                
                # Apply colormap on depth image (image must be converted to 8-bit per pixel first)
                depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)
                
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
                
            time.sleep(0.1)

    finally:
        # Stop all pipelines
        for pipeline in pipelines:
            pipeline.stop()
