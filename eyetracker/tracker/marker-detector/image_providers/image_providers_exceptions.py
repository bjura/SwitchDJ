class ImageProvidersException(Exception):
    """Base class for image providers module"""
    pass
    
class UpdateImageNotImplementedError(ImageProvidersException):
    """Thrown when subclass of ImageProvider doesn't implement 
    update_image function.
    
    """
    pass