import os
import shutil
import socket
import subprocess
import requests
           
# Prepare directories for camera data storage
def create_directories():
    # Checkes if directories exist
    if os.path.exists(f"colour"):
        shutil.rmtree(f"colour")
    if os.path.exists(f"depth"):
        shutil.rmtree(f"depth")
    if os.path.exists(f"colour_metadata"):
        shutil.rmtree(f"colour_metadata")
    if os.path.exists(f"depth_metadata"):
        shutil.rmtree(f"depth_metadata")
    
    # Creates new directories for the camera data       
    os.makedirs(f"colour", exist_ok=True)
    os.makedirs(f"depth", exist_ok=True)
    os.makedirs(f"colour_metadata", exist_ok=True)
    os.makedirs(f"depth_metadata", exist_ok=True)


################### CAPTURE STATE ###################### 

# Run capture script for 30 frames    
def capture_30():
    try:
        subprocess.run(["./capture 30"], check=True)
        print("Capture complete successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error executing Python script: {e}")


################### WAIT STATE ######################   
# Reboot raspberry pi     
def reboot_system():
    try:
        subprocess.run(["sudo", "reboot"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error rebooting system: {e}")

# Create UDP socket and listen on that socket
def wait_for_capture():
    PORT = 5005                      # Port to listen on
    BUFFER_SIZE = 1024               # Max size for incoming messages

    # Create a UDP socket for listening
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("", PORT))  # Bind to all interfaces

    print(f"Listening for broadcast messages on port {PORT}...")
    
    command_not_received = True
    while command_not_received:
        data, addr = sock.recvfrom(BUFFER_SIZE)
        message = data.decode().strip()
        print(f"Received message: {message} from {addr}")
        
        # Command handling
        if message == "CAPTURE_30":
            capture_30()
            command_not_received = False
        elif message == "REBOOT":
            reboot_system()
            command_not_received = False
        else:
            print(f"Unknown command: {message}")


################### TRANSFER STATE ######################
# Transfer an image set to Jetson Orin Nano
def transfer_files(pi):
    # Jetson Orin Nano's IP address
    url = "http://192.168.249.145:5000/uploads"

    # Store the frame number to send to orin nano
    colour_frame_number = int(input("What colour frame should be used?"))
    depth_frame_number = int(input("What depth frame number should be used?"))

    # List of files to send
    files_to_send = [
        f"colour/{pi}_colour_{colour_frame_number}.png",
        f"depth/{pi}_depth_{depth_frame_number}.csv",
        f"colour_metadata/{pi}_colour_metadata_{colour_frame_number}.csv",
        f"depth_metadata/{pi}_depth_metadata_{depth_frame_number}.csv"
    ]

    for file_path in files_to_send:
        with open(file_path, 'rb') as f:
            file_name = file_path.split("/")[-1]  # Get the file name from the path
            files = {'file': (file_name, f)}  # Send the file with its original name
            response = requests.post(url, files=files)
            
            # Print the server's response
            print(f"Response for {file_name}: {response}")


if __name__ == "__main__":
    pi_name = "raspi1"
    
    while(True):
        create_directories()
        wait_for_capture()
        transfer_files(pi_name)

