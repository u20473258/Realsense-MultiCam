from data_processing import processor



# Store the name of raspberry pi 5s
raspberrys = ["raspi1", "raspi2", "raspi3", "raspi4", "raspi5"]
depth_capture_config = {'width' : 640,
                        'height' : 480,
                        'fps' : 15}
colour_capture_config = {'width' : 640,
                        'height' : 480,
                        'fps' : 15}

capture_duration = 5

processor_1 = processor("uploads/", capture_duration, depth_capture_config, colour_capture_config, raspberrys)

# Convert some depth csv to png
image_sets = []
for i in raspberrys:
    frame_number = input("What depth frame number should be used for " + i)
    image_sets.append(int(frame_number))
processor_1.convert_csv_to_depth(image_sets)

# Do SW syncing
framesets = processor_1.depth_software_sync(50)
print(framesets)