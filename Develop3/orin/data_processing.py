import numpy as np
import csv
import cv2
import os
import open3d as o3d
import numpy as np
from PIL import Image
import pandas as pd
import shutil
import argparse

class raspberry_pi:
    """
    Class of raspberry pi objects. Each raspberry pi has a camera attached to it.
    """
    
    def __init__(self, raspi_name, serial_number):
        """
        Constructor.
        
        Args:
        raspi_name (str): The name of the rasbperry pi object represents.
        serial_number (int): The serial number of the attached D455 camera.
        camera_intrinsics (list): The intrinsic parameters of the attached D455 camera.
        
        """
        
        self.raspi_name = raspi_name
        self.serial_number = serial_number
        
        self.camera_intrinsics = self.load_cam_intrinsics()
        
    def get_raspi_name(self):
        return self.raspi_name
    
    def get_serial_number(self):
        return self.serial_number
    
    """
    # Loads the camera instrinsics for a specific camera from a .csv file
    # serial_number -> the serial number of the camera
    # return: fx, fy, ppx, ppy
    """
    def load_cam_intrinsics(self):
        """
        Loads the camera instrinsics from a .csv file.
        
        Returns:
        list: A list of the total number of frames for each raspberry pi.
        """
    
        # Open the frame_metadata csv
        df = pd.read_csv("camera_intrinsics.csv")
        
        # Search for the correct row
        row_num = 0
        while True:
            if df.loc[row_num, "serial_number"] == self.serial_number:
                break
            else:
                row_num += 1
                        
        return df.loc[row_num, "fx"], df.loc[row_num, "fy"], df.loc[row_num, "ppx"], df.loc[row_num, "ppy"]  


def create_raspberry_pi(raspi):
    """
    Creates a new raspberry pi object.
    
    Args:
    raspi (str): The name of the raspberry pi.
    
    Returns:
    raspberry_pi: A new raspberry_pi object.
    """
    
    # Get the serial number from raspi_serial_numbers csv
    df = pd.read_csv("raspi_serial_numbers.csv")
    
    # Search for the correct row
    row_num = 0
    while True:
        if df.loc[row_num, "raspberry"] == raspi:
            break
        else:
            row_num += 1
    serial_number = df.loc[row_num, "serial_number"]
    
    return raspberry_pi(raspi, serial_number)


def get_total_frame(folder_path, data_type, raspberry_pis):
    """
    Counts the number of frames, of the given data type, each raspberry pi captured.
    
    Args:
    folder_path (str): The folder path of the data to synchronise.
    data_type (str): The data type of the frames to count.
    raspberry_pis (list): A list of raspberry_pi objects.
    
    Returns:
    dict: A dictionary of the total number of frames for each raspberry pi.
    """
    
    total_num_frames = {}
    for raspi in raspberry_pis:
        num_frames = 0
        # Store the filename to use when search directory
        filename = ""
        filename += raspi
        
        # Search for depth frames
        if data_type == "depth":
            filename += "_depth"
            
            # Get all the filenames in the directory and loop through them
            for root, dirs, files in os.walk(folder_path):
                for file in files: 
                    # Count only the .csv files that match the filename 
                    if file.count(filename) != 0 and file.endswith('.csv'):
                        num_frames += 1
                        
        # Search for colour frames
        else:
            filename += "_colour"
            
            # Get all the filenames in the directory and loop through them
            for root, dirs, files in os.walk(folder_path):
                for file in files: 
                    # Count only the .png files that match the filename 
                    if file.count(filename) != 0 and file.endswith('.png'):
                        num_frames += 1
                        
        total_num_frames[raspi] = num_frames
        
    return total_num_frames
        
    
    
    

def sync_depth_data(threshold, folder_path):
    """
    Uses the Time of Arrival timestamps (ToAt) of the depth frame metadata to find
    closely-matching frames (when the difference in ToAt is within the given threshold).
    
    Args:
    threshold (int): The maximum ToAt allowed between frames.
    folder_path (str): The folder path of the data to synchronise.
    
    Returns:
    list: A list of framesets of closely-matching frames.
    """
    
    # Prep for synchronisation
    # Get the number of frames collected for each raspberry pi
    # Get the frame numbers of the collected images for each raspberry pi
    
    # List to store the framesets
    framesets = []
    
    # Loop until just one camera has no more frames to match
    all_cameras_have_frames = True
    while all_cameras_have_frames:
        print("Y")


def main():
    # Get user input
    parser=argparse.ArgumentParser(description="process data")
    parser.add_argument("filename")
    parser.add_argument("raspberry_pis", type=list)
    parser.add_argument("delete_unsynced", choices=['Y', 'y', 'N', 'n'])
    args=parser.parse_args()
    print ("My filename is ", args.filename)
    
    # Create raspberry pi objects
    raspis = []
    for raspi in args.raspberry_pis:
        raspis.append(create_raspberry_pi())
        

if __name__ == "__main__":
    main()
    
    
        
