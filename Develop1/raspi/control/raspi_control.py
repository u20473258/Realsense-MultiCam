import os
import shutil
import socket
import subprocess
import requests
                          

""" Deletes previously captured data, if any, and creates new file directories for 
the new data """
def create_file_directories():
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
    

""" Capture num_frames frames using capture script """
def capture(num_frames):
    frame_options = {"15" : "1",
                     "30" : "2",
                     "75" : "5",
                     "150" : "10",
                     "225" : "15",
                     "300" : "20",
                     "375" : "25",
                     "450" : "30",
                     "900" : "60",
                     "1500" : "100"}
    
    try:
        capture_command = "./capture " + num_frames
        subprocess.run(["./capture "], check=True)
        print("Capture " + num_frames + " frames (" + frame_options[num_frames] + "s) complete successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error executing Python script: {e}")


""" Reboot raspberry pi """   
def reboot_system():
    try:
        print("Rebooting system...")
        subprocess.run(["sudo", "reboot"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error rebooting system: {e}")
     
        
""" Waits for message from Jetson Orin Nano and then executes the commend sent """
def wait_for_command_from_orin():
    # Port to listen on
    PORT = 5005
    
    # Max size for incoming messages
    BUFFER_SIZE = 1024

    # Create a UDP socket for listening
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # Bind to all interfaces
    sock.bind(("", PORT))

    print(f"Listening for broadcast messages on port {PORT}...")
    
    # Wait until command is received
    command_not_received = True
    try:
        while command_not_received:
            data, addr = sock.recvfrom(BUFFER_SIZE)
            message = data.decode().strip()
            print(f"Received message: {message} from {addr}")
            
            # Command handling
            if message == "CAPTURE_1s":
                capture("15")
                command_not_received = False
                
            elif message == "CAPTURE_2s":
                capture("30")
                command_not_received = False
                
            elif message == "CAPTURE_5s":
                capture("75")
                command_not_received = False
                
            elif message == "CAPTURE_10s":
                capture("150")
                command_not_received = False
                
            elif message == "CAPTURE_15s":
                capture("225")
                command_not_received = False
                
            elif message == "CAPTURE_20s":
                capture("300")
                command_not_received = False
                
            elif message == "CAPTURE_25s":
                capture("375")
                command_not_received = False
                
            elif message == "CAPTURE_30s":
                capture("450")
                command_not_received = False
                
            elif message == "CAPTURE_60s":
                capture("900")
                command_not_received = False
                
            elif message == "CAPTURE_100s":
                capture("1500")
                command_not_received = False
                
            elif message == "REBOOT":
                reboot_system()
                command_not_received = False
                
            else:
                print(f"Unknown command: {message}")
            
    except KeyboardInterrupt:
        print("UDP Listener interrupted. Closing socket...")

    finally:
        sock.close()
        print("Socket closed.")


""" Use HTTP REST API POST command to send all captured data to Jetson Orin Nano """
def send_files_to_orin(pi):
    # Jetson Orin Nano's IP address
    url = "http://192.168.249.145:5000/uploads"

    # Store the frame number to send to orin nano
    colour_frame_number = int(input("What colour frame should be used?"))
    depth_frame_number = int(input("What depth frame number should be used?"))

    # List of file paths to send
    folder_paths_to_Send = [
        f"colour",
        f"depth",
        f"colour_metadata",
        f"depth_metadata"
    ]

    for folder_path in folder_paths_to_Send:
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            
            # Ensure it's a file
            if os.path.isfile(file_path):
                with open(file_path, "rb") as file:
                    # Send the file with its original name
                    files = {"file": (filename, file)}
                    response = requests.post(url, files=files)
                    
                    # Print response
                    print(f"Uploaded {filename}: {response.status_code} - {response.text}")
                    

if __name__ == "__main__":
    pi_name = "raspi1"
    
    while(True):
        create_file_directories()
        wait_for_command_from_orin()
        send_files_to_orin(pi_name)