import pyrealsense2 as rs
import numpy as np
import datetime as dt
import time
import multiprocessing as mp
import os
#import mpio
import cv2
from queue import Queue
import threading as th


class RecordingJob(th.Thread):

    def __init__(self, video_name, queue):
        super(RecordingJob, self).__init__()
        self.stop_flag = th.Event()
        self.stop_flag.set()
        self.video_name = video_name
        self.queue = queue

    def run(self):
        self.num = 0
        self.fourcc = cv2.VideoWriter_fourcc(*'XVID')
        self.out = cv2.VideoWriter(self.video_name, self.fourcc, 60, (640, 480))
        while self.stop_flag.isSet():
            #print(self.queue.qsize())
            #self.num += 1
            if not self.queue.empty():
                self.out.write(self.queue.get())
                #self.queue.get()
                self.num += 1
        time.sleep(1)
        print(self.num)
        #print(self.queue.qsize())
        self.out.release()
        print('Thread Exitted')

    def stop(self):
        self.stop_flag.clear()


if __name__ == '__main__':


    directory_path = '0702test'
    if not os.path.exists(directory_path):
        os.mkdir(directory_path)

    rgb_video_name = directory_path+'/rgb.avi'
    f = open(directory_path+'/time.txt','w')
    #rgb_queue = mp.Queue()
    rgb_queue = Queue()

    #p = mpio.RGBRecordingClass(rgb_video_name, rgb_queue)
    #p.start()
    t = RecordingJob(rgb_video_name, rgb_queue)
    t.start()

    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 60)

    profile = pipeline.start(config)
    frame_count = 0
    sensors = profile.get_device().query_sensors()

    #print('Sensors are '+str(sensors))

    for sensor in sensors:
        if sensor.supports(rs.option.auto_exposure_priority):
            #print('Start setting AE priority.')
            aep = sensor.get_option(rs.option.auto_exposure_priority)
            print('Original AEP = %d' %aep)
            aep = sensor.set_option(rs.option.auto_exposure_priority, 0)
            aep = sensor.get_option(rs.option.auto_exposure_priority)
            print('New AEP = %d' %aep)

    try:
        print('Start Recording %s' %(str(dt.datetime.now())))
        date_start = time.time()

        while True:
            frames = pipeline.wait_for_frames()


            color_frame = frames.get_color_frame()
            f.write(str(time.time()*1000)+'\n')
            if not color_frame:
                print('No color frame')


            color_image = color_frame.get_data()
            color_image = np.asanyarray(color_image)
            '''
            cv2.imshow('frame', color_image)
            cv2.waitKey(1)
            '''
            
            rgb_queue.put(color_image)

            frame_count += 1



            total_elapsed = time.time()-date_start
            print('Frame num: %d, fps: %d' %(frame_count, frame_count/total_elapsed))

            if frame_count >= 18000:

                break

    except Exception as e:
        print('Error is ', str(e))
    finally:
        print(str(dt.datetime.now()))
        pipeline.stop()
        print('frame_count=',str(frame_count))
        #p.stop()
        t.stop()
        #cv2.destroyAllWindows()
        f.close()
        print('end')