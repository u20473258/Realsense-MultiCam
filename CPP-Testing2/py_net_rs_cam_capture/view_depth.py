import cv2
import numpy as np
import csv

# Depth image relative path
relative_path = "/home/orin/Desktop/Realsense-MultiCam/CPP-Testing2/net_rs_cam_capture/build/Depth_Images/depth_"
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
            if j != 640:
                depth_image[i,j] = float(depth)
                j += 1
        i += 1

# Apply a colour map to the depth image
depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=25.5), cv2.COLORMAP_JET)
print(type(depth_colormap))
# Show depth colour map
cv2.imshow(f"Depth Image", depth_colormap)
# Save depth image
depth_filename = f"depth_image_{depth_image_number}.png"
cv2.imwrite(depth_filename, depth_colormap)


