from data_processing import processor



# Store the name of raspberry pi 5s
raspberrys = ["raspi1", "raspi2", "raspi3", "raspi4"]

# Serial number of D455 camera for each raspi
serial_numbers = {"raspi1" : "138322250306",
                "raspi2" : "138322252073",
                "raspi3" : "141322252627",
                "raspi4" : "141322250372",
                "raspi5" : "141322252882"}

# Depth capture configuration setup 
depth_capture_config = {'width' : 640,
                        'height' : 480,
                        'fps' : 15}

# Colour capture configuration setup 
colour_capture_config = {'width' : 640,
                        'height' : 480,
                        'fps' : 15}

# How long in seconds is the capture done for
capture_duration = 10 #s

processor_1 = processor("25_Mar_OP_1_uploads_five_10_15/", capture_duration, depth_capture_config, colour_capture_config, raspberrys)

# Convert some depth csv to png
# image_sets = []
# for i in raspberrys:
#     frame_number = input("What depth frame number should be used for " + i + "\t")
#     image_sets.append(int(frame_number))
# processor_1.convert_csv_to_depth(image_sets)

# Do SW syncing
print("Performing SW synchronisation now...")

threshold = 66 #ms
depth_framesets = processor_1.depth_software_sync(threshold)
print(depth_framesets)
print(len(depth_framesets))

colour_framesets = processor_1.colour_software_sync(threshold, depth_framesets)
print(colour_framesets)
print(len(colour_framesets))

frameset = int(input("Please select the index of the frameset to process further from the given SW colour framesets \t"))

# Convert the depth images in selected frameset to pngs
print("Converting depth image .csv files to .png images...")
for i in range(0, len(raspberrys)):
    processor_1.convert_single_csv_to_depth(i, depth_framesets[colour_framesets[frameset][len(raspberrys)]][i])
    
# Create point clouds from depth frames in selected frameset
print("Converting depth image .csv files to .ply point cloud files...")
depth_scale = 1000.0
depth_trunc = 1.5
for i in range(0, len(raspberrys)):
    processor_1.convert_csv_to_pcd(i, depth_framesets[colour_framesets[frameset][len(raspberrys)]][i], depth_scale, depth_trunc)
    
# Perform registration
print("Performing registration...")
reference_raspi = 0
transformations = processor_1.registration(reference_raspi, depth_framesets[colour_framesets[frameset][len(raspberrys)]], colour_framesets[frameset])

# Perform reconstruction
print("Performing reconstruction...")
reference_raspi = 0
# processor_1.reconstruction(reference_raspi, depth_framesets[colour_framesets[frameset][len(raspberrys)]], colour_framesets[frameset], transformations)