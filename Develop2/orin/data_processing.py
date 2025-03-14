

class processor:
    def __init__(self, filename, duration, fps):
        self.data_filename = filename
        self.capture_duration = duration
        self.capture_fps = fps
        
    def software_sync(self):
        print("Performing software synchronisation. Output is series of closely-matched framesets.")
        
        