import requests

# Replace with your Jetson's IP address
url = "192.168.249.145"

# Store the name of the raspberry pi
pi_name = "raspi1"

# Store the frame number to send to orin nano
colour_frame_number = 100
depth_frame_number = 100

# List of files to send
files_to_send = [
    f"{pi_name}/colour/{pi_name}_colour_{colour_frame_number}.png",
    f"{pi_name}/depth/{pi_name}_depth_{depth_frame_number}.csv",
    f"{pi_name}/colour_metadata/{pi_name}_colour_metadata_{colour_frame_number}.csv",
    f"{pi_name}/depth_metadata/{pi_name}_depth_metadata_{depth_frame_number}.csv"
]

for file_path in files_to_send:
    with open(file_path, 'rb') as f:
        file_name = file_path.split("/")[-1]  # Get the file name from the path
        files = {'file': (file_name, f)}  # Send the file with its original name
        response = requests.post(url, files=files)
        
        # Print the server's response
        print(f"Response for {file_name}: {response.json()}")
