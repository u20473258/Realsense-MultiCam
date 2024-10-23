import pyrealsense2 as rs
import time

# Initialize pipelines for each camera
pipelines = []
serial_numbers = ['<serial_number_1>', '<serial_number_2>']  # Replace with your camera serial numbers

for serial in serial_numbers:
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_device(serial)
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
            
            # Here, you could save the frames to disk, or process them as needed
            print(f"Camera {i} - Depth Frame: {depth_frame}, Color Frame: {color_frame}")

        time.sleep(0.1)  # Adjust the sleep time as needed

finally:
    # Stop all pipelines
    for pipeline in pipelines:
        pipeline.stop()
