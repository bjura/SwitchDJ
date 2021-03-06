'''
ClutterScript paint specific signal handler library
'''
from gi.repository import Clutter

from pisak.libs import signals, utils


@signals.registered_handler("paint/set_line_color")
def set_line_color(button, _app):
    """
    Set easel line color
    """
    easel = button.related_object
    easel.line_rgba = utils.convert_color(button.get_background_color())


@signals.registered_handler("paint/set_line_width")
def set_line_width(button, _app):
    """
    Set easel line width
    """
    easel = button.related_object
    easel.line_width = int(button.text.split(" ")[0])


@signals.registered_handler("paint/clear_canvas")
def clear_canvas(easel, _app):
    """
    Clear easel canvas
    """
    easel.clear_canvas()


@signals.registered_handler("paint/save_to_file")
def save_to_file(easel, _app):
    """
    Save easel canvas picture to png file
    """
    easel.save_to_file()


@signals.registered_handler("paint/new_spot")
def new_spot(easel, _app):
    """
    Localize new drawing spot
    """
    easel.run_localizer()


@signals.registered_handler("paint/navigate")
def navigate(easel, _app):
    """
    Back to drawing and navigate
    """
    easel.run_navigator()


@signals.registered_handler("paint/erase")
def erase(easel, _app):
    """
    Erase one step backward
    """
    easel.erase()
