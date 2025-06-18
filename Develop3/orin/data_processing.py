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
import copy

class raspberry_pi:
    """
    Class of raspberry pi objects. Each raspberry pi has a camera attached to it.
    """
    
    def __init__(self, raspi_name: str, serial_number: int, folder_path: str):
        """
        Constructor.
        
        Parameters
        ----------
        raspi_name : str
            The name of the rasbperry pi object represents.
        serial_number : int
            The serial number of the attached D455 camera.
        folder_path : str
            The folder path containing data collected.
        
        Returns
        ----------
        RPi : raspberry_pi
            A raspberry_pi object.
        """
        
        self.raspi_name = raspi_name
        self.serial_number = serial_number
        self.folder_path = folder_path
        
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
        Loads the camera instrinsics from a .txt file.
        
        Returns
        ----------
        intrinsics : list
            A list of the D455 intrinsics connected to the give RPi (fx, fy, ppx, ppy).
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
        
        Parameters
        ----------
        data_type : str
            The data type of the frames to count.
        
        Returns
        ----------
        total_num_frames : int
            Total number of frames for collected by the raspberry pi.
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
        
        Parameters
        ----------
        data_type : str
            The data type of the frame numbers to extract.
        
        Returns
        ----------
        frame_numbers : list
            A list of the frame numbers for the raspberry pi.
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
        
        # Sort frame numbers
        frame_numbers.sort()
        
        return frame_numbers


def create_raspberry_pi(raspi: str, folder_path: str) -> raspberry_pi:
    """
    Creates a new raspberry pi object.
    
    Parameters
    ----------
    raspi : str
        The name of the raspberry pi.
    folder_path : str
        The folder path of the captured data.
    
    Returns
    ----------
    raspi : raspberry_pi
        A new raspberry_pi object.
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
    
    Parameters
    ----------
    folder_path : str
        Folder path of the captured data.
    data_type : str
        Data type of the file: colour or depth.
    raspi_name : str
        Name of the raspberry pi object.
    frame_number : int
        Frame number of file.
    is_metadata : bool 
        Indicate if the file being extracted is metadata.
    
    Returns
    ----------
    framesets : list
        A list of framesets of closely-matching frames.
    """
    
    filename = ""
    filename += folder_path  
    frame_num = str(frame_number) 
    
    if date_type == "depth":
        if is_metadata:
            filename = filename + raspi_name + "_depth_metadata_" + frame_num + ".txt"
        else:
            filename = filename + raspi_name + "_depth_" + frame_num + ".csv"
    else:
        if is_metadata:
            filename = filename + raspi_name + "_colour_metadata_" + frame_num + ".txt"
        else:
            filename = filename + raspi_name + "_colour_" + frame_num + ".png"
    
    return filename


def extract_ToAt_from_file(folder_path: str, date_type: str, raspi_name: str, frame_number: int) -> int: 
    """
    Gets the Time of Arrival timestamp (ToAt) from a metadata file with the given .txt filename.

    Parameters
    ----------
    folder_path : str
        Folder path of the captured data.
    data_type : str
        Data type of the frames to synchronise.
    raspi_name : str
        Name of the raspberry pi object.
    frame_number : int
        Frame number of ToAt metadata file.
    
    Returns
    ----------
    ToAt : int
        Extracted ToAt.
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
       
    return -1

def sync_data(threshold: int, folder_path: str, raspberry_pis: list, data_type: str) -> list:
    """
    Uses the Time of Arrival timestamps (ToAt) of the depth frame metadata to find
    closely-matching frames (when the difference in ToAt is within the given threshold).
    
    Parameters
    ----------
    threshold : int
        The maximum ToAt allowed between frames.
    folder_path : str
        The folder path of the data to synchronise.
    raspberry_pis : list
        The list of raspberry pi objects.
    data_type : str
        The data type of the frames to synchronise.
    
    Returns
    ----------
    framesets : list
        A list of framesets of closely-matching frames.
    """
    
    # Get and store the current frame index for each raspberry pi
    curr_frame_index = []
    for raspi in raspberry_pis:
        curr_frame_index.append(0)
    
    # List to store the framesets
    all_framesets = []
        
    # Loop until just one camera has no more frames to match
    all_cameras_have_frames = True
    # print(raspberry_pis[0].get_frame_numbers(data_type))
    # print(raspberry_pis[1].get_frame_numbers(data_type))
    while all_cameras_have_frames:
    # for i in range(0, 20):
        curr_frameset = copy.deepcopy(curr_frame_index)
        # Amongst the current frames, search for the one with the largest ToAt (most recent frame)
        ref_ToAt = extract_ToAt_from_file(folder_path, data_type, raspberry_pis[0].get_raspi_name(), 
                                          raspberry_pis[0].get_frame_numbers(data_type)[curr_frame_index[0]])
        ref_raspi = 0
        for raspi in range(1, len(raspberry_pis)):
            curr_ToAt = extract_ToAt_from_file(folder_path, data_type, raspberry_pis[raspi].get_raspi_name(), 
                                               raspberry_pis[raspi].get_frame_numbers(data_type)[curr_frame_index[raspi]])
            if ref_ToAt < curr_ToAt:
                ref_ToAt = curr_ToAt
                ref_raspi = raspi
                
        # Store the reference raspberry pi's frame number in the current frameset
        curr_frameset[ref_raspi] = raspberry_pis[ref_raspi].get_frame_numbers(data_type)[curr_frame_index[ref_raspi]]
        
        # Search for a frameset, i.e. a group of closely-matching frames from each raspberry pi
        continue_search = True
        matching_frame_counter = 0
        raspi = 0
        new_curr_frame_index = copy.deepcopy(curr_frame_index)
        # print("Ref " + str(raspberry_pis[ref_raspi].get_frame_numbers(data_type)[curr_frame_index[ref_raspi]]) + ": " + raspberry_pis[ref_raspi].get_raspi_name() + " -> " + str(ref_ToAt))
        while continue_search and raspi < len(raspberry_pis):
            # Do not search for matching frame within reference raspberry's frames
            if raspi != ref_raspi:
                # Search for matching frame
                for frame in range(curr_frame_index[raspi], raspberry_pis[raspi].get_total_num_frames(data_type)):
                    curr_ToAt = extract_ToAt_from_file(folder_path, data_type, raspberry_pis[raspi].get_raspi_name(), 
                                                       raspberry_pis[raspi].get_frame_numbers(data_type)[frame])
                    
                    # print(raspberry_pis[raspi].get_raspi_name() + " " + str(raspberry_pis[raspi].get_frame_numbers(data_type)[curr_frame_index[raspi]]) + ": " + str(curr_ToAt))
                    if abs(curr_ToAt - ref_ToAt) < threshold:
                        # print("Valid Frame: " + raspberry_pis[raspi].get_raspi_name() + " " + str(raspberry_pis[raspi].get_frame_numbers(data_type)[curr_frame_index[raspi]]) + ": " + str(curr_ToAt))
                        curr_frameset[raspi] = raspberry_pis[raspi].get_frame_numbers(data_type)[frame]
                        
                         # Store this frame number index temporarily
                        new_curr_frame_index[raspi] = frame + 1
                        
                        matching_frame_counter += 1
                         
                        # Found closely-matching frame, so terminate search
                        break
                    
                    # Check if the current ToAt is much bigger than the reference one or no more frames to match, terminate search if it is
                    elif curr_ToAt > ref_ToAt or frame >= (raspberry_pis[raspi].get_total_num_frames(data_type) - 1):
                        continue_search = False
                        # # Increment the frame index of the raspberry pi that ended the search
                        # curr_frame_index[raspi] += 1
                        break
            
            raspi += 1
                        
        # Save frameset if it is valid
        if matching_frame_counter == (len(raspberry_pis) - 1):
            # print("Valid Frameset")
            all_framesets.append(curr_frameset)
            
            # Update current frame number indexes
            curr_frame_index = copy.deepcopy(new_curr_frame_index)
            curr_frame_index[ref_raspi] += 1
                
        else:
            # # Increment the frame index of the reference raspberry pi
            # curr_frame_index[ref_raspi] += 1
            
            # Increment all current frame indexes
            for raspi in range(0, len(raspberry_pis)):
                curr_frame_index[raspi] += 1

        # Check if any raspberry pi has no frames to search
        for raspi in range(0, len(raspberry_pis)):
            if curr_frame_index[raspi] >= raspberry_pis[raspi].get_total_num_frames(data_type):
                all_cameras_have_frames = False
            
    return all_framesets    

   
def extract_working_data(folder_path: str, raspberry_pis: list, depth_frameset: list, depth_info: dict, 
                         colour_frameset: list, colour_info: dict, delete_other_files: bool) -> str:
    """
    Separates the given framesets' files into a separate folder and if delete_other_files is True, deletes
    unused data to conserve storage.
    
    Parameters
    ----------
    folder_path : str
        The folder path of the captured data.
    raspberry_pis : list
        The list of raspberry pi objects.
    depth_frameset : list
        Frameset of depth frames to be used.
    depth_info : dict
        Hold information about the depth frame, e.g. dimensions.
    colour_frameset : list
        Frameset of colour frames to be used.
    delete_other_files : bool
        Informs function whether to delete remaining files.
    
    Returns
    ----------
    filepath : str
        The file path of the folder containing working data.
    """
 
    # Create new folder for files to process
    working_data_filepath = "working_data" 
    if os.path.exists(working_data_filepath):
        shutil.rmtree(working_data_filepath)
    os.makedirs(working_data_filepath, exist_ok=True)
    working_data_filepath += "/"
    
    # For each depth frame
    i = 0
    for depth_frame_number in depth_frameset:
        # Create the file paths for the depth frame
        old_depth_frame_filepath = get_filename(folder_path, "depth", raspberry_pis[i].get_raspi_name(), depth_frame_number, False)
        new_depth_frame_filepath = get_filename(working_data_filepath, "depth", raspberry_pis[i].get_raspi_name(), depth_frame_number, False)
        
        # Move depth frame to new folder        
        shutil.move(old_depth_frame_filepath, new_depth_frame_filepath)
        
        # Create the file paths for the depth frame metadata
        old_depth_frame_filepath = get_filename(folder_path, "depth", raspberry_pis[i].get_raspi_name(), depth_frame_number, True)
        new_depth_frame_filepath = get_filename(working_data_filepath, "depth", raspberry_pis[i].get_raspi_name(), depth_frame_number, True)
        
        # Move depth frame to new folder        
        shutil.move(old_depth_frame_filepath, new_depth_frame_filepath)
        
        i += 1
        
        print("Raspi " + str(i) + " depth image " + str(depth_frame_number) + " copied.")
        
    # For each colour frame
    i = 0
    for colour_frame_number in colour_frameset:
        # Create the file paths for the colour frame
        old_colour_frame_filepath = get_filename(folder_path, "colour", raspberry_pis[i].get_raspi_name(), colour_frame_number, False)
        new_colour_frame_filepath = get_filename(working_data_filepath, "colour", raspberry_pis[i].get_raspi_name(), colour_frame_number, False)
        
        # Move colour frame to new folder        
        shutil.move(old_colour_frame_filepath, new_colour_frame_filepath)
        
        # Create the file paths for the colour frame metadata
        old_colour_frame_filepath = get_filename(folder_path, "colour", raspberry_pis[i].get_raspi_name(), colour_frame_number, True)
        new_colour_frame_filepath = get_filename(working_data_filepath, "colour", raspberry_pis[i].get_raspi_name(), colour_frame_number, True)
        
        # Move colour frame to new folder        
        shutil.move(old_colour_frame_filepath, new_colour_frame_filepath)
        
        i += 1
        
        print("Raspi " + str(i) + " colour image " + str(colour_frame_number) + " copied.")
        
    # Delete folder
    if delete_other_files:
        shutil.rmtree(folder_path)
    
    return working_data_filepath


def create_depthmap(filepath: str, depth_info: dict, min_depth: int, max_depth: int) -> str:
    """
    Converts the given binary depth file to a depth map .png file.
    
    Parameters
    ----------
    filepath : str
        The folder path of the captured data.
    depth_info : dict
        Hold information about the depth frame, e.g. dimensions.
    min_depth : int
        Minimum depth value to include in depth map.
    max_depth : int
        Minimum depth value to include in depth map.
    
    Returns
    ----------
    filepath : str
        The file path of the depthmap.
    """
    
    depth_array = np.fromfile(filepath, dtype=np.uint16).reshape((depth_info['height'], depth_info['width']))
    
    # Clip the values for visualization
    depth_clipped = np.clip(depth_array, min_depth, max_depth)

    # Normalize to 0–255 (8-bit) for colormap
    depth_normalized = ((depth_clipped - min_depth) / (max_depth - min_depth) * 255.0).astype(np.uint8)

    # Apply colormap
    heatmap = cv2.applyColorMap(depth_normalized, cv2.COLORMAP_JET)
    
    # Save depth image as .png
    depth_filename = filepath[ : len(filepath)- 3] + "png"
    # cv2.imwrite(depth_filename, depth_colormap)
    cv2.imwrite(depth_filename, heatmap)
    
    print(depth_filename + " depth image .pngs saved.")
    
    return depth_filename
            

def main():
    # Get user input
    parser=argparse.ArgumentParser(description="process data")
    parser.add_argument("folder_path")
    parser.add_argument("raspberry_pis", nargs="*", type=str, default=["raspi1"],)
    parser.add_argument("sync_threshold")
    parser.add_argument("delete_unsynced", choices=['Y', 'y', 'N', 'n'])
    args=parser.parse_args()
    
    folder_path = args.folder_path + "/"
    
    # Create raspberry pi objects
    raspis = []
    for raspi in args.raspberry_pis:
        raspis.append(create_raspberry_pi(raspi, folder_path))
                
    # Sync depth data
    depth_framesets = sync_data(int(args.sync_threshold), folder_path, raspis, "depth")
    print(depth_framesets)
    print(len(depth_framesets))
    
    depth_info = {'height' : 240,
                  'width' : 428}
    
    # Sync colour data
    colour_framesets = sync_data(int(args.sync_threshold), folder_path, raspis, "colour")
    print(colour_framesets)
    print(len(colour_framesets))
    
    colour_info = {'height' : 480,
                  'width' : 640}
    
    # Separate processing data
    if args.delete_unsynced == 'Y' or args.delete_unsynced == 'y':
        working_data_folderpath = extract_working_data(folder_path, raspis, depth_framesets[0], depth_info, colour_framesets[0], colour_info, True)
    
    else:
        working_data_folderpath = extract_working_data(folder_path, raspis, depth_framesets[0], depth_info, colour_framesets[0], colour_info, False)
    
    i = 0
    for raspi in raspis:
        binary_depth_filename = get_filename(working_data_folderpath, "depth", raspi.get_raspi_name(), depth_framesets[0][i], False)
        png_depth_filename = create_depthmap(binary_depth_filename, depth_info, 300, 3000)
        
        print("Saved: " + png_depth_filename)
        i += 1
    
    
    # Rotate images
    
    # Depth croppping
    
    # Background subtraction
    
    

if __name__ == "__main__":
    main()
    
