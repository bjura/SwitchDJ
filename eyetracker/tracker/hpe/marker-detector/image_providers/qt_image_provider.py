#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 27-02-2012

@author: Macias
'''
from qt.core import QObject, Signal
from cv import iplimage
from titanis.opencv_image import OpenCVImage
import time
class QTImageProvider(QObject):
    '''
    classdocs
    '''
    frame_available = Signal(object, float)

    def __init__(self, image_provider, frame_rate=15):
        '''
        Constructor
        '''
        super(QTImageProvider, self).__init__()
        self._image_provider = image_provider
        img = self._image_provider.next()
        self.image = OpenCVImage(img.width, img.height)
        self._timerId = self.startTimer(50)
        self.frame_rate = frame_rate
        self.next_frame = 0
        self.interval = 1.0 / self.frame_rate
    
    def refresh(self):        
        img, time = self._image_provider.getNext()
        self.image.refresh(img)
        return time
        
    def timerEvent(self, tEvent):
        t = time.time()
        if t < self.next_frame:
            return
        late = min(t - self.next_frame, self.interval)        
        self.next_frame = t + self.interval - late
        t = 0
        t = self.refresh()        
        self.frame_available.emit(self.image, t)
    
    def setFrameRate(self, frame_rate):
        self.frame_rate = frame_rate
        self.interval = 1.0 / self.frame_rate
        
    def getFrameRate(self):
        return self.frame_rate
    
    def next(self):
        return self.image.org_image
