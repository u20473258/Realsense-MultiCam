import zmq
import cv2
import numpy as np

# Raspberry Pi addresses
pi_addresses = ["192.168.1.10", "192.168.1.11"]

# Connect to all Raspberry Pis
control_sockets = []
for address in pi_addresses:
    context = zmq.Context()
    socket = context.socket(zmq.REQ)  # Request socket for control
    socket.connect(f"tcp://{address}:5555")
    control_sockets.append(socket)

# Subscribe to video streams
stream_context = zmq.Context()
stream_socket = stream_context.socket(zmq.SUB)
for address in pi_addresses:
    stream_socket.connect(f"tcp://{address}:5556")
stream_socket.setsockopt_string(zmq.SUBSCRIBE, '')

def send_command(command):
    for socket in control_sockets:
        socket.send_string(command)
        print(socket.recv_string())  # Wait for response

# Start recording
send_command("START")

try:
    while True:
        # Receive and display video streams
        frame = stream_socket.recv()
        np_frame = np.frombuffer(frame, dtype=np.uint8)
        image = cv2.imdecode(np_frame, cv2.IMREAD_COLOR)
        cv2.imshow("Jetson Video Stream", image)

        # Break on keypress
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
finally:
    # Stop recording
    send_command("STOP")
    cv2.destroyAllWindows()
