#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 01-03-2012

@author: Macias
'''
import cv
def createImg(img, d=None, c=None, zero=False):
    if isinstance(img, tuple):
        if d is None:
            d = 8
        if c is None:
            c = 1
        res = cv.CreateImage(img, d, c)
    else:
        if d is None:
            d = img.depth
        if c is None:
            c = img.nChannels
        res = cv.CreateImage(cv.GetSize(img), d, c)
    if zero:
        cv.Zero(res)
    return res

def putText(img, text, color=(255, 255, 255), size=2, position=None):
    import cv2, numpy as np
    fontFace = cv2.FONT_HERSHEY_SIMPLEX
    fontScale = 2
    thickness = 3
    if position is None:
        textSize, _ = cv2.getTextSize(text, fontFace, fontScale, thickness)
        position = ((img.shape[1] - textSize[0]) / 2, (img.shape[0] + textSize[1]) / 2)
    cv2.putText(img, text, position, fontFace, fontScale, color, thickness)

def textImage(size, text, color=(0, 0, 0)):
    import cv2, numpy as np
    width, height = size

    img = np.zeros((height, width, len(color)), dtype=np.uint8)
    cv2.rectangle(img, (0, 0), (width - 1, height - 1), color, -1)
    putText(img, text)
    return img
