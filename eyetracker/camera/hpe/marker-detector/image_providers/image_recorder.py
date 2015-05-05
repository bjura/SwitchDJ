'''
Created on 24-03-2011

@author: Macias
'''
import cv
from utils import createImg
class ImageRecorder(object):
    '''
    classdocs
    '''


    def __init__(self,p_record_to=None,p_fourcc='XVID'):
        '''
        Constructor
        '''
        self.record_to=p_record_to
        self.fourcc = p_fourcc if type(p_fourcc)==int else cv.CV_FOURCC(*p_fourcc)
        self.init_recording=True
        self.video_wr=None

    def _init_recording(self,img):
        if self.record_to is not None:
            self.video_wr = cv.CreateVideoWriter(self.record_to,
                                                 self.fourcc, 24,
                                                 cv.GetSize(img),
                                                 1 if img.nChannels>1 else 0)
            import platform
            if platform.system()!='Windows':
                self.record_img = createImg(img)
            else: self.record_img=None
        else:
            self.video_wr = None
        self.init_recording=False

    def write_frame(self,p_image):
        if self.init_recording and p_image is not None:
            self._init_recording(p_image)
        if self.video_wr:
            if self.record_img:
                cv.Copy(p_image,self.record_img)
                cv.WriteFrame(self.video_wr, self.record_img)
            else:
                cv.WriteFrame(self.video_wr, p_image)
    def __del__(self):
        del self.video_wr
