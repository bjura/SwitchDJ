"""
Basic classes for Pisak application.
"""
import sys, os

from configobj import ConfigObj

from gi.repository import Gtk, GObject, Clutter, Mx, ClutterGst

from pisak import res, sound_effects, configurator, dirs, logger

_LOG = logger.getLogger(__name__)


class Application(configurator.Configurable):
    """
    Abstract application class. This is the entry point for all Pisak apps.
    """
    def __init__(self, argv):
        """
        Initialize the application. Call methods that initialize
        application stage, style and global sound effects player. 
        
        :param: argv application arguments
        """
        super().__init__()
        Gtk.init(sys.argv)
        Clutter.init(sys.argv)
        self._configure()
        self._initialize_style()
        self._initialize_window(argv)
        self._initialize_sound_effects_player()

    def _configure(self):
        self.apply_props()
        self.sound_effects_enabled = self.config.as_bool("sound_effects_enabled")
        self.sound_effects_volume = self.config.as_float("sound_effects_volume")
        self.style = dirs.get_css_path(self.config.get("skin"))
        self.sound_effects = {}
        for k, v in self.config.get("sound_effects").items():
            self.sound_effects[k] = res.get(v)

    def _initialize_style(self):
        # load style
        try:
            Mx.Style.get_default().load_from_file(self.style)
        except GObject.GError:
            raise Exception("Failed to load default style.")

    def _initialize_window(self, argv):
        # create and set up app window
        self.window = self.create_window(argv)
        if hasattr(self.window, "wrapper") and isinstance(self.window.wrapper,
                                                          Gtk.Window):
            self.window.wrapper.connect("destroy", lambda _: Gtk.main_quit())
        else:
            self.window.stage.connect("destroy", lambda _: Clutter.main_quit())

    def _initialize_sound_effects_player(self):
        if self.sound_effects_enabled:
            self._sound_effects_player = sound_effects.SoundEffectsPlayer(self.sound_effects)
            self._sound_effects_player.set_volume(self.sound_effects_volume)
        else:
            self._sound_effects_player = None

    def _shutdown_sound_effects_player(self):
        if self._sound_effects_player is not None:
            self._sound_effects_player.shutdown()

    def create_window(self, argv):
        """
        Abstract method which should create Clutter.Stage instance
        :param: argv application arguments
        """
        raise NotImplementedError()

    def play_sound_effect(self, sound_name):
        """
        Play one of the previously instantiated sound effects by the means of
        an internal player.

        :param sound_name: name of the sound to be played
        """
        if self._sound_effects_player is not None:
            self._sound_effects_player.play(sound_name)

    def main(self):
        """
        Starts the application main loop.
        """
        if hasattr(self.window, "wrapper") and isinstance(self.window.wrapper,
                                                          Gtk.Window):
            self.window.wrapper.show_all()
            _LOG.debug("Running GTK loop")
            Gtk.main()
        else:
            self.window.stage.show_all()
            _LOG.debug("Running Clutter loop")
            Clutter.main()
        self._shutdown_sound_effects_player()
