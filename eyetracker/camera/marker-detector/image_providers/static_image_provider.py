'''
Created on 08-03-2011

@author: Macias
'''
from image_providers.image_provider import ImageProvider
import cv
class StaticImageProvider(ImageProvider):
    '''
    classdocs
    '''


    def __init__(self, filenames, *args, **kwargs):
        '''
        Constructor
        '''
        super(StaticImageProvider, self).__init__(*args, **kwargs)
        self.filenames = filenames
        self._imgs = []
        self.load_images(filenames)
    
    def load_images(self, filenames):
        for f in filenames:
            self._imgs.append(cv.LoadImage(f))

    def _update_image(self):
        self.index = (self.index + self.direction) % len(self._imgs)        
        self.current_image = cv.CloneImage(self._imgs[self.index])
        return self.current_image
    
class SingleImageProvider(StaticImageProvider):
    def __init__(self, filename=u'resources\\camera_disconnected.png'):
        StaticImageProvider.__init__(self, [filename])

if __name__ == '__main__':
    from image_providers import CamImageProvider
    ip = CamImageProvider(0)
    filenames = ['test%d.png' % i for i in range(10)]
    for f in filenames:
        cv.WaitKey(200)
        img = ip.next()
        cv.ShowImage("image", img)
        cv.SaveImage(f, img)
    ip.stop()
    del ip
    ip = StaticImageProvider(filenames)
    img = ip.next()
    while img is not None and cv.WaitKey(1) != 27:
        cv.ShowImage('image2', img)
        img = ip.next()
    import os
    for f in filenames:
        os.remove(f)
