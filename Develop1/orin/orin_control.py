import os
import shutil
import socket
import time
from flask import Flask, request, jsonify
import numpy as np
import csv
import cv2

# Initialise flask server
app = Flask(__name__)      
     

""" Uses UDP to broadcast commands to Raspberry Pi 5s in the network """
def send_command_to_raspis(command, capture_duration):
    # Broadcast address to send to all devices in the subnet
    BROADCAST_IP = "192.168.249.255"
    
    # Port to broadcast on
    PORT = 5005

    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    # Store the different capture commands
    capture_commands = ["CAPTURE_1s",
                "CAPTURE_2s",
                "CAPTURE_5s",
                "CAPTURE_10s",
                "CAPTURE_15s",
                "CAPTURE_20s",
                "CAPTURE_25s",
                "CAPTURE_30s",
                "CAPTURE_60s",
                "CAPTURE_100s"]
    
    try:
        if command == 'C':
            if capture_duration == 1:
                sock.sendto(capture_commands[0].encode(), (BROADCAST_IP, PORT))
                print(f"Broadcast message sent: {capture_commands[0]}")
                time.sleep(5)
                
            elif capture_duration == 2:
                sock.sendto(capture_commands[1].encode(), (BROADCAST_IP, PORT))
                print(f"Broadcast message sent: {capture_commands[1]}")
                time.sleep(5)
                
            elif capture_duration == 5:
                sock.sendto(capture_commands[2].encode(), (BROADCAST_IP, PORT))
                print(f"Broadcast message sent: {capture_commands[2]}")
                time.sleep(5)
                
            elif capture_duration == 10:
                sock.sendto(capture_commands[3].encode(), (BROADCAST_IP, PORT))
                print(f"Broadcast message sent: {capture_commands[3]}")
                time.sleep(5)
                
            elif capture_duration == 15:
                sock.sendto(capture_commands[4].encode(), (BROADCAST_IP, PORT))
                print(f"Broadcast message sent: {capture_commands[4]}")
                time.sleep(5)
                
            elif capture_duration == 20:
                sock.sendto(capture_commands[5].encode(), (BROADCAST_IP, PORT))
                print(f"Broadcast message sent: {capture_commands[5]}")
                time.sleep(5)
                
            elif capture_duration == 25:
                sock.sendto(capture_commands[6].encode(), (BROADCAST_IP, PORT))
                print(f"Broadcast message sent: {capture_commands[6]}")
                time.sleep(5)
                
            elif capture_duration == 30:
                sock.sendto(capture_commands[7].encode(), (BROADCAST_IP, PORT))
                print(f"Broadcast message sent: {capture_commands[7]}")
                time.sleep(5)
                
            elif capture_duration == 60:
                sock.sendto(capture_commands[8].encode(), (BROADCAST_IP, PORT))
                print(f"Broadcast message sent: {capture_commands[8]}")
                time.sleep(5)
                
            elif capture_duration == 100:
                sock.sendto(capture_commands[9].encode(), (BROADCAST_IP, PORT))
                print(f"Broadcast message sent: {capture_commands[9]}")
                time.sleep(5)
                
            else:
                print("Incorrect capture duration received, terminating program...")
                exit(1)
            
        elif command == 'R':
            reboot_command = "REBOOT"
            sock.sendto(reboot_command.encode(), (BROADCAST_IP, PORT))
            print(f"Broadcast message sent: {reboot_command}")
            time.sleep(5)
            
    except KeyboardInterrupt:
        print("Broadcasting stopped.")
    finally:
        sock.close()


""" Runs the flask server """
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


""" Receives the files sent from the raspberry pi 5s. A flask server is created and the program
then waits for files from the pis. The server is terminated by inputting: Ctrl + C, into the 
terminal. """
def receive_files_from_pis():
    # Delete previous uploads folder and then create a new one
    UPLOAD_FOLDER = './uploads'
    if os.path.exists(f"uploads"):
        shutil.rmtree(UPLOAD_FOLDER)
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
    # Tell which folder to use
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    
    # Start Flask server
    app.run(host='0.0.0.0', port=5000)


""" Perform a basic processing step: convert depth.csv files into pngs and save them """
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
    
    raspberrys = ["raspi1", "raspi2"]
    
    while(True):
        # Promt user to get command
        print("Please select one of the following commands to proceed:\n")
        print("C -> Begin Capture\n")
        print("R -> Reboot Raspberry Pi 5s\n")
        command = input("Enter command")
        
        if command == 'C':
            print("How long, in seconds, should the cameras capture?\n")
            capture_duration = int(input("Choose from the following: 1, 2, 5, 10, 15, 20, 25, 30, 60, 100"))
            send_command_to_raspis(command, capture_duration)
        elif command == 'R':
            send_command_to_raspis(command, -1)
        else:
            print("Incorrect command received, terminating program...")
            exit(1)
            
        receive_files_from_pis()
        convert_csv_to_depth(raspberrys)

