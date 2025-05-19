import numpy as np
import csv
import cv2
import os
import open3d as o3d
import numpy as np
from PIL import Image
import pandas as pd
import shutil

class processor:
    """
    Constructor.
    
    filepath -> (str) filepath of the uploads folder containing captured data from all raspis
    duration -> (int) how long in seconds was the capture
    depth_stream_config -> (dict) the streaming configuration setup for depth sensor
    colour_stream_config -> (dict) the streaming configuration setup for colour sensor
    raspberrys -> (list) raspi names used in system
    serial_numbers -> (dict) serial numbers of D455 cameras attached to each raspi, raspi name is the key to this dict
    processing_empty_crush -> (bool) are we doing processing for an empty crush?
    """
    def __init__(self, filepath, duration, depth_stream_config, colour_stream_config, raspberrys, serial_numbers, processing_empty_crush):
        self.data_filepath = filepath
        self.capture_duration = duration
        self.depth_stream_config = depth_stream_config
        self.colour_stream_config = colour_stream_config
        self.raspberrys = raspberrys
        self.serial_numbers = serial_numbers
        
        if processing_empty_crush:
            self.processing_data_filepath = "empty_crush_data/"
            
            # Create a separate folder for storing the output data from the processing
            if os.path.exists(f"empty_crush_data"):
                shutil.rmtree(f"empty_crush_data")
        
            # Creates new directories for the camera data       
            os.makedirs(f"empty_crush_data", exist_ok=True)
        else:
            self.processing_data_filepath = "processing_data/"
            
            # Create a separate folder for storing the output data from the processing
            if os.path.exists(f"processing_data"):
                shutil.rmtree(f"processing_data")
        
            # Creates new directories for the camera data       
            os.makedirs(f"processing_data", exist_ok=True)
            
        
    
    """
    Algorithm that counts the number of frames that were captured for a given raspi
    
    raspi -> (string) the RPi name
    is_depth_frames -> (bool) do you want to get the frame numbers of the depth frames?
    
    Return: (int) number of frames
    """
    def count_depth_frames(self, raspi, is_depth_frames):
        num_frames = 0
        
        # Store the filename to use when search directory
        filename = ""
        filename += raspi
        
        # Search for depth frames
        if is_depth_frames:
            filename += "_depth"
            
            # Get all the filenames in the directory and loop through them
            for root, dirs, files in os.walk(self.data_filepath):
                for file in files: 
                    # Count only the .csv files that match the filename 
                    if file.count(filename) != 0 and file.endswith('.csv'):
                        num_frames += 1
                        
        # Search for colour frames
        else:
            filename += "_colour"
            
            # Get all the filenames in the directory and loop through them
            for root, dirs, files in os.walk(self.data_filepath):
                for file in files: 
                    # Count only the .png files that match the filename 
                    if file.count(filename) != 0 and file.endswith('.png'):
                        num_frames += 1
                        
        return num_frames
    
    
    """
    Algorithm that gets the filenames i.e. the frame numbers for a given RPi for a given file type.
    
    raspi -> (string) the RPi name
    is_depth_frames -> (bool) do you want to get the frame numbers of the depth frames?
    num_frames -> (int) approximately how many frames have been captured
    
    Return: (list) frame numbers
    """
    def get_frame_numbers(self, raspi, is_depth_frames, num_frames) -> list:
        frame_numbers = []
        
        # Scan directory and get an iterator
        obj = os.scandir(self.data_filepath)
        
        # Loop through each file
        for file in obj:
            # Check if we have already gotten all depth frame numbers
            if len(frame_numbers) == num_frames:
                break
            
            # Check if the file is for the correct raspi and the file is not metadata
            if (file.name).find(raspi) != -1 and (file.name).find("metadata") == -1:
                # Check if the file is a colour image and if we are searching for colour images
                if (file.name).find("colour") != -1 and is_depth_frames == False:
                    # Split file names based on the _ separator
                    split1 = (file.name).split("_")
                    
                    # The 3rd item in the first split will be <frame-num>.png. Split again using . as separator
                    split2 = split1[2].split(".")
                    
                    frame_num = int(split2[0])
                    frame_numbers.append(frame_num)
                    
                # Check if the file is a depth image and if we are searching for depth images
                elif (file.name).find("depth") != -1 and is_depth_frames:
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
    
    
    """
    Function that gets the ToA timestamp from a given .txt filename.
    
    filename -> (str) the .txt to open and read from
    
    Return: (int) ToA timestamp
    """
    def get_ToA_from_file(self, filename, is_depth_frame):     
        if is_depth_frame:
            # Open file and get line 9 (ToA timestamp is always on line 9 of metadata)
            with open(filename) as fp:
                for i, line in enumerate(fp):
                    if i == 8:
                        # Split line using comma
                        split = line.split(",")
                        # The ToA timestamp should be the second item in the list
                        return int(split[1])
        else:
            # Open file and get line 7 (ToA timestamp is always on line 9 of metadata)
            with open(filename) as fp:
                for i, line in enumerate(fp):
                    if i == 6:
                        # Split line using comma
                        split = line.split(",")
                        # The ToA timestamp should be the second item in the list
                        return int(split[1])
    
    
    """
    Function that compiles the filename 
    
    raspi -> (str) the name of the RPi
    frame_number -> (str) actual frame number recorded during capture
    is_depth_frame -> (bool) do you want to get the file of a depth frame?
    is_metadata -> (bool) do you want to get the file of metadata?
    
    Return: (str) filename
    """
    def get_filename(self, raspi, frame_number, is_depth_frame, is_metadata):
        filename = ""
        filename += self.data_filepath   
        frame_number = str(frame_number) 
        
        if is_depth_frame:
            if is_metadata:
                filename = filename + raspi + "_depth_metadata_" + frame_number + ".txt"
            else:
                filename = filename + raspi + "_depth_" + frame_number + ".csv"
        else:
            if is_metadata:
                filename = filename + raspi + "_colour_metadata_" + frame_number + ".txt"
            else:
                filename = filename + raspi + "_colour_" + frame_number + ".png"
        
        return filename
    
    
    """
    Algorithm that finds a closely matched frameset.
    
    raspi_curr_frame_num -> (list) the current index to use for the raspi_frame_numbers for each raspi
    raspi_frame_numbers -> (list) the actual frame numbers captured for each raspi
    threshold -> (int) the maximum allowable difference in timestamps between frames of different RPis
    is_depth_frames -> (bool) do you want to get the frame numbers of the depth frames?
    
    Return: (list) frameset
    """
    # def get_frameset(self, raspi_curr_frame_num, raspi_frame_numbers, threshold, is_depth_frames):
    #     frame_set_index = raspi_curr_frame_num.copy()
        
    #     # Find the largest (most recent) ToA timestamp
    #     largest_ToA = self.get_ToA_from_file(self.get_filename(self.raspberrys[0], raspi_frame_numbers[0][raspi_curr_frame_num[0]], is_depth_frames, True))
    #     print(largest_ToA)
    #     reference_RPi = 0
    #     for i in range(1, len(self.raspberrys)):
    #         curr_ToA = self.get_ToA_from_file(self.get_filename(self.raspberrys[i], raspi_frame_numbers[i][raspi_curr_frame_num[i]], is_depth_frames, True))
    #         print(curr_ToA)
    #         if largest_ToA < curr_ToA:
    #             largest_ToA = curr_ToA
    #             reference_RPi = i
                
    #     print(reference_RPi)
                
    #     # Find the frame number of each RPi that is closely matched to the largest ToA timestamp
    #     for i in range(0, len(self.raspberrys)):
    #         # Avoid comparing reference Pi to itself
    #         if i == reference_RPi:
    #             continue
    #         else:
    #             # Find a closely matched ToA timestamp
    #             not_found_match = True
    #             while not_found_match:
    #                 # Check if reached the last frame for current RPi
    #                 if raspi_curr_frame_num[i]+j >= len(raspi_frame_numbers[i]) and raspi_curr_frame_num[reference_RPi] < len(raspi_frame_numbers[reference_RPi]):
    #                     # Add to reference RPi index
    #                     frame_set_index[reference_RPi] += 1
    #                     return frame_set_index
    #                 else:
    #                     curr_ToA = self.get_ToA_from_file(self.get_filename(self.raspberrys[i], raspi_frame_numbers[i][raspi_curr_frame_num[i]+j], is_depth_frames, True))
    #                     # If within threshold
    #                     if abs(curr_ToA - largest_ToA) < threshold:
    #                         not_found_match = False
    #                         frame_set_index[i] += j
    #                     else:
    #                         if curr_ToA - largest_ToA > threshold:
                                
    #                         j += 1 
                
    #             difference_above_threshold = True
    #             j = 0
    #             while difference_above_threshold:
    #                 # Check if we have reached the last frame for the RPi
    #                 if raspi_curr_frame_num[i]+j >= len(raspi_frame_numbers[i]):
    #                     # Set a flag to indicate no matched frames
    #                     for k in range(len(self.raspberrys)):
    #                         frame_set[k] = -1
    #                     # Break out of function
    #                     return frame_set
                    
    #                 else:
    #                     curr_ToA = self.get_ToA_from_file(self.get_filename(self.raspberrys[i], raspi_frame_numbers[i][raspi_curr_frame_num[i]+j], is_depth_frames, True))
    #                     if abs(curr_ToA - largest_ToA) < threshold:
    #                         difference_above_threshold = False
    #                         frame_set[i] += j
    #                     else:
    #                         j += 1 
        
    #     return frame_set
    
    
    """
    Algorithm that finds a closely matched frameset.
    
    raspi_curr_frame_num -> (list) the current index to use for the raspi_frame_numbers for each raspi
    raspi_frame_numbers -> (list) the actual frame numbers captured for each raspi
    threshold -> (int) the maximum allowable difference in timestamps between frames of different RPis
    is_depth_frames -> (bool) do you want to get the frame numbers of the depth frames?
    
    Return: (list) frameset
    """
    def find_a_frameset(self, raspi_curr_frame_num, raspi_frame_numbers, threshold, is_depth_frames, reference_ToAt, reference_RPi):
        frame_set = raspi_curr_frame_num.copy()
        
        # Find the frame number of each RPi that is closely matched to the largest ToA timestamp
        for i in range(0, len(self.raspberrys)):
            # Avoid comparing reference Pi to itself
            if i == reference_RPi:
                continue
            
            else:
                # Find a closely matched ToAt
                not_found_match = True
                j = 0
                while not_found_match:
                    # Check if reached the last frame for current RPi
                    if raspi_curr_frame_num[i]+j >= len(raspi_frame_numbers[i]):
                        for k in range(0, len(self.raspberrys)):
                            frame_set[k] = -1
                        return frame_set
                    else:
                        curr_ToAt = self.get_ToA_from_file(self.get_filename(self.raspberrys[i], raspi_frame_numbers[i][raspi_curr_frame_num[i]+j], is_depth_frames, True), is_depth_frames)
                        # If within threshold
                        if abs(curr_ToAt - reference_ToAt) < threshold:
                            not_found_match = False
                            frame_set[i] += j
                        else:
                            # Check if the current ToAt is much larger than the reference one (implies that there is no matching ToAt and we should stop checking)
                            if curr_ToAt - reference_ToAt > threshold:
                                for k in range(0, len(self.raspberrys)):
                                    frame_set[k] = -2
                                return frame_set
                            else:
                                j += 1 
                                
        return frame_set
                
        # # Find the frame number of each RPi that is closely matched to the largest ToA timestamp
        # for i in range(0, len(self.raspberrys)):
        #     # Avoid comparing reference Pi to itself
        #     if i == reference_RPi:
        #         continue
        #     else:
        #         # Find a closely matched ToA timestamp
        #         not_found_match = True
        #         while not_found_match:
        #             # Check if reached the last frame for current RPi
        #             if raspi_curr_frame_num[i]+j >= len(raspi_frame_numbers[i]) and raspi_curr_frame_num[reference_RPi] < len(raspi_frame_numbers[reference_RPi]):
        #                 # Add to reference RPi index
        #                 frame_set_index[reference_RPi] += 1
        #                 return frame_set_index
        #             else:
        #                 curr_ToA = self.get_ToA_from_file(self.get_filename(self.raspberrys[i], raspi_frame_numbers[i][raspi_curr_frame_num[i]+j], is_depth_frames, True))
        #                 # If within threshold
        #                 if abs(curr_ToA - largest_ToA) < threshold:
        #                     not_found_match = False
        #                     frame_set_index[i] += j
        #                 else:
        #                     if curr_ToA - largest_ToA > threshold:
                                
        #                     j += 1 
                
        #         difference_above_threshold = True
        #         j = 0
        #         while difference_above_threshold:
        #             # Check if we have reached the last frame for the RPi
        #             if raspi_curr_frame_num[i]+j >= len(raspi_frame_numbers[i]):
        #                 # Set a flag to indicate no matched frames
        #                 for k in range(len(self.raspberrys)):
        #                     frame_set[k] = -1
        #                 # Break out of function
        #                 return frame_set
                    
        #             else:
        #                 curr_ToA = self.get_ToA_from_file(self.get_filename(self.raspberrys[i], raspi_frame_numbers[i][raspi_curr_frame_num[i]+j], is_depth_frames, True))
        #                 if abs(curr_ToA - largest_ToA) < threshold:
        #                     difference_above_threshold = False
        #                     frame_set[i] += j
        #                 else:
        #                     j += 1 
        
        # return frame_set
    
    
    
    """
    Algorithm that performs software synchronisation of captured depth data. The algorithm uses the Time of Arrival (ToA)
    timestamp to determine which frames from the respective RPis are closely-matched. The output is a list of framesets.
    
    threshold -> (int) the maximum allowable difference in timestamps between frames of different RPis
    
    Return: (list) closely-matched framesets
    """
    def depth_software_sync(self, threshold):
        # Store the number of depth frames collected
        num_frames = []
        for i in self.raspberrys:
            num_frames.append(self.count_depth_frames(i, True))
                
        # Store the framesets
        framesets = []
        
        # Get frame numbers for all raspis
        raspi_frame_numbers = []
        j = 0
        for i in self.raspberrys:
            raspi_frame_numbers.append((self.get_frame_numbers(i, True, num_frames[j])))
            # Ensure list is sorted
            raspi_frame_numbers[j].sort()
            j += 1
                        
        # Store the index in raspi_frame_numbers of the current frame number for each RPi
        raspi_curr_frame_num = []
        for i in range(0, len(self.raspberrys)):
            raspi_curr_frame_num.append(0)
            
        # Loop through frames to find matching frameset
        not_done_matching = True
        while not_done_matching:
            # Get the RPi with the most recent frame (largest ToAt)
            reference_ToAt = self.get_ToA_from_file(self.get_filename(self.raspberrys[0], raspi_frame_numbers[0][raspi_curr_frame_num[0]], True, True), True)
            reference_RPi = 0
            
            for i in range(1, len(self.raspberrys)):
                current_ToAt = self.get_ToA_from_file(self.get_filename(self.raspberrys[i], raspi_frame_numbers[i][raspi_curr_frame_num[i]], True, True), True)
                
                if reference_ToAt < current_ToAt:
                    reference_ToAt = current_ToAt
                    reference_RPi = i
                    
            # Try find a frameset
            frameset_index = self.find_a_frameset(raspi_curr_frame_num, raspi_frame_numbers, threshold, True, reference_ToAt, reference_RPi)
            
            # Look for flags
            if frameset_index[0] == -1 or frameset_index[0] == -2 and raspi_curr_frame_num[reference_RPi] < len(raspi_frame_numbers[reference_RPi]):
                # Increment previous reference RPi frame number index if it is still smaller than 
                raspi_curr_frame_num[reference_RPi] += 1
            else:
                # Store frameset
                frameset = []
                for i in range(0, len(self.raspberrys)):
                    frameset.append(raspi_frame_numbers[i][frameset_index[i]])
                    
                framesets.append(frameset)
                # Increment frame numbers
                for i in range(0, len(self.raspberrys)):
                    raspi_curr_frame_num[i] += 1
                    
            # Check if exhausted all the frames of any RPi
            for i in range(0, len(self.raspberrys)):
                if raspi_curr_frame_num[i] >= num_frames[i]:
                    not_done_matching = False
                    
        return framesets
    
    
    """
    Algorithm that performs software synchronisation of captured coloured data. The algorithm uses the Time of Arrival (ToA)
    timestamp to determine which frames from the respective RPis are closely-matched to the given depth frameset. 
    The output is a list of framesets.
    
    threshold -> (int) the maximum allowable difference in timestamps between frames of different RPis
    depth_framesets -> (list) the framesets from the depth SW sync
    
    Return: (list) closely-matched framesets with the matching depth frameset's index appended
    """
    def colour_software_sync(self, threshold, depth_framesets):
        # Store the number of depth frames collected
        num_frames = self.capture_duration * self.depth_stream_config['fps']
        
        # Store the framesets
        colour_framesets = []
        
        # Get frame numbers for all raspis
        raspi_frame_numbers = []
        j = 0
        for i in self.raspberrys:
            raspi_frame_numbers.append((self.get_frame_numbers(i, False, num_frames)))
            # Ensure list is sorted
            raspi_frame_numbers[j].sort()
            j += 1
        
        # Loop through each frameset
        for depth_frameset in range(0, len(depth_framesets)):
            colour_frameset = []
            
            # For each depth frame in the frameset
            for depth_frame in range(0, len(depth_framesets[depth_frameset])):
                # Get the ToAt of the depth frame
                curr_depth_frame_ToAt = self.get_ToA_from_file(self.get_filename(self.raspberrys[depth_frame], depth_framesets[depth_frameset][depth_frame], True, True), True)
                
                # Loop through each colour frame for the current raspi
                for curr_colour_frame in raspi_frame_numbers[depth_frame]:
                    curr_colour_frame_ToAt = self.get_ToA_from_file(self.get_filename(self.raspberrys[depth_frame], curr_colour_frame, False, True), False)
                                        
                    if abs(curr_depth_frame_ToAt - curr_colour_frame_ToAt) < threshold:
                        colour_frameset.append(curr_colour_frame)
                        # No need to keep searching colour frames when we found a matching one
                        break
                        
                    # If the curr_colour_frame_ToAt is much larger than the (threshold + curr_depth_frame_ToAt) we want to break since there is no need
                    # to continue searching
                    if curr_colour_frame_ToAt > (threshold + curr_depth_frame_ToAt):
                        break
                    
            # Check if a matching colour frame was found for each depth frame in the depth framest
            if len(colour_frameset) == len(depth_framesets[depth_frameset]):
                colour_frameset.append(depth_frameset)
                colour_framesets.append(colour_frameset)
                # colour_framesets.append(depth_frameset)
                    
        return colour_framesets
        
        
    """
    Opens up a .csv file and returns it as a numpy array
    
    raspi_index -> (int) index of raspi name in self.raspberrys to convert
    depth_frame_number -> (int) frame number of depth frame to convert
    """
    def get_numpy_from_csv(self, raspi_index, depth_frame_number):
        # Store the depth image file path
        depth_image_path = self.data_filepath + self.raspberrys[raspi_index] + "_depth_" + str(depth_frame_number) + ".csv"
        
        # Create the numpy array depth image
        depth_image = np.empty((self.depth_stream_config['height'], self.depth_stream_config['width']), dtype=float)  
        # Access the depth image .csv file and extract the data
        with open(depth_image_path, newline='') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=",", quotechar='|')
            i = 0
            for row in spamreader:
                j = 0
                for depth in row:
                    if j != self.depth_stream_config['width']:
                        depth_image[i,j] = float(depth)
                        j += 1
                i += 1
                
        return depth_image
        
    
    """
    Opens up a .npy file and returns it as a numpy array
    
    raspi_index -> (int) index of raspi name in self.raspberrys to convert
    depth_frame_number -> (int) frame number of depth frame to convert
    """ 
    def get_numpy_from_npy(self, raspi_index, depth_frame_number):
        # Store the depth image file path
        depth_image_path = self.processing_data_filepath + self.raspberrys[raspi_index] + "_depth_" + str(depth_frame_number) + ".npy"
        
        return np.load(depth_image_path)
        
    """
    Copy frameset images to a separate folder: processing data.
    
    depth_frameset -> (list) frameset of depth frames to be used for registration
    colour_frameset -> (list) frameset of colour frames to be used for registration
    """    
    def separate_frameset_images(self, depth_frameset, colour_frameset):
        # For each depth frame
        i = 0
        for depth_frame_number in depth_frameset:
            # Open depth frame .csv
            depth_frame = self.get_numpy_from_csv(i, depth_frame_number)
            
            # Save depth frame
            depth_frame_path = self.processing_data_filepath + self.raspberrys[i] + "_depth_" + str(depth_frame_number) + ".npy"
            np.save(depth_frame_path, depth_frame)
            
            i += 1
            
            print("Raspi " + str(i) + " depth image " + str(depth_frame_number) + " copied.")
            
        # For each depth frame
        i = 0
        for colour_frame_number in colour_frameset:
            # Get colour frame .png name
            colour_frame_filename = str(self.get_filename(self.raspberrys[i], colour_frame_number, False, False))
            
            # New colour frame .png name
            new_colour_frame_destination = str(self.processing_data_filepath.split("/")[0])
            
            # Copy colour frame
            shutil.copy(colour_frame_filename, new_colour_frame_destination)
            
            i += 1
            
            if i == len(self.raspberrys):
                break
            
            print("Raspi " + str(i) + " colour image " + str(colour_frame_number) + " copied.")
        
        
    """
    Algorithm that rotates depth.csv and colour.png images.
    
    raspi_index -> (int) index of raspi name in self.raspberrys to convert
    frame_number -> (list) list of frame numbers of depth frames to convert
    is_depth_frames -> (bool) do you want to get the frame numbers of the depth frames?
    """
    def rotate_image(self, raspi_index, frame_number, is_depth_frames):
        if is_depth_frames:
            # Store the depth image file path
            depth_image_path = self.data_filepath + self.raspberrys[raspi_index] + "_depth_" + str(frame_number) + ".csv"
                        
            # Create the numpy array depth image
            depth_image = self.get_numpy_from_csv(raspi_index, frame_number)
            
            # Rotate the depth image
            rotated_depth_image = np.rot90(np.rot90(depth_image))
            
            # Save image in processed data
            rotated_depth_image_path = self.processing_data_filepath + self.raspberrys[raspi_index] + "_depth_" + str(frame_number) + ".npy"
            np.save(rotated_depth_image_path, rotated_depth_image)
            
            print("Raspi " + str(raspi_index) + " depth image rotated.")
        else:
            # Store the colour image file path
            colour_image_path = self.data_filepath + self.raspberrys[raspi_index] + "_colour_" + str(frame_number) + ".png"
            
            # Get the image
            colour_image = cv2.imread(colour_image_path)
            
            # Rotate the image
            rotated_colour_image = cv2.rotate(colour_image, cv2.ROTATE_180)
            
            # Save image in processed data
            rotated_colour_image_path = self.processing_data_filepath + self.raspberrys[raspi_index] + "_colour_" + str(frame_number) + ".png"
            cv2.imwrite(rotated_colour_image_path, rotated_colour_image)
            
            print("Raspi " + str(raspi_index) + " colour image rotated.")
    
    
    """
    Algorithm that does depth image distance cropping, i.e. any pixel beyond a certain distance is set to 0.0
    
    raspi_index -> (int) index of raspi name in self.raspberrys to convert
    depth_frame_number -> (int) frame number of depth frame to convert
    distance_threshold -> (float) maximum allowable distance in metres
    """
    def depth_distance_cropping(self, raspi_index, depth_frame_number, distance_threshold):
        # Get depth image
        depth_image = (self.get_numpy_from_npy(raspi_index, depth_frame_number)).astype(np.float32)
        
        # Find pixels beyond distance threshold and set them to 0.0
        for i in range(0, len(depth_image)):
            for j in range(0, len(depth_image[i])):
                if depth_image[i][j] >= distance_threshold:
                    # Set pixel to 0.0
                    depth_image[i][j] = 0.0
                    
        # Apply a colour map to the depth image
        depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=25.5), cv2.COLORMAP_JET)
        
        # Save depth image
        depth_filename = self.processing_data_filepath + self.raspberrys[raspi_index] + "_cropped_depth_image_" + str(depth_frame_number) + ".png"
        cv2.imwrite(depth_filename, depth_colormap)
        print("Raspi " + str(raspi_index) + " depth cropped image .pngs saved.")
        
        # Save image in processed data
        depth_cropped_image_path = self.processing_data_filepath + self.raspberrys[raspi_index] + "_depth_" + str(depth_frame_number) + ".npy"
        np.save(depth_cropped_image_path, depth_image)
        print("Raspi " + str(raspi_index) + " depth cropped image .npys saved.")
        
        
    """
    Algorithm that does depth barrier subtraction using images of an empty crush
    
    raspi_index -> (int) index of raspi name in self.raspberrys to convert
    depth_frame_number -> (int) frame number of depth frame to background subtract
    empty_depth_frame_number -> (int) frame number of empty depth frame to use for subtraction
    """
    def depth_barrier_subtraction(self, raspi_index, depth_frame_number, empty_depth_frame_number):
        # Get depth image
        depth_image = (self.get_numpy_from_npy(raspi_index, depth_frame_number)).astype(np.float32)
        
        # Get empty depth image
        # Store the depth image file path
        empty_depth_image_path = "empty_crush_data/" + self.raspberrys[raspi_index] + "_depth_" + str(empty_depth_frame_number) + ".npy"
        empty_depth_image = np.load(empty_depth_image_path).astype(np.float32)
        
        # Find pixels beyond distance threshold and set them to 0.0
        for i in range(0, len(depth_image)):
            for j in range(0, len(depth_image[i])):
                # Subtract pixel values
                depth_image[i][j] = depth_image[i][j] - empty_depth_image[i][j]
                    
        # Apply a colour map to the depth image
        depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=25.5), cv2.COLORMAP_JET)
        
        # Save depth image
        depth_filename = self.processing_data_filepath + self.raspberrys[raspi_index] + "_barrier_subtracted_depth_image_" + str(depth_frame_number) + ".png"
        cv2.imwrite(depth_filename, depth_colormap)
        print("Raspi " + str(raspi_index) + " depth barrier subtracted .pngs saved.")
        
        # Save image in processed data
        depth_cropped_image_path = self.processing_data_filepath + self.raspberrys[raspi_index] + "_depth_" + str(depth_frame_number) + ".npy"
        np.save(depth_cropped_image_path, depth_image)
        print("Raspi " + str(raspi_index) + " depth cropped image .npys saved.")
            
        
    """
    Algorithm that converts depth .csv files to colourised depth .png images using opencv.
    
    depth_frame_numbers -> (list) list of frame numbers of depth frames to convert
    """
    def convert_csv_to_depth(self, depth_frame_numbers):
        # For each raspberry pi
        for x in range(len(self.raspberrys)):
            depth_image_path = self.data_filepath + self.raspberrys[x] + "_depth_" + str(depth_frame_numbers[x]) + ".csv"
            
            # Create the numpy array depth image
            depth_image = np.empty((self.depth_stream_config['height'], self.depth_stream_config['width']), dtype=float)  
            
            # Access the depth image .csv file and extract the data
            with open(depth_image_path, newline='') as csvfile:
                spamreader = csv.reader(csvfile, delimiter=",", quotechar='|')
                i = 0
                for row in spamreader:
                    j = 0
                    for depth in row:
                        if j != self.depth_stream_config['width']:
                            depth_image[i,j] = float(depth)
                            j += 1
                    i += 1

            # Apply a colour map to the depth image
            depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=25.5), cv2.COLORMAP_JET)
            
            # Save depth image
            depth_filename = self.data_filepath + self.raspberrys[x] + "_depth_image_" + str(depth_frame_numbers[x]) + ".png"
            cv2.imwrite(depth_filename, depth_colormap)
        
    
    """
    Algorithm that converts a depth .csv file to a colourised depth .png images using opencv and saves it in
    self.data_filepath
    
    raspi_index -> (int) index of raspi name in self.raspberrys to convert
    depth_frame_number -> (int) frame number of depth frame to convert
    is_rotated -> (bool) if the original image needed rotation
    """
    def convert_single_csv_to_depth(self, raspi_index, depth_frame_number):
        depth_image = self.get_numpy_from_npy(raspi_index, depth_frame_number)
                
        # Apply a colour map to the depth image
        depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=25.5), cv2.COLORMAP_JET)
        
        # Save depth image
        depth_filename = self.processing_data_filepath + self.raspberrys[raspi_index] + "_depth_image_" + str(depth_frame_number) + ".png"
        cv2.imwrite(depth_filename, depth_colormap)
        print("Raspi " + str(raspi_index) + " depth image .pngs saved.")
        
        
    """
    # Loads the camera instrinsics for a specific camera from a .csv file
    # serial_number -> the serial number of the camera
    # return: fx, fy, ppx, ppy
    """
    def load_cam_intrinsics(self, raspi_index):
        # Get serial number
        serial_number = np.int64(self.serial_numbers[self.raspberrys[raspi_index]])
        
        # Open the frame_metadata csv
        df = pd.read_csv("camera_intrinsics.csv")
        
        # Search for the correct row
        row_num = 0
        while True:
            if df.loc[row_num, "serial_number"] == serial_number:
                break
            else:
                row_num += 1
                        
        return df.loc[row_num, "fx"], df.loc[row_num, "fy"], df.loc[row_num, "ppx"], df.loc[row_num, "ppy"]    
    
    
    """
    Algorithm that converts a depth .csv file to a point cloud and stores it in the same folder
    
    raspi_index -> (int) index of raspi name in self.raspberrys to convert
    depth_frame_number -> (int) frame number of depth frame to convert
    depth_scale -> (float) adjust according to the depth unit in your images (e.g., 1000 for mm to meters)
    depth_trunc -> (float) how much should the depth image be truncated
    is_rotated -> (bool) if the original image needed rotation
    """
    def convert_csv_to_pcd(self, raspi_index, depth_frame_number, depth_scale, depth_trunc):
        # Get depth image
        depth_image = (self.get_numpy_from_npy(raspi_index, depth_frame_number)).astype(np.float32)
                
        # Get instrinsic of camera
        fx, fy, ppx, ppy = self.load_cam_intrinsics(raspi_index)
        
        # Define intrinsic parameters for Open3D
        intrinsic = o3d.camera.PinholeCameraIntrinsic(self.depth_stream_config['height'], self.depth_stream_config['width'], fx, fy, ppx, ppy)
         
        # Create point cloud from depth image
        pcd = o3d.geometry.PointCloud.create_from_depth_image(o3d.geometry.Image(depth_image), 
                                                            intrinsic, depth_scale=depth_scale, 
                                                            depth_trunc=depth_trunc)
        
        # Save point cloud
        pcd_filename = self.processing_data_filepath + self.raspberrys[raspi_index] + "_pcd_" + str(depth_frame_number) + ".ply"
        o3d.io.write_point_cloud(pcd_filename, pcd)
        print("Point cloud .pcd saved.")
        
    
    """
    # Loads images from png file
    # raspi_index -> (int) index of raspi name in self.raspberrys to convert
    # depth_frame_number -> (int) frame number of depth frame to convert
    
    # return: point cloud
    """
    def load_point_cloud(self, raspi_index, depth_frame_number):
        # Load the .ply file
        pcd_file_path = self.processing_data_filepath + self.raspberrys[raspi_index] + f"_pcd_{depth_frame_number}.ply"
        pcd = o3d.io.read_point_cloud(pcd_file_path)
        
        # Check if the point cloud is loaded
        if not pcd.is_empty():
            return pcd
        else:
            print("Failed to load point cloud. Check the file path or format.")
            return None


    """
    # Downsamples point clouds to reduce computational costs, applies noise filtering and computers normals for robust alignment.
    
    # pcd -> (open3d.geometry.PointCloud) point cloud
    # voxel_size -> (float) size of voxel
    
    # return: (open3d.geometry.PointCloud) pre-processed point cloud
    """
    def preprocess_point_cloud(self, pcd, voxel_size):
        # Down sample point cloud
        pcd_down = pcd.voxel_down_sample(voxel_size)
        
        pcd_down.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=voxel_size * 2, max_nn=30))
        
        return pcd_down


    """
    # Performs fast global registration registration. Rough registration using a RANSAC-based algorithm.
    
    # source -> (open3d.geometry.PointCloud) point cloud to register
    # target -> stationary point cloud 
    
    # return: (np.ndarray) transformation matrix
    """
    def registration_with_fgr(self, source, target):
        # Define search radius for FPFH computation
        search_radius = 0.05
        search_param = o3d.geometry.KDTreeSearchParamRadius(radius=search_radius)
        
        # Get FPFh feature for each point cloud
        source_fpfh = o3d.pipelines.registration.compute_fpfh_feature(source, search_param)
        target_fpfh = o3d.pipelines.registration.compute_fpfh_feature(target, search_param)
        
        # Global registration
        result = o3d.pipelines.registration.registration_fgr_based_on_feature_matching(
            source, target, source_fpfh, target_fpfh)
        
        print("Registration with FGR complete.")
        
        return result.transformation


    """
    # Performs registration with ICP.
    
    # source -> (open3d.geometry.PointCloud) point cloud to register
    # target -> stationary point cloud 
    # voxel_size -> size of voxel
    
    # return: (np.ndarray) transformation matrix
    """
    def registration_with_icp(self, source, target, voxel_size):
        distance_threshold = voxel_size * 1.5
        source_down = source
        target_down = target
        
        # Global registration
        result = o3d.pipelines.registration.registration_icp(
            source_down, target_down, distance_threshold, 
            np.eye(4), o3d.pipelines.registration.TransformationEstimationPointToPlane())
        
        print("Registration with ICP complete.")
        
        return result.transformation


    """
    Algorithm that performs registration of the different camera views
    
    reference_raspi_index -> (int) index of raspi name in self.raspberrys to be used as the reference camera view
    depth_frameset -> (list) frameset of depth frames to be used for registration
    colour_frameset -> (list) frameset of colour frames to be used for registration
    
    returns (list) transformation matrix
    """
    def registration(self, reference_raspi_index, depth_frameset, colour_frameset):
        transforms = [
        np.eye(4),  # Camera 1 (identity, reference frame)
        np.array([[0.952304544001, 0.055685926827, 0.300025220655, -0.337908239954],
                [-0.046863706186, 0.998233224821, -0.036527002431, 0.026966347488],
                [-0.301529183527, 0.020724536604, 0.953231684883, 0.041012801797],
                [0.000000000000, 0.000000000000, 0.000000000000, 1.000000000000]])
        ]
        
        return transforms
    
    
    """
    Algorithm that performs reconstruction of the 3D image
    
    reference_raspi_index -> (int) index of raspi name in self.raspberrys to be used as the reference camera view
    depth_frameset -> (list) frameset of depth frames to be used for registration
    colour_frameset -> (list) frameset of colour frames to be used for registration
    transformation_matrices -> (list) holds the transformation matrices to be used to different camera views
    
    Saves the reconstruction in the processed data folder
    """
    def reconstruction(self, reference_raspi_index, depth_frameset, colour_frameset, transformation_matrices):
        # Define the combined point cloud
        pcd_combined = o3d.geometry.PointCloud()
        
        # Transform point clouds
        point_clouds = []
        i = 0
        for raspi in range(0, len(self.raspberrys)):
            # Load the .ply file
            point_cloud = self.load_point_cloud(raspi, depth_frameset[raspi])
            
            # Transform point cloud
            point_cloud.transform(transformation_matrices[i])
            i += 1
            
            # Store transformed point cloud
            point_clouds.append(point_cloud)
            pcd_combined += point_cloud
        
        # Visualize aligned point clouds
        o3d.visualization.draw_geometries(point_clouds)
        
        # Save the combined point cloud
        filename = self.processing_data_filepath + "combined_pcd.ply"
        o3d.io.write_point_cloud(filename, pcd_combined)
        print("Combined point cloud saved.")