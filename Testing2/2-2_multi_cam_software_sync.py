import pandas as pd
import numpy as np

# Loads the rgb and depth timestamp for a specific camera from a .csv file. The search begins
# from a given starting_row.
# serial_number -> the serial number of the camera
# frame_number -> which frame or image number to use
# return: timestamp, prev_row_num
def get_timestamps(serial_number, frame_number, rgb_stamp, starting_row):
    # Open the frame_metadata csv
    df = pd.read_csv("frame_metadata.csv")
    # Search for the correct row
    row_num = starting_row
    # When the frame number has not been found yet
    frame_not_found = True
    while frame_not_found:
        if df.loc[row_num, "serial_number"] == serial_number:
            if df.loc[row_num, "frame_number"] == frame_number:
                frame_not_found = False
                break
            else:
                row_num += 1
        else:
            row_num += 1
    
    if frame_not_found:
        print("Frame not found")
        return -1
    
    if rgb_stamp == True:
        return df.loc[row_num, "rgb_timestamp"], row_num
    else:
        return df.loc[row_num, "depth_timestamp"], row_num



# Store the serial numbers of the cameras used
serial_numbers = ["141322252882", "138322250306"]
# Store the previous row number for each serial number. This prevents the algorithm from searching
# through the entire .csv file
previous_row_num = {
    "141322252882" : 0,
    "138322250306" : 0
    # "138322252073" : 0
}
# Total number of frames captured
total_frames = 568
# Frame numbers that meet the threshold
frame_set = []
# Threshold of maximum difference between timestamps
threshold = 5 #ms
# Store the current timestamps
rgb_timestamps = []
depth_timestamps = []
for i in range(len(serial_numbers)):
    rgb_timestamps.append(0)
    depth_timestamps.append(0)
# Indicate which timestamp to use for synchronisation
use_rgb_stamp = False
if __name__ == "__main__":
    # Store the serial numbers of the cameras used
    serial_numbers = ["141322252882", "138322250306"]
    # Store the previous row number for each serial number. This prevents the algorithm from searching
    # through the entire .csv file
    previous_row_num = {
        "141322252882" : 0,
        "138322250306" : 0
        # "138322252073" : 0
    }
    
    # Total number of frames captured
    total_frames = 568
    
    # Frame numbers that meet the threshold
    frame_sets = []
    
    # Threshold of maximum difference between timestamps
    threshold = 5 #ms
    
    # Store the current timestamps
    cam1_timestamp = 0
    camn_timestamp = 0
    
    # Indicate which timestamp to use for synchronisation: True -> RGB and False -> Depth.
    use_rgb_stamp = False
    
    # Keep track of if no timestamp was found for the current camera
    matching_timestamp_found = True
    
    # For each of cam 1's timestamps
    for i in range(1, total_frames+1):
        # Store the current cam1 timestamp
        cam1_timestamp, previous_row_num[serial_numbers[0]] = get_timestamps(np.int64(serial_numbers[0]), i, use_rgb_stamp, previous_row_num[serial_numbers[0]])
        
        # Store the current frame set
        frame_set = [i]
        
        # Reset to true
        matching_timestamp_found = True
        
        # For each of cam n excluding cam 1.
        for j in range(1, len(serial_numbers)):
            # Does cam n have a timestamp that closely matches cam1's ith timestamp?
            for k in range(1, total_frames+1):
                # Get the current camn timestamp
                camn_timestamp, previous_row_num[serial_numbers[j]] = get_timestamps(np.int64(serial_numbers[j]), i, use_rgb_stamp, previous_row_num[serial_numbers[j]])
                
                # Test if difference between timestamps is below threshold
                if abs(cam1_timestamp - camn_timestamp) < threshold:
                    frame_set.append(k)
                    
                    # No need to keep on looking for a match in the current camera.
                    previous_row_num[serial_numbers[j]]
                    break
                
                # Check if this is the last of cam n's frames
                if k == total_frames:
                    matching_timestamp_found = False
                
            # Reset the previous row number for cam n
            previous_row_num[serial_numbers[j]]
                    
            # If there is no matching timestamp for the current camera
            if matching_timestamp_found == False:
                # No need to keep looking for a closely matching timestamp in other cameras
                break
            
        # Check if there is a matching timestamp found for each camera
        if matching_timestamp_found == False:
            # Store the frameset
            frame_sets.append(frame_set)
            
    print(frame_sets)