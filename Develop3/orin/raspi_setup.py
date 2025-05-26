import os
import shutil
import socket
import time
from flask import Flask, request, jsonify
import csv

# Initialise flask server
app = Flask(__name__)      
     

""" Uses UDP to broadcast commands to Raspberry Pi 5s in the network """
def send_command_to_raspis():
    # Broadcast address to send to all devices in the subnet
    BROADCAST_IP = "192.168.249.255"
    
    # Port to broadcast on
    PORT = 5005

    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    try:
        command = "GET_SERIAL"
        sock.sendto(command.encode(), (BROADCAST_IP, PORT))
        print(f"Broadcast message sent: {command}")
        time.sleep(5)
            
    except KeyboardInterrupt:
        print("Broadcasting stopped.")
    finally:
        sock.close()


""" Runs the flask server """
@app.route('/raspi_info', methods=['POST'])
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

def save_raspi_to_data_csv(csv_name: str, raspi_info_folder: str):
    """ 
    
    Extract serial numbers and store them in a excel sheet.  
    
    """
    
    # Delete previous uploads folder and then create a new one
    if os.path.exists(csv_name):
        os.remove(csv_name)
    
    csv_data = []
    for filename in os.listdir(raspi_info_folder):
        print(filename)
        pi_name = filename.split("_")[0]
        with open(raspi_info_folder + "/" + filename, "rb") as file:
            garbage = (file.readline()).decode("utf-8")
            serial = int(((file.readline()).decode("utf-8")).split(' ')[12])
            
            csv_data.append([pi_name, serial])
    
    # Write all data to csv file     
    with open(csv_name, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(csv_data)
        

if __name__ == "__main__":
    
    """ Send broadcast message to all raspberrys to get and send their serial numbers. """
    print("Broadcasting to all connected raspberry pis...")
    send_command_to_raspis()
    
    
    """ Receive the files sent from the raspberry pi 5s. A flask server is created and the program
    then waits for files from the pis. The server is terminated by inputting: Ctrl + C, into the 
    terminal. """
    # Delete previous uploads folder and then create a new one
    UPLOAD_FOLDER = './raspi_info'
    if os.path.exists(f"raspi_info"):
        shutil.rmtree(UPLOAD_FOLDER)
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
    # Tell which folder to use
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    
    # Start Flask server
    app.run(host='0.0.0.0', port=5000)

    # Extract and store raspi serial info
    csv_name = "raspi_serial_numbers.csv"
    raspi_info_folder = "raspi_info"
    save_raspi_to_data_csv(csv_name, raspi_info_folder)