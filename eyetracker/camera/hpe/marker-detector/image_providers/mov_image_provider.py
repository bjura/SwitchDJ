'''
Created on 2011-02-10

@author: Macias
'''
import cv
import time
import math
from image_provider import ImageProvider
from xml_exporter import XMLExporter
class MovieImageProvider(ImageProvider):
    '''
    Provides images from supported video file
    '''
    xml_init_fields = ('file_name','real_time','start_from')
    def __init__(self,file_name, real_time=False, start_from=0,**kwargs):
        '''
        Initializes object
        @param file_name: video file to open
        @param realtime: if false provide images frame after frame, if true
                         provide images in realtime (ie. ommiting some)
        @param start_from: frame to start from
        '''
        super(MovieImageProvider, self).__init__(**kwargs)
        if file_name is not None:
            self.init(file_name,real_time,start_from)
    def __repr__(self):
        return "Movie file: "+str(self.file_name)+" strat_from: "+str(self.start_from)

    def init(self,file_name,real_time=False,start_from=0):
        self.file_name = file_name
        self.start_from = start_from
        self.capture = cv.CaptureFromFile(file_name)
        self.real_time = real_time
        self.fps = cv.GetCaptureProperty(self.capture, cv.CV_CAP_PROP_FPS) or 1
        self.f_count= cv.GetCaptureProperty(self.capture, cv.CV_CAP_PROP_FRAME_COUNT)
        self.displayed = list(range(start_from + 1))
        self.index = -1
        self.last_frame=0
        if not self.real_time:
            self.get_time=self._get_time
        self.start_time=self.get_time()
        for i in range(start_from - 1):
            self.update_image()
    def _get_time(self):
        return self.last_frame/float(self.fps)
    def set_time_function(self,func):
        if self.real_time:
            super(MovieImageProvider, self).set_time_function(func)
    def _getFrameNumber(self, step):
        dis = self.displayed
        self.index += step
        if self.index < 0:
            self.index = 0;
        if self.index >= len(dis):
            if self.real_time:
                f = int(math.ceil((self.get_time() - self.start) * self.fps))
                dis.append(f)
            else:
                dis.append(dis[-1] + 1)
        return self.displayed[int(self.index)]

    def _update_image(self):
        self.last_frame = frame=self._getFrameNumber(self.direction);
        if frame<self.f_count:
            cv.SetCaptureProperty(self.capture, cv.CV_CAP_PROP_POS_FRAMES, frame);
        img = cv.QueryFrame(self.capture)
        return img
    def stop(self):
        del self.capture

if __name__=='__main__':
    from image_providers import CamImageProvider
    ip=CamImageProvider(0,'test.avi')
    start=time.time()
    while time.time()<start+5 and cv.WaitKey(1)!=27:
        img=ip.next()
        cv.ShowImage("image", img)
    ip.stop()
    del ip
    ip=MovieImageProvider('test.avi')
    img=ip.next()
    while img is not None and cv.WaitKey(1)!=27:
        cv.ShowImage('image2', img)
        img=ip.next()
    import os
    os.remove('test.avi')

XMLExporter.add_class(MovieImageProvider)
