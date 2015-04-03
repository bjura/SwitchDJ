import threading

from gi.repository import GObject, Clutter

from pisak import properties, configurator


class Predictor(GObject.GObject, properties.PropertyAdapter,
                 configurator.Configurable):
    """
    Base class for objects that follow changes in the given target
    text and supply suggestions based on the text context. Searching
    through a predictor database happens in another thread.

    Properties:

    * :attr:`target`
    """
    __gsignals__ = {
        "content_update": (
            GObject.SIGNAL_RUN_FIRST, None, ()),
        "processing_on": (
            GObject.SIGNAL_RUN_FIRST, None, ())
    }
    __gproperties__ = {
        "target": (
            Clutter.Actor.__gtype__,
            "target to follow",
            "id of text box to follow",
            GObject.PARAM_READWRITE)
    }

    def __init__(self):
        super().__init__()
        self.target = None
        self.content = []

    def get_suggestion(self, accuracy_level):
        if accuracy_level < len(self.content):
            return self.content[accuracy_level]

    def do_prediction(self, text, position):
        raise NotImplementedError

    def _update_content(self, *args):
        self.emit("processing-on")
        text = self.target.get_text()
        position = self.target.get_cursor_position()
        worker = threading.Thread(
            target=self.do_prediction, args=(text, position), daemon=True)
        worker.start()

    def _follow_target(self):
        if self.target is not None:
            text_field = self.target.clutter_text
            text_field.connect("text-changed", self._update_content)

    def _stop_following_target(self):
        try:
            if self.target is not None:
                text_field = self.target.clutter_text
                text_field.disconnect_by_func("text-changed", self._update_content)
        except AttributeError:
            return None

    @property
    def target(self):
        return self._target

    @target.setter
    def target(self, value):
        self._stop_following_target()
        self._target = value
        self._follow_target()