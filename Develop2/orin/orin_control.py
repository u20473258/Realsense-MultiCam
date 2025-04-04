import os
import shutil
import socket
import time
from flask import Flask, request, jsonify
from data_processing import processor

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



if __name__ == "__main__":
    
    # Store the name of raspberry pi 5s
    raspberrys = ["raspi1", "raspi2", "raspi3", "raspi4", "raspi5"]

    # Serial number of D455 camera for each raspi
    serial_numbers = {"raspi1" : "138322250306",
                    "raspi2" : "138322252073",
                    "raspi3" : "141322252627",
                    "raspi4" : "141322250372",
                    "raspi5" : "141322252882"}

    # Depth capture configuration setup 
    depth_capture_config = {'width' : 640,
                            'height' : 480,
                            'fps' : 15}

    # Colour capture configuration setup 
    colour_capture_config = {'width' : 640,
                            'height' : 480,
                            'fps' : 15}
    
    while(True):
        # Promt user to get command
        print("Please select one of the following commands to proceed:\n")
        print("C -> Begin Capture")
        print("R -> Reboot Raspberry Pi 5s")
        command = input("Enter command:\t")
        
        if command == 'C':
            print("How long, in seconds, should the cameras capture?\n")
            capture_duration = int(input("Choose from the following: 1, 2, 5, 10, 15, 20, 25, 30, 60, 100. \t"))
            send_command_to_raspis(command, capture_duration)
        elif command == 'R':
            send_command_to_raspis(command, -1)
        else:
            print("Incorrect command received, terminating program...")
            exit(1)
            
        receive_files_from_pis()
        
        processor_1 = processor("uploads/", capture_duration, depth_capture_config, colour_capture_config, raspberrys, serial_numbers)

        # Convert some depth csv to png
        # image_sets = []
        # for i in raspberrys:
        #     frame_number = input("What depth frame number should be used for " + i + "\t")
        #     image_sets.append(int(frame_number))
        # processor_1.convert_csv_to_depth(image_sets)

        # Do SW syncing
        print("Performing SW synchronisation now...")

        threshold = 66 #ms
        depth_framesets = processor_1.depth_software_sync(threshold)
        print(depth_framesets)
        print(len(depth_framesets))

        colour_framesets = processor_1.colour_software_sync(threshold, depth_framesets)
        print(colour_framesets)
        print(len(colour_framesets))

        frameset = int(input("Please select the index of the frameset to process further from the given SW colour framesets \t"))

        # Convert the depth images in selected frameset to pngs
        print("Converting depth image .csv files to .png images...")
        for i in range(0, len(raspberrys)):
            processor_1.convert_single_csv_to_depth(i, depth_framesets[colour_framesets[frameset][len(raspberrys)]][i])
            
        # Create point clouds from depth frames in selected frameset
        print("Converting depth image .csv files to .ply point cloud files...")
        depth_scale = 1000.0
        depth_trunc = 1.5
        for i in range(0, len(raspberrys)):
            processor_1.convert_csv_to_pcd(i, depth_framesets[colour_framesets[frameset][len(raspberrys)]][i], depth_scale, depth_trunc)
            
        # Perform registration
        print("Performing registration...")
        reference_raspi = 0
        transformations = processor_1.registration(reference_raspi, depth_framesets[colour_framesets[frameset][len(raspberrys)]], colour_framesets[frameset])
        
        # Perform reconstruction
        print("Performing reconstruction...")
        reference_raspi = 0
        processor_1.reconstruction(reference_raspi, depth_framesets[colour_framesets[frameset][len(raspberrys)]], colour_framesets[frameset], transformations)
        
