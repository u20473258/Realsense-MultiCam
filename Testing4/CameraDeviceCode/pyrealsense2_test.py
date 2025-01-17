import pyrealsense2 as rs
import numpy as np
import cv2

# Configure RealSense camera
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 5)
config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 5)
pipeline.start(config)


# Create an align object to align depth to color for each pipeline
align = rs.align(rs.stream.color)

frame_number = 0

# Begin recording
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
    
    # Convert to depth map    
    depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)
    
    # Save RGB image
    rgb_filename = f"rgb_images/rgb_frame_{frame_number}.png"
    cv2.imwrite(rgb_filename, color_image)
    
    # Save depth image
    depth_filename = f"depth_images/depth_frame_{frame_number}.png"
    cv2.imwrite(depth_filename, depth_image)
    
    frame_number += 1
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
pipeline.stop()