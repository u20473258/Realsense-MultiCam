import cv2
import numpy as np
import csv

# Depth image relative path
relative_path = "net_rs_cam_capture/build/Depth_Images/depth_"
# Depth image to store
depth_image_number = 1001
# Depth image relative file path
depth_image_path = relative_path + str(depth_image_number) + ".csv"
# Store depth image dimensions/resolution
depth_image_width = 640
depth_image_height = 480
# Create the numpy array depth image
depth_image = np.empty((depth_image_height, depth_image_width), dtype=float)  
# Access the depth image .csv file and extract the data
with open(depth_image_path, newline='') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=",", quotechar='|')
    i = 0
    for row in spamreader:
        j = 0
        for depth in row:
            depth_image[i,j] = depth
            j += 1
        i += 1

# Apply a colour map to the depth image
depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)
# Show depth colour map
cv2.imshow(f"Depth Stream - Camera {depth_colormap}", depth_image)
# Save depth image
# depth_filename = f"depth_images/depth_frame_{frame_number}_cam{serial_number}.png"
# cv2.imwrite(depth_filename, depth_image)


