import numpy as np
import csv
import cv2
import os

class processor:
    """
    Constructor.
    
    filepath -> (str) filepath of the uploads folder containing captured data from all raspis
    duration -> (int) how long in seconds was the capture
    depth_stream_config -> (dict) the streaming configuration setup for depth sensor
    colour_stream_config -> (dict) the streaming configuration setup for colour sensor
    raspberrys -> (list) raspi names used in system
    """
    def __init__(self, filepath, duration, depth_stream_config, colour_stream_config, raspberrys):
        self.data_filepath = filepath
        self.capture_duration = duration
        self.depth_stream_config = depth_stream_config
        self.colour_stream_config = colour_stream_config
        self.raspberrys = raspberrys
        
    
    """
    Algorithm that gets the filenames i.e. the frame numbers for a given RPi for a given file type.
    
    raspi -> (string) the RPi name
    is_depth_frames -> (bool) do you want to get the frame numbers of the depth frames?
    num_frames -> (int) approximately how many frames have been captured
    
    Return: (list) frame numbers
    """
    def get_frame_numbers(self, raspi, is_depth_frames, num_frames):
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
    def get_ToA_from_file(self, filename):        
        # Open file and get line 9 (ToA timestamp is always on line 9 of metadata)
        with open(filename) as fp:
            for i, line in enumerate(fp):
                if i == 8:
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
        filename = "uploads/"    
        
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
    def get_frameset(self, raspi_curr_frame_num, raspi_frame_numbers, threshold, is_depth_frames):
        frame_set = raspi_curr_frame_num.copy()
        
        # Find the largest (most recent) ToA timestamp
        largest_ToA = self.get_ToA_from_file(self.get_filename(self.raspberrys[0], raspi_frame_numbers[0][raspi_curr_frame_num[0]], is_depth_frames, True))
        reference_RPi = 0
        for i in range(1, len(self.raspberrys)):
            curr_ToA = self.get_ToA_from_file(self.get_filename(self.raspberrys[i], raspi_frame_numbers[i][raspi_curr_frame_num[i]], is_depth_frames, True))
            if largest_ToA < curr_ToA:
                largest_ToA = curr_ToA
                reference_RPi = i
                
        # Find the frame number of each RPi that is closely matched to the largest ToA timestamp
        for i in range(0, len(self.raspberrys)):
            # Avoid comparing reference Pi to itself
            if i == reference_RPi:
                continue
            else:
                difference_above_threshold = True
                j = 0
                while difference_above_threshold:
                    # Check if we have reached the last frame for the RPi
                    if raspi_curr_frame_num[i]+j >= len(raspi_frame_numbers[i]):
                        # Set a flag to indicate no matched frames
                        for k in range(len(self.raspberrys)):
                            frame_set[k] = -1
                        # Break out of function
                        return frame_set
                    
                    else:
                        curr_ToA = self.get_ToA_from_file(self.get_filename(self.raspberrys[i], raspi_frame_numbers[i][raspi_curr_frame_num[i]+j], is_depth_frames, True))
                        if abs(curr_ToA - largest_ToA) < threshold:
                            difference_above_threshold = False
                            frame_set[i] = frame_set[i]+j
                        else:
                            j += 1 
        
        return frame_set
    
    
    """
    Algorithm that performs software synchronisation of captured depth data. The algorithm uses the Time of Arrival (ToA)
    timestamp to determine which frames from the respective RPis are closely-matched. The output is a list of framesets.
    
    threshold -> (int) the maximum allowable difference in timestamps between frames of different RPis
    first_depth_frames
    
    Return: (list) closely-matched framesets
    """
    def depth_software_sync(self, threshold, first_depth_frames):
        print("Performing software synchronisation. Output is series of closely-matched framesets.")
        # Store the number of depth frames collected
        num_frames = self.capture_duration * self.depth_stream_config['fps']
        
        # Store the framesets
        framesets = []
        
        # Get frame numbers for all raspis
        raspi_frame_numbers = []
        for i in self.raspberrys:
            raspi_frame_numbers.append(self.get_frame_numbers(i, True, num_frames))
            
        # Store the current frame numbers for each RPi
        raspi_curr_frame_num = []
        for i in range(0, len(self.raspberrys)):
            raspi_curr_frame_num.append(raspi_frame_numbers[i][0])
        
        # Loop through frames
        still_matching_frames = True
        while not(still_matching_frames):
            curr_frameset = self.get_frameset(raspi_curr_frame_num, raspi_frame_numbers, threshold, True)
            
            # Check for the end of frames flag
            if curr_frameset[0] == -1:
                still_matching_frames = False
            else:
                framesets.append(curr_frameset.copy())
                for i in range(0, len(self.raspberrys)):
                    raspi_curr_frame_num = curr_frameset[i] + 1
        
        return framesets
        
        
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
        
        