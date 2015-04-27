from PySide.QtCore import SIGNAL, QObject, QTimer, QMutex
from databus.databus_user import DatabusUser

from cam_image_provider import CamImageProvider, CamImageProviderError
from image_provider import ImageProvider
from logger import get_logger
from gof.singleton import Singleton
from cam_image_provider import NoCameraConnectedError
from static_image_provider import SingleImageProvider
from image_providers.image_provider import ImageProviderType
LOGGER = get_logger('ImageInputManager')
class ImageInputManager(Singleton, DatabusUser):
    NONE = 0
    CAMERA = 1
    KINECT = 2
    MOVIE = 3
    def init(self):
        self._init_databus()
        self._check_timer = QTimer(self)
        self._check_timer.timeout.connect(self._check_camera_connection)
        self._check_timer.setInterval(1000)
        self.image_provider = None
        self._old_provider = None
    def _get_provider(self, show_errors=False):
        try:
            from image_providers.kinect_provider import KinectProvider, Transform
            i_p = KinectProvider(-1)
            i_p.set_transform(Transform.VIEWPOINT_STRETCH)            
            LOGGER.info("Kinect is connected!!")
#            i_p.print_fps(True)
            return i_p
        except Exception as ex:
            if show_errors:
                LOGGER.warning('Kinect load failed: ' + str(ex))
        try:
            i_p = CamImageProvider()
            LOGGER.info("Camera is connected")
#            i_p.print_fps(True)
            return i_p
        except NoCameraConnectedError:
            return None
    def init_provider(self):
        i_p = self._get_provider(True)
        if i_p:
            self.image_provider = i_p
        else:
            LOGGER.warning("No Kinect and no camera. Static Image Provider")
            self._camera_disconnected()
        
    def _is_kinect(self):
        return self.image_provider and self.image_provider.get_type() == self.KINECT
    
    def _type(self):
        if self.image_provider:
            return self.image_provider.get_type()
        else: return ImageProviderType.NONE
    
    is_kinect = property(_is_kinect)
    type = property(_type)
    
    def next(self):
        return self.get_current_image()
    def _get_current_image(self):
        return self.image_provider.current_image
    def _get_current_time(self):
        return self.image_provider.current_time 
    current_image = property(_get_current_image)
    current_time = property(_get_current_time)
    def get_current_image(self):
        if self.image_provider is None:
            self.init_provider()
        try:
            return self.image_provider.next()
        except NoCameraConnectedError:
            self._camera_disconnected()
            return self.image_provider.next()
    def play_movie(self, p_file_name, stop_function=None, start_time=0):
        self.reset_provider()
        try:
            from movie_image_provider import MovieImageProvider
            movie_ip = MovieImageProvider(p_file_name, start_time)
            self._old_provider = self.image_provider
            if stop_function is not None:
                movie_ip.control.stopped.connect(stop_function)
            movie_ip.control.stopped.connect(self.reset_provider)
            self.image_provider = movie_ip      
        except Exception as ex:
#            raise ex
            LOGGER.debug("Play movie error: " + unicode(ex))
            if stop_function:
                stop_function()
    def reset_provider(self, stop=False):
        LOGGER.debug('reset_provider ' + str(self.image_provider))
        if self._old_provider is None:
            return
        prov = self.image_provider
        type = self.type
        self.image_provider = self._old_provider
        self._old_provider = None
        if isinstance(prov, MovieImageProvider):
#            if not stop:
            prov.stopped.disconnect()
            prov.clear()
            del prov        
        LOGGER.debug('reset_provider done:' + str(self.image_provider))
    def _camera_disconnected(self):
        LOGGER.debug("Camera disconnected")
        self.image_provider = SingleImageProvider()
        self.send_data('image_provider_changed')
        self._check_timer.start()
    
    def _check_camera_connection(self):
        i_p = self._get_provider()
        if not i_p:
            return
        self.image_provider = i_p
        self._check_timer.stop()
        self.send_data('image_provider_changed')
    
    def _clear(self):
        if self.image_provider:
            self.image_provider.stop()
        if self._old_provider:
            self._old_provider.stop()
        self.image_provider = None
        self._old_provider = None

    def stop(self):
        self._clear()
    def start(self):
        self._init_databus()
        if not self.image_provider:
            self.init_provider()
        if self.image_provider:
            self.image_provider.start()
    def show_image(self, file_name):
        LOGGER.debug('show_image:' + file_name)
        self.reset_provider()
        self._old_provider = self.image_provider
        self.image_provider = SingleImageProvider(file_name)
        LOGGER.debug('show image done')
    def __del__(self):
        self.stop()
    
    ##########################################################################
    # Databus functions
    
    def _init_databus(self):
        self.register_as_sender(['image_input_active', 'current_image'])
        self.register_as_listener(['play_movie', 'stop_movie', 'show_image'])
    def need_data(self, p_data_symbol, p_parameters=None):
        if p_data_symbol == 'image_input_active':
            return self._type != self.NONE
        elif p_data_symbol == 'current_image':
            return self.get_current_image()
        
    def got_data(self, p_data_symbol, p_data, p_sender=None):
        if p_data_symbol == 'play_movie':
            if isinstance(p_data, list):
                self.play_movie(*p_data)
            else:
                self.play_movie(p_data)
        elif p_data_symbol == 'stop_movie':
            self.reset_provider(p_data)
        elif p_data_symbol == 'show_image':
            self.show_image(p_data)
        
    # Databus functions
    ##########################################################################
import atexit

@atexit.register
def stop_image():
    ImageInputManager()._clear()
