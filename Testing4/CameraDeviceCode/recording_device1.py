import zmq
import pyrealsense2 as rs
import cv2
import numpy as np

# Configure ZeroMQ
context = zmq.Context()
socket = context.socket(zmq.REP)  # Reply socket for control
socket.bind("tcp://*:5555")       # Listen for commands on port 5555

# Video streaming socket
stream_socket = context.socket(zmq.PUB)  # Publish socket for video
stream_socket.bind("tcp://*:5556")       # Stream video on port 5556

# Configure RealSense camera
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
pipeline.start(config)

recording = False

try:
    while True:
        # Listen for commands
        message = socket.recv_string()
        if message == "START":
            recording = True
            socket.send_string("RECORDING STARTED")
        elif message == "STOP":
            recording = False
            socket.send_string("RECORDING STOPPED")
        else:
            socket.send_string("UNKNOWN COMMAND")

        # Capture and stream video frames if recording
        if recording:
            frames = pipeline.wait_for_frames()
            color_frame = frames.get_color_frame()
            if color_frame:
                color_image = np.asanyarray(color_frame.get_data())
                _, encoded_frame = cv2.imencode('.jpg', color_image)
                stream_socket.send(encoded_frame)
finally:
    pipeline.stop()
