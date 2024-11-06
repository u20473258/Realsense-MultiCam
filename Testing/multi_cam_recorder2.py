import pyrealsense2 as rs
from multiprocessing import Process, Queue
import cv2
import numpy as np
import csv
import os
import shutil

# Define a function for capturing frames from a single camera
def capture_frames(serial_number, queue):
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_device(serial_number)
    config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
    config.enable_stream(rs.stream.depth, 848, 480, rs.format.z16, 30)
    
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
            
            # Get camera intrinsics
            intrinsics = color_frame.profile.as_video_stream_profile().intrinsics
            fx, fy, ppx, ppy = intrinsics.fx, intrinsics.fy, intrinsics.ppx, intrinsics.ppy

            
            # Retrieve timestamps
            rgb_timestamp = color_frame.get_timestamp()
            depth_timestamp = depth_frame.get_timestamp()
            
            depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)
            
            frame_number += 1
            
            # Send frames to the queue
            queue.put((serial_number, color_image, depth_colormap, rgb_timestamp, depth_timestamp, frame_number, fx, fy, ppx, ppy))

    finally:
        pipeline.stop()

# Process the frames from the queue
def process_frames(queue, csv_filename):
    while True:
        # Receive data from the queue
        serial_number, color_image, depth_image, rgb_timestamp, depth_timestamp, frame_number, fx, fy, ppx, ppy = queue.get()
        
        # Display or process frames as needed
        cv2.imshow(f"Color Stream - Camera {serial_number}", color_image)
        cv2.imshow(f"Depth Stream - Camera {serial_number}", depth_image)
        
        # Write metadata to CSV
        with open(csv_filename, mode="a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([
                frame_number, serial_number, rgb_timestamp, depth_timestamp, fx, fy, ppx, ppy
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

os.makedirs("rgb_images", exist_ok=True)
os.makedirs("depth_images", exist_ok=True)

# Create csv files for each camera's metadata
csv_filename = "frame_metadata.csv"
with open(csv_filename, mode="w", newline="") as file:
    writer = csv.writer(file)
    # Write CSV header
    writer.writerow(["frame_number", "serial_number", "rgb_timestamp", 
                     "depth_timestamp", "fx", "fy", "ppx", "ppy"])

# Start a process for each camera
processes = []
for device in ctx.devices:
    p = Process(target=capture_frames, args=(device.get_info(rs.camera_info.serial_number), frame_queue))
    processes.append(p)
    p.start()

# Start a single process to handle frame processing
process_frames_process = Process(target=process_frames, args=(frame_queue, csv_filename))
process_frames_process.start()

# Wait for all camera processes to finish
for p in processes:
    p.join()

# Terminate the frame processing process
process_frames_process.terminate()
