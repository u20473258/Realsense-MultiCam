import pyrealsense2 as rs
from multiprocessing import Process, Queue
import cv2
import numpy as np

# Define a function for capturing frames from a single camera
def capture_frames(serial_number, queue):
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_device(serial_number)
    config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
    config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
    
    pipeline.start(config)

    try:
        while True:
            frames = pipeline.wait_for_frames()
            color_frame = frames.get_color_frame()
            depth_frame = frames.get_depth_frame()
            
            if not color_frame or not depth_frame:
                continue
            
            # Convert frames to numpy arrays
            color_image = np.asanyarray(color_frame.get_data())
            depth_image = np.asanyarray(depth_frame.get_data())
            
            depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)
            
            # Send frames to the queue
            queue.put((serial_number, color_image, depth_colormap))

    finally:
        pipeline.stop()

# Process the frames from the queue
def process_frames(queue):
    while True:
        # Receive data from the queue
        serial_number, color_image, depth_image = queue.get()
        
        # Display or process frames as needed
        cv2.imshow(f"Color Stream - Camera {serial_number}", color_image)
        cv2.imshow(f"Depth Stream - Camera {serial_number}", depth_image)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()

# Get context for handling an arbitrary number of cameras
ctx = rs.context()

# Queue for sharing frames between processes
frame_queue = Queue()

# Start a process for each camera
processes = []
for device in ctx.devices:
    p = Process(target=capture_frames, args=(device.get_info(rs.camera_info.serial_number), frame_queue))
    processes.append(p)
    p.start()

# Start a single process to handle frame processing
process_frames_process = Process(target=process_frames, args=(frame_queue,))
process_frames_process.start()

# Wait for all camera processes to finish
for p in processes:
    p.join()

# Terminate the frame processing process
process_frames_process.terminate()
