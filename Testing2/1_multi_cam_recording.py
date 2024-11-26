import pyrealsense2 as rs
from multiprocessing import Process, Queue
import cv2
import numpy as np
import csv
import os
import shutil

# Loads the rgb and depth timestamp for a specific camera from a .csv file
# serial_number -> the serial number of the camera
def get_camera_intrinsics(serial_number, csv_filename):
    # Initialize the pipeline
    pipeline = rs.pipeline()
    config = rs.config()

    # Configure the stream
    config.enable_device(serial_number)
    config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 5)  # Color stream
    config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 5)   # Depth stream

    # Start the pipeline
    pipeline_profile = pipeline.start(config)

    # Get stream profiles
    color_profile = pipeline_profile.get_stream(rs.stream.color)  # Color stream
    depth_profile = pipeline_profile.get_stream(rs.stream.depth)  # Depth stream

    # Get intrinsics
    color_intrinsics = color_profile.as_video_stream_profile().get_intrinsics()
    depth_intrinsics = depth_profile.as_video_stream_profile().get_intrinsics()

    # Print intrinsic parameters
    # print("Color Camera Intrinsics:")
    # print(f"  Width: {color_intrinsics.width}")
    # print(f"  Height: {color_intrinsics.height}")
    # print(f"  Focal Length (fx, fy): ({color_intrinsics.fx}, {color_intrinsics.fy})")
    # print(f"  Principal Point (cx, cy): ({color_intrinsics.ppx}, {color_intrinsics.ppy})")
    # print(f"  Distortion Model: {color_intrinsics.model}")
    # print(f"  Distortion Coefficients: {color_intrinsics.coeffs}")

    # print("\nDepth Camera Intrinsics:")
    # print(f"  Width: {depth_intrinsics.width}")
    # print(f"  Height: {depth_intrinsics.height}")
    # print(f"  Focal Length (fx, fy): ({depth_intrinsics.fx}, {depth_intrinsics.fy})")
    # print(f"  Principal Point (cx, cy): ({depth_intrinsics.ppx}, {depth_intrinsics.ppy})")
    # print(f"  Distortion Model: {depth_intrinsics.model}")
    # print(f"  Distortion Coefficients: {depth_intrinsics.coeffs}")
    
    # Write metadata to CSV
    with open(csv_filename, mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([
            serial_number, color_intrinsics.fx, color_intrinsics.fy, color_intrinsics.ppx, color_intrinsics.ppy
        ])

    # Stop the pipeline
    pipeline.stop()


# Define a function for capturing frames from a single camera
def capture_frames(serial_number, queue):
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_device(serial_number)
    config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 5)
    config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 5)
    
    profile = pipeline.start(config)
    
    # Store frame number
    frame_number = 0
    
    # Create an align object to align depth to color for each pipeline
    align = rs.align(rs.stream.color)

    try:
        while True:
            # Get frames
            frames = pipeline.wait_for_frames()
            
            # Align the colour and depth frames
            aligned_frames = align.process(frames)
            
            # Get aligned depth and colour frames
            color_frame = aligned_frames.get_color_frame()
            depth_frame = aligned_frames.get_depth_frame()
            
            # If frames could not be retrieved
            if not color_frame or not depth_frame:
                continue
            
            # Convert frames to numpy arrays
            color_image = np.asanyarray(color_frame.get_data())
            depth_image = np.asanyarray(depth_frame.get_data())
            
            # Retrieve timestamps
            rgb_timestamp = color_frame.get_timestamp()
            depth_timestamp = depth_frame.get_timestamp()
            
            depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)
            
            frame_number += 1
            
            # Send frames to the queue
            queue.put((serial_number, color_image, depth_colormap, rgb_timestamp, depth_timestamp, frame_number))

    finally:
        pipeline.stop()

# Process the frames from the queue
def process_frames(queue, csv_filename):
    while True:
        # Receive data from the queue
        serial_number, color_image, depth_image, rgb_timestamp, depth_timestamp, frame_number = queue.get()
        
        # Display or process frames as needed
        cv2.imshow(f"Color Stream - Camera {serial_number}", color_image)
        cv2.imshow(f"Depth Stream - Camera {serial_number}", depth_image)
        
        # Write metadata to CSV
        with open(csv_filename, mode="a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([
                frame_number, serial_number, rgb_timestamp, depth_timestamp
            ])
            
        # Save RGB image
        rgb_filename = f"rgb_images/rgb_frame_{frame_number}_cam{serial_number}.png"
        cv2.imwrite(rgb_filename, color_image)
        
        # Save depth image
        depth_filename = f"depth_images/depth_frame_{frame_number}_cam{serial_number}.png"
        cv2.imwrite(depth_filename, depth_image)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()

# Get context for handling an arbitrary number of cameras
ctx = rs.context()

# Queue for sharing frames between processes
frame_queue = Queue()

# Configure settings for saving images
if os.path.exists("rgb_images"):
    shutil.rmtree("rgb_images")
if os.path.exists("depth_images"):
    shutil.rmtree("depth_images")
if os.path.exists("frame_metadata.csv"):
    os.remove("frame_metadata.csv")
if os.path.exists("camera_intrinsics.csv"):
    os.remove("camera_intrinsics.csv")

os.makedirs("rgb_images", exist_ok=True)
os.makedirs("depth_images", exist_ok=True)

# Create csv files for each camera's metadata
frame_data_csv = "frame_metadata.csv"
with open(frame_data_csv, mode="w", newline="") as file:
    writer = csv.writer(file)
    # Write CSV header
    writer.writerow(["frame_number", "serial_number", "rgb_timestamp", 
                     "depth_timestamp"])
    
# Create csv files for each camera's intrinsic parameters
camera_intrinsics_csv = "camera_intrinsics.csv"
with open(camera_intrinsics_csv, mode="w", newline="") as file:
    writer = csv.writer(file)
    # Write CSV header
    writer.writerow(["serial_number", "fx", "fy", "ppx", "ppy"])

# Start a process for each camera
processes = []
for device in ctx.devices:
    # Store the camera intrinsics for each camera
    get_camera_intrinsics(device.get_info(rs.camera_info.serial_number), "camera_intrinsics.csv")
    p = Process(target=capture_frames, args=(device.get_info(rs.camera_info.serial_number), frame_queue))
    processes.append(p)
    p.start()

# Start a single process to handle frame processing
process_frames_process = Process(target=process_frames, args=(frame_queue, frame_data_csv))
process_frames_process.start()

# Wait for all camera processes to finish
for p in processes:
    p.join()

# Terminate the frame processing process
process_frames_process.terminate()
