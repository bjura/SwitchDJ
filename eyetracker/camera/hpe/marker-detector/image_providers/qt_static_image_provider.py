#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 15-03-2012

@author: Macias
'''
from image_providers.image_provider import ImageProvider
from qt.gui import *
import cv
import copy
from image_providers.static_image_provider import StaticImageProvider
from resources import image_provider_rc

class QTStaticImageProvider(StaticImageProvider):
    '''
    classdocs
    '''

    def __init__(self, filenames):
        '''
        Constructor
        '''
        super(QTStaticImageProvider, self).__init__(filenames)

    def load_images(self, filenames):
        for f in filenames:
            img = QImage(f)
            cvimg = cv.CreateImage((img.width(), img.height()), 8, 4)            
            img2 = img.convertToFormat(img.Format_ARGB32)
            data = str(img2.constBits())
            cv.SetData(cvimg, data, img.width() * 4)
            self._imgs.append(cvimg)


class QtSingleImageProvider(QTStaticImageProvider):
    def __init__(self, filename=":/image_provider/disconnected"):
        super(QtSingleImageProvider, self).__init__([filename])
