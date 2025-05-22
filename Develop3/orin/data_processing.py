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
from collections import defaultdict

class raspberry_pi:
    """
    Class of raspberry pi objects. Each raspberry pi has a camera attached to it.
    """
    
    def __init__(self, raspi_name: str, serial_number: int, folder_path: str):
        """
        Constructor.
        
        Args:
        raspi_name (str): The name of the rasbperry pi object represents.
        serial_number (int): The serial number of the attached D455 camera.
        folder_path (str): The folder path containing data collected.
        
        """
        
        self.raspi_name = raspi_name
        self.serial_number = serial_number
        
        self.camera_intrinsics = self.load_cam_intrinsics()
        self.total_num_depth_frames = self.calculate_total_num_frames("depth")
        self.total_num_colour_frames = self.calculate_total_num_frames("colour")
        self.depth_frame_numbers = self.extract_frame_numbers("depth")
        self.colour_frame_numbers = self.extract_frame_numbers("colour")
        
    def get_raspi_name(self) -> str:
        return self.raspi_name
    
    def get_serial_number(self) -> int:
        return self.serial_number
    
    def get_total_num_frames(self, data_type: str) -> int:
        if data_type == "depth":
            return self.total_num_depth_frames
        else:
            return self.total_num_colour_frames
    
    def get_frame_numbers(self, data_type: str) -> list:
        if data_type == "depth":
            return self.depth_frame_numbers
        else:
            return self.colour_frame_numbers
    
    def load_cam_intrinsics(self) -> list:
        """
        Loads the camera instrinsics from a .csv file.
        
        Returns:
        list: A list of the total number of frames for each raspberry pi (fx, fy, ppx, ppy).
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
    
    
    def calculate_total_num_frames(self, data_type: str) -> int:
        """
        Counts the number of frames, of the given data type, captured by the raspberry pi.
        
        Args:
        data_type (str): The data type of the frames to count.
        
        Returns:
        int: Total number of frames for collected by the raspberry pi.
        """
        
        num_frames = 0
        # Store the filename to use when search directory
        filename = ""
        filename += self.raspi_name
        
        # Search for depth frames
        if data_type == "depth":
            filename += "_depth"
            
            # Get all the filenames in the directory and loop through them
            for root, dirs, files in os.walk(self.folder_path):
                for file in files: 
                    # Count only the .csv files that match the filename 
                    if file.count(filename) != 0 and file.endswith('.csv'):
                        num_frames += 1
                        
        # Search for colour frames
        else:
            filename += "_colour"
            
            # Get all the filenames in the directory and loop through them
            for root, dirs, files in os.walk(self.folder_path):
                for file in files: 
                    # Count only the .png files that match the filename 
                    if file.count(filename) != 0 and file.endswith('.png'):
                        num_frames += 1
                            
        return num_frames
            
        
    def extract_frame_numbers(self, data_type: str) -> list:
        """
        Extracts all the frame numbers of a given data type for all given raspberry pis
        in the given folder path.
        
        Args:
        data_type (str): The data type of the frames to count.
        
        Returns:
        defaultdict: A list of the frame numbers for the raspberry pi.
        """
                
        # Scan directory and get an iterator
        obj = os.scandir(self.folder_path)
        
        frame_numbers = []        
        num_frames = self.total_num_depth_frames if data_type == "depth" else self.total_num_colour_frames
        # Loop through each file
        for file in obj:
            # Check if we have already gotten all frame numbers
            if len(frame_numbers) == num_frames:
                break
            
            # Check if the file is for the correct raspi and the file is not metadata
            if (file.name).find(self.raspi_name) != -1 and (file.name).find("metadata") == -1:
                # Check if the file is a colour image and if we are searching for colour images
                if (file.name).find("colour") != -1 and data_type == "colour":
                    # Split file names based on the _ separator
                    split1 = (file.name).split("_")
                    
                    # The 3rd item in the first split will be <fnum>.png. Split again using . as separator
                    split2 = split1[2].split(".")
                    
                    frame_num = int(split2[0])
                    frame_numbers.append(frame_num)
                    
                # Check if the file is a depth image and if we are searching for depth images
                elif (file.name).find("depth") != -1 and data_type == "depth":
                    # Split file names based on the _ separator
                    split1 = (file.name).split("_")
                    
                    # Add a check for if any .png depth image files exist in folder
                    if split1[2] == "image":
                        # The 4th item in the first split will be <fnum>.csv. Split again using . as separator
                        split2 = split1[3].split(".")
                        frame_num = int(split2[0])
                        
                    else:
                        # The 3rd item in the first split will be <fnum>.csv. Split again using . as separator
                        split2 = split1[2].split(".")
                        frame_num = int(split2[0])
                    
                    frame_numbers.append(frame_num)
                else:
                    continue
            else:
                continue
                
        # Close iterator
        obj.close()
        
        return frame_numbers


def create_raspberry_pi(raspi: str, folder_path: str) -> raspberry_pi:
    """
    Creates a new raspberry pi object.
    
    Args:
    raspi (str): The name of the raspberry pi.
    folder_path (str): The folder path of the data to synchronise.
    
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
    
    return raspberry_pi(raspi, serial_number, folder_path)


def get_filename(folder_path: str, date_type: str, raspi_name: str, frame_number: int, is_metadata: bool):
    """
    Function that compiles the filename into a single string using given information.
    
    folder_path (str): The folder path of the data to synchronise.
    data_type (str): The data type of the frames to synchronise.
    raspi_name (str): The name of the raspberry pi object.
    frame_number (int): Frame number of ToAt metadata file.
    is_metadata (bool): Indicate if the file being extracted is metadata.
    
    Return: (str) filename
    """
    
    filename = ""
    filename += folder_path  
    frame_number = str(frame_number) 
    
    if date_type == "depth":
        if is_metadata:
            filename = filename + raspi_name + "_depth_metadata_" + frame_number + ".txt"
        else:
            filename = filename + raspi_name + "_depth_" + frame_number + ".csv"
    else:
        if is_metadata:
            filename = filename + raspi_name + "_colour_metadata_" + frame_number + ".txt"
        else:
            filename = filename + raspi_name + "_colour_" + frame_number + ".png"
    
    return filename


def extract_ToAt_from_file(folder_path: str, date_type: str, raspi_name: str, frame_number: int) -> int: 
    """
    Gets the ToAt from a metadata file with the given .txt filename.

    folder_path (str): The folder path of the data to synchronise.
    data_type (str): The data type of the frames to synchronise.
    raspi_name (str): The name of the raspberry pi object.
    frame_number (int): Frame number of ToAt metadata file.

    Return: (int) the extracted ToAt
    """   
    
    file_name = get_filename(folder_path, date_type, raspi_name, frame_number, True)
     
    if date_type == "depth":
        # Open file and get line 9 (ToAt is always on line 9 of metadata)
        with open(file_name) as fp:
            for i, line in enumerate(fp):
                if i == 8:
                    # Split line using comma
                    split = line.split(",")
                    
                    # The ToAt should be the second item in the list
                    return int(split[1])
    else:
        # Open file and get line 7 (ToAt is always on line 9 of metadata)
        with open(file_name) as fp:
            for i, line in enumerate(fp):
                if i == 6:
                    # Split line using comma
                    split = line.split(",")
                    
                    # The ToAt should be the second item in the list
                    return int(split[1])
       

def sync_data(threshold: int, folder_path: str, raspberry_pis: list, data_type: str) -> list:
    """
    Uses the Time of Arrival timestamps (ToAt) of the depth frame metadata to find
    closely-matching frames (when the difference in ToAt is within the given threshold).
    
    Args:
    threshold (int): The maximum ToAt allowed between frames.
    folder_path (str): The folder path of the data to synchronise.
    raspberry_pis (list): The list of raspberry pi objects.
    data_type (str): The data type of the frames to synchronise.
    
    Returns:
    list: A list of framesets of closely-matching frames.
    """
    
    # Get and store the current frame index for each raspberry pi
    curr_frame_index = []
    for raspi in raspberry_pis:
        curr_frame_index.append(0)
    
    # List to store the framesets
    all_framesets = []
        
    # Loop until just one camera has no more frames to match
    all_cameras_have_frames = True
    while all_cameras_have_frames:
        curr_frameset = []
        # Amongst the current frames, search for the one with the largest ToAt
        ref_ToAt = extract_ToAt_from_file(folder_path, data_type, raspberry_pis[0].get_raspi_name(), 
                                          raspberry_pis[0].get_frame_numbers(data_type)[curr_frame_index[0]])
        ref_raspi = 0
        for raspi in range(1, len(raspberry_pis)):
            curr_ToAt = extract_ToAt_from_file(folder_path, data_type, raspberry_pis[raspi].get_raspi_name(), 
                                               raspberry_pis[raspi].get_frame_numbers(data_type)[curr_frame_index[raspi]])
            if ref_ToAt < curr_ToAt:
                ref_ToAt = curr_ToAt
                ref_raspi = raspi
        
        # Search for a frameset, i.e. a group of closely-matching frames from each raspberry pi
        continue_search = True
        raspi = 0
        new_curr_frame_index = curr_frame_index.copy()
        while continue_search and raspi < len(raspberry_pis):
            # Do not search for matching frame within reference raspberry's frames
            if raspi == ref_raspi:
                continue
            else:
                # Search for matching frame
                for frame in range(curr_frame_index[raspi], raspberry_pis[raspi].get_total_num_frames(data_type)):
                    curr_ToAt = extract_ToAt_from_file(folder_path, data_type, raspberry_pis[raspi].get_raspi_name(), 
                                                       raspberry_pis[raspi].get_frame_numbers(data_type)[frame])
                    
                    if abs(curr_ToAt - ref_ToAt) < threshold:
                        curr_frameset.append(raspberry_pis[raspi].get_frame_numbers(data_type)[frame])
                        # Store this frame number index temporarily
                        new_curr_frame_index[raspi] = frame                        
                        # Found closely-matching frame, so terminate search
                        break
                    
                    # Check if the current ToAt is much bigger than the reference one or no more frames to match, terminate search if it is
                    elif curr_ToAt - ref_ToAt > threshold and frame == (raspberry_pis[raspi].get_total_num_frames(data_type) - 1):
                        continue_search = False
                        break
                        
                    else:
                        raspi += 1
                        
        # Save frameset if it is valid
        if len(curr_frameset) == len(raspberry_pis):
            all_framesets.append(curr_frameset)
            
            # Update current frame number indexes
            for i in range(0, len(raspberry_pis)):
                curr_frame_index[i] = new_curr_frame_index[i]
                
        else:
            # Increment the frame index of the reference raspberry pi
            curr_frame_index[ref_raspi] += 1
            
            # Increment the frame index of the  raspberry pi that ended the search (had no closely-matching frame)
            curr_frame_index[raspi] += 1
        
            # Determine if search should continue
            if curr_frame_index[ref_raspi] == raspberry_pis[ref_raspi].get_total_num_frames(data_type) \
            or curr_frame_index[raspi] == raspberry_pis[raspi].get_total_num_frames(data_type):
                all_cameras_have_frames = False
            
            


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
    
    
        
