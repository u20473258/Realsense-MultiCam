import numpy as np
import csv
import cv2

class processor:
    """filepath -> (str) filepath of the uploads folder containing captured data from all raspis
       duration -> (int) how long in seconds was the capture
       depth_stream_config -> (dict) the streaming configuration setup for depth sensor
       colour_stream_config -> (dict) the streaming configuration setup for colour sensor
       raspberrys -> (list) raspi names used in system"""
    def __init__(self, filepath, duration, depth_stream_config, colour_stream_config, raspberrys):
        self.data_filepath = filepath
        self.capture_duration = duration
        self.depth_stream_config = depth_stream_config
        self.colour_stream_config = colour_stream_config
        self.raspberrys = raspberrys
        
    def software_sync(self):
        print("Performing software synchronisation. Output is series of closely-matched framesets.")
        
        
    """Algorithm that converts depth .csv files to colourised depth .png images using opencv"""
    def convert_csv_to_depth(self):
        image_sets = []
        for i in self.raspberrys:
            frame_number = input("What depth frame number should be used for " + i)
            image_sets.append(int(frame_number))
        
        # For each raspberry pi
        for x in range(len(self.raspberrys)):
            depth_image_path = self.data_filepath + self.raspberrys[x] + "_depth_" + str(image_sets[x]) + ".csv"
            
            # Create the numpy array depth image
            depth_image = np.empty((self.depth_stream_config['height'], self.depth_stream_config['width']), dtype=float)  
            # Access the depth image .csv file and extract the data
            with open(depth_image_path, newline='') as csvfile:
                spamreader = csv.reader(csvfile, delimiter=",", quotechar='|')
                i = 0
                for row in spamreader:
                    j = 0
                    for depth in row:
                        if j != 640:
                            depth_image[i,j] = float(depth)
                            j += 1
                    i += 1

            # Apply a colour map to the depth image
            depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=25.5), cv2.COLORMAP_JET)
            
            # Save depth image
            depth_filename = self.data_filepath + self.raspberrys[x] + "_depth_image_" + str(image_sets[x]) + ".png"
            cv2.imwrite(depth_filename, depth_colormap)
        
        