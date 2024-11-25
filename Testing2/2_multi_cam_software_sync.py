import pandas as pd
import numpy as np

# Loads the rgb and depth timestamp for a specific camera from a .csv file
# serial_number -> the serial number of the camera
# frame_number -> which frame or image number to use
# return: rgb_timestamp, depth_timestampm, prev_row_num
def get_timestamps(serial_number, frame_number, starting_row):
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
        return 10000, -10000
    
    return df.loc[row_num, "rgb_timestamp"], df.loc[row_num, "depth_timestamp"], row_num



# Store the serial numbers of the cameras used
serial_numbers = ["138322252073", "141322252882"]
# Store the previous row number for each serial number. This prevents the algorithm from searching
# through the entire .csv file
previous_row_num = {
    "138322252073" : 0,
    "141322252882" : 0
    # "138322252073" : 0,
    # "138322252073" : 0
}
# Total number of frames captured
total_frames = 690
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
    for i in range(1, total_frames+1):
        for j in range(len(serial_numbers)):
            rgb_timestamps[j], depth_timestamps[j], previous_row_num[serial_numbers[j]] = get_timestamps(np.int64(serial_numbers[j]), i, previous_row_num[serial_numbers[j]])
            
        # Test if difference between timestamps is below threshold
        if abs(rgb_timestamps[0] - rgb_timestamps[1]) < threshold and abs(depth_timestamps[0] - depth_timestamps[1]) < threshold:
            frame_set.append(i)
            
    print(frame_set)