import os
import shutil
import socket
import subprocess
import requests
import time
                          

def create_file_directories():
    """
    Deletes previously captured data, if any, and creates new file directories for 
    the new data.
    """
    
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
    

def capture(num_frames: int, duration: int, pi: str):
    """
    Capture a num_frames amount of frames using capture script.
    
    Parameters
    ----------
    num_frames : int
        The total number of frames to capture.
    duration : int
        The actual duration of capture in seconds.
    pi : str
        The hostname of the raspberry pi.
    """
    
    # Convert num frames to an integer
    total_frames = str(num_frames)
    
    try:
        arguments = [total_frames, pi]
        subprocess.run(["./capture"] + arguments, check=True)
        print("Capture " + total_frames + " frames (" + str(duration) + "s) complete successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error executing Python script: {e}")


""" Getting serial number of connected D455 """   
def get_serial_number(pi: str):
    """
    Get the serial number of the connected D455.
    
    Parameters
    ----------
    pi : str
        The hostname of the raspberry pi.
    """
    
    try:
        print("Getting serial number...")
        subprocess.run("rs-enumerate-devices -s >> " + pi + "_serial.txt", shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error getting serial number: {e}")
        
    # Give Orin/Host time to start-up server
    time.sleep(5)


""" Reboot raspberry pi """   
def reboot_system():
    """
    Reboot the raspberry pi.
    """
    
    try:
        print("Rebooting system...")
        subprocess.run(["sudo", "reboot"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error rebooting system: {e}")
     
        
def wait_for_command_from_orin(pi: str) -> str:
    """
    Waits for broadcast message from Jetson Orin Nano and then executes the commend sent.
    
    Parameters
    ----------
    pi : str
        The hostname of the raspberry pi.
    
    Returns
    ----------
    message : str
        The message received from the Orin Nano.
    """
    
    # Port to listen on
    PORT = 5005
    
    # Max size for incoming messages
    BUFFER_SIZE = 1024

    # Create a UDP socket for listening
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # Bind to all interfaces
    sock.bind(("", PORT))

    print(f"Listening for broadcast messages on port {PORT}...")
    
    message = "empty"
    
    # Wait until command is received
    command_not_received = True
    while command_not_received:
        data, addr = sock.recvfrom(BUFFER_SIZE)
        message = data.decode().strip()
        print(f"Received message: {message} from {addr}")
        
        # Command handling
        if message == "CAPTURE_1s":
            capture(fps*1, 1, pi)
            command_not_received = False
            
        elif message == "CAPTURE_2s":
            capture(fps*2, 2, pi)
            command_not_received = False
            
        elif message == "CAPTURE_5s":
            capture(fps*5, 5, pi)
            command_not_received = False
            
        elif message == "CAPTURE_10s":
            capture(fps*10, 10, pi)
            command_not_received = False
            
        elif message == "CAPTURE_15s":
            capture(fps*15, 15, pi)
            command_not_received = False
            
        elif message == "CAPTURE_20s":
            capture(fps*20, 20, pi)
            command_not_received = False
            
        elif message == "CAPTURE_25s":
            capture(fps*25, 25, pi)
            command_not_received = False
            
        elif message == "CAPTURE_30s":
            capture(fps*30, 30, pi)
            command_not_received = False
            
        elif message == "CAPTURE_60s":
            capture(fps*60, 60, pi)
            command_not_received = False
            
        elif message == "CAPTURE_100s":
            capture(fps*100, 100, pi)
            command_not_received = False
            
        elif message == "GET_SERIAL":
            get_serial_number(pi)
            command_not_received = False
            
        elif message == "REBOOT":
            reboot_system()
            command_not_received = False
            
        else:
            print(f"Unknown command: {message}")
            command_not_received = False
            
        sock.close()
        print("Socket closed.")
    
    return message


def send_files_to_orin(send_serial: bool):
    """ 
    Use HTTP REST API POST command to send all captured data to Jetson Orin Nano
    
    Parameters
    ----------
    send_serial: bool
        Boolean that informs function what files to send back to Orin Nano.
    """
    
    if send_serial:
        # Jetson Orin Nano's IP address
        url = "http://192.168.249.155:5000/raspi_info"
        
        filename = pi_name+"_serial.txt"
        # Ensure it's a file
        if os.path.isfile(filename):
            with open(filename, "rb") as file:
                # Send the file with its original name
                file = {"file": (filename, file)}
                response = requests.post(url, files=file)
                
                # Print response
                print(f"Uploaded {filename}: {response.status_code} - {response.text}")
                
    else:
        # Jetson Orin Nano's IP address
        url = "http://192.168.249.155:5000/uploads"

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
    pi_name = socket.gethostname()
    fps = 15
        
    while(True):
        create_file_directories()
        message = wait_for_command_from_orin(pi_name)
        if message == "GET_SERIAL":
            send_files_to_orin(True)
        else:
            send_files_to_orin(False)
