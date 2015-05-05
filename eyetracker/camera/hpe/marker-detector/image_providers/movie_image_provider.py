'''
Created on 29-07-2011

@author: Macias
'''

from image_providers.image_provider import ImageProvider, ImageProviderType
from PySide.QtCore import QSemaphore
import cv
from logger import get_logger
from tools.media_player.movie_player import MoviePlayer
from tools.media_player.play_control import PlayControl
from utils import createImg

class MovieImageProvider(ImageProvider,MoviePlayer):
    '''
    classdocs
    '''
    LOGGER=get_logger('MovieImageProvider')
    def __init__(self,file_name,start=0,**kwargs):
        '''
        Constructor
        '''
        ImageProvider.__init__(self,**kwargs)
        self.LOGGER.debug("Init:"+file_name)
        play_control=PlayControl()
        MoviePlayer.__init__(self, file_name,play_control)
        self._sem=QSemaphore()
#        self.control.frame_available.connect(self._release_sem)
        self._movie_time=0
        if start>0:
            self.control.set_pos(start)
        self.control.play()
        self._mirrored_img=None
    def _update_gui(self,img,movie_time):
#        self.LOGGER.debug('releease')
#        self._sem.release()
        self._movie_time=movie_time
    def _get_time(self):
        return self._movie_time
    def _update_image(self):
#        self.LOGGER.debug('acquire')
#        self._sem.acquire()
#        self._sem.tryAcquire(self._sem.available())
        if self._video_player._raw_image:
            if self._mirrored_img is None:
                self._mirrored_img=createImg(self._video_player._raw_image)
            cv.Flip(self._video_player._raw_image,self._mirrored_img,1)
            return self._mirrored_img
        return None
    def stop(self):
        self.LOGGER.debug("Stop")
        self.control.stop()
    def get_type(self):
        return ImageProviderType.MOVIE
def test1():
    from PySide.QtCore import QCoreApplication,QTimer,QThread
    from image_providers.image_input_manager import ImageInputManager
    app=QCoreApplication([])
    ip=ImageInputManager()
    ip.init_provider()
#    class _test(QThread):
    def run():
#            while True:
#                print "req_image"
        img=ip.request_data('current_image')
#                print "got_image"
        cv.ShowImage('img', img)
#                print "shown_image"
#                if i%10==0:
#                    if cv.WaitKey(1)==27:
#                        break
#    thread=_test()
#    thread.start()
    timer = QTimer()
    timer.timeout.connect(run)
    timer.start(0)
    def koniec():
        get_logger('KONIEC').debug('Koniec')
    def exit():
        print 'exit'
        app.exit()
        timer.stop()
    def play_movie():
        print 'play_movie'
        ip.send_data('play_movie', ['C:\\Users\\Macias\\AppData\\Roaming\\Titanis\\Titanis SM\\movies\\tmplzds4mtsm.avi',koniec,0])
    QTimer.singleShot(2000,play_movie)
    QTimer.singleShot(7000,exit)
    app.exec_()
    ip.stop()
def test2():
    from PySide.QtCore import QCoreApplication,QTimer,QThread
    cap=cv.CaptureFromCAM(0)
    app=QCoreApplication([])
    ip=MovieImageProvider('C:\\Users\\Macias\\AppData\\Roaming\\Titanis\\Titanis SM\\movies\\tmplzds4mtsm.avi',5)
    def stopped():
        print 'stopped'
    ip.stopped.connect(stopped)
    timer=QTimer()
    timer.timeout.connect(lambda:cv.ShowImage('img', ip.next()))
    timer.start(1)
    def stop():
        timer.stop()
        ip.clear()
        app.exit()
    QTimer.singleShot(2000,stop)
    app.exec_()
    del cap
if __name__=='__main__':
    test1()
