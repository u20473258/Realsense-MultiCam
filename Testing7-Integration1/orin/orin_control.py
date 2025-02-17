import os
import shutil
import socket
import threading
import time
from flask import Flask, request, jsonify
import numpy as np
import csv
import cv2

app = Flask(__name__)      
     

################### CAPTURE AND TRANSFER STATE ###################### 

@app.route('/uploads', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"})

    # Save the uploaded file in the uploads directory
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)
    
    return jsonify({"message": f"File {file.filename} saved at {file_path}"})

def shutdown_after_duration(duration):
    """Run a timer and then shut down the server after the given duration."""
    print(f"[INFO] Server will run for {duration} seconds.")
    time.sleep(duration)
    print("\n[INFO] Time's up! Shutting down the server...")
    os._exit(0)  # Forcefully exits the process

# Run capture script for 30s    
def receive_data():
    UPLOAD_FOLDER = './uploads'
    # Checkes if directories exist
    if os.path.exists(f"uploads"):
        shutil.rmtree(UPLOAD_FOLDER)
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Create the uploads folder if it doesn't exist
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    
    # duration = 100  # Duration in seconds (e.g., 5 minutes = 300 seconds)
    # timer_thread = threading.Thread(target=shutdown_after_duration, args=(duration,))
    # timer_thread.start()
    app.run(host='0.0.0.0', port=5000)


################### WAIT STATE ###################### 

# Wait for user to start program and then broadcast to raspberry pis
def wait_for_capture():
    BROADCAST_IP = "255.255.255.255"  # Broadcast address to send to all devices in the subnet
    PORT = 5005                       # Port to broadcast on

    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    commands = ["CAPTURE_30", "REBOOT"]  # Different command types
    
    standby = True
    while (standby):
        start = input("Press Y to start capture...\n")
        if start == 'Y':
            standby = False
    command = input("Press 1 to capture and 2 to reboot raspberry pis...\n")
    try:
        if command == '1':
            sock.sendto(commands[0].encode(), (BROADCAST_IP, PORT))
            print(f"Broadcast message sent: {commands[0]}")
            time.sleep(5)
        elif command == '2':
            sock.sendto(commands[1].encode(), (BROADCAST_IP, PORT))
            print(f"Broadcast message sent: {commands[1]}")
            time.sleep(5)
    except KeyboardInterrupt:
        print("Broadcasting stopped.")
    finally:
        sock.close()


################### PROCESSING STATE ###################### 

# Convert the depth image .csv to depth image pngs
def convert_csv_to_depth(raspis):
    image_sets = []
    for i in raspberrys:
        frame_number = input("What depth frame number should be used for " + i)
        image_sets.append(int(frame_number))
    
    # Depth image relative path
    relative_path = "uploads/"
    
    # Store depth image dimensions/resolution
    depth_image_width = 640
    depth_image_height = 480
    
    # For each raspberry pi
    for x in range(len(raspis)):
        depth_image_path = relative_path + raspis[x] + "_depth_" + str(image_sets[x]) + ".csv"
        
        # Create the numpy array depth image
        depth_image = np.empty((depth_image_height, depth_image_width), dtype=float)  
        # Access the depth image .csv file and extract the data
        with open(depth_image_path, newline='') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=",", quotechar='|')
            i = 0
            for row in spamreader:
                j = 0
                for depth in row:
                    if j != 640:
                        depth_image[i,j] = float(depth)
                        j += 1
                i += 1

        # Apply a colour map to the depth image
        depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=25.5), cv2.COLORMAP_JET)
        # Save depth image
        depth_filename = relative_path + raspis[x] + "_depth_image_" + str(image_sets[x]) + ".png"
        cv2.imwrite(depth_filename, depth_colormap)

if __name__ == "__main__":
    
    raspberrys = ["raspi1"]
    
    while(True):
        wait_for_capture()
        receive_data()
        convert_csv_to_depth(raspberrys)

