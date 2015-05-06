'''
Module which processes and launches pisak apps
'''
import os

from gi.repository import GtkClutter

from gi.repository import Gtk, Clutter, Mx

import pisak
from pisak import application, res
from pisak.libs import signals, unit, arg_parser, configurator, dirs, inputs

import pisak.libs.layout  # @UnusedImport
import pisak.libs.widgets  # @UnusedImport
import pisak.libs.handlers  # @UnusedImport


class LauncherError(Exception):

    """
    Error thrown when launcher meets an unexpected condition.
    """
    pass


class _UI(object):
    """
    User interface definition plain container.

    :param script: UI script
    """
    def __init__(self, script):
        for obj in script.list_objects():
            if hasattr(obj, "get_id"):
                setattr(self, obj.get_id(), obj)


class LauncherWindow(configurator.Configurable):
    def __init__(self, application, stage, descriptor):
        super().__init__()
        self.base_application = application
        self.stage = stage
        self.box = {}
        self.ui = None
        self.input_group = inputs.InputGroup(self.stage)
        self._init_layout()
        self.type = descriptor["type"]
        self._read_descriptor(descriptor)

    def load_initial_view(self):
        """
        Load initial view of the application.
        """
        self.load_view(self.initial_view)

    def _init_layout(self):
        '''Each class should implement it's own specific layout'''
        self.layout = Clutter.BinLayout()
        self.stage.set_layout_manager(self.layout)

    def _read_descriptor(self, descriptor):
        """
        Read the given descriptor. Valid descriptor must be in a form
        of a dictionary and should contain following keys: 'views' and
        'app', that are obligatory. 'app' is a string name of an application;
        'views' is a list of tuples, each consisting of the name of a single
        view and callable that is responsible for preparing that view.

        :param descriptor: dictionary that unambiguously describes
        an application that should be prepared and launched
        """
        view_list = descriptor.get("views")
        app_name = descriptor.get("app")
        app_elements = descriptor.get("elements")
        if app_elements:
            self._register_app_elements(app_elements)
        self._read_config(app_name)
        self._read_views(app_name, view_list)
        self.initial_view = os.path.join(app_name, "main")

    def _register_app_elements(self, elements):
        """
        Register all basic elements that will be used by the application. Elements are
        put inside the 'box' dictionary and then avalaible throughout the entire
        lifetime of the application.

        :param elements: dictionary with application basic elements
        """
        self.box.update(elements)

    def _read_config(self, app_name):
        """
        Extract configuration parameters for the current application.
        Currently, these are optional and can influence only:
        type of views content that will replace their default content.

        :param app_name: name of the current application
        """
        self.apply_props()
        self._configuration = self.config["PisakAppManager"]["apps"].get(app_name)

    def _read_views(self, app_name, view_list):
        """
        Translate the view list received in the descriptor into the one
        understood by the views loader.
        
        :param app_name: name of the current application
        :param view_list: list of tuples of avalaible views, each consists
        of view name and view callable preparator
        """
        content = 'default'
        if self._configuration:
            content = self._configuration.get("content")
        self.views = {}
        for view_name, preparator in view_list:
            self.views[os.path.join(app_name, view_name)] = (
                                dirs.get_json_path(app_name, view_name, 
                                                   content), preparator)

    def load_view(self, name, data=None):
        if name not in self.views.keys():
            message = "Descriptor has no view with name: {}".format(name)
            raise LauncherError(message)
        view_path, prepare = self.views.get(name)
        self.script = Clutter.Script()
        self.script.load_from_file(view_path)
        self.script.connect_signals_full(signals.connect_registered, self)
        self.ui = _UI(self.script)
        if prepare:
            prepare(self, self.script, data)
        children = self.stage.get_children()
        main_actor = self.script.get_object("main")
        if children:
            old_child = children[0]
            self.stage.replace_child(old_child, main_actor)
        else:
            self.stage.add_child(main_actor)
        self.input_group.load_content(main_actor)

def run(descriptor):
    # define inline class, because it uses descriptor
    class LauncherApp(application.Application):

        '''
        Implementation of application for JSON descriptors.
        '''

        def create_window(self, argv):
            clutter_window = LauncherWindow(self, Clutter.Stage(), descriptor)
            clutter_window.stage.set_title('Pisak Main')
            if arg_parser.get_args().debug:
                clutter_window.stage.set_size(800, 600)
                clutter_window.stage.set_user_resizable(True)
            else:
                clutter_window.stage.set_size(unit.w(1), unit.h(1))
                clutter_window.stage.set_fullscreen(True)
            return clutter_window

    class LauncherGtkApp(application.Application):
        '''
        Implementation of application for JSON descriptors inside GtkWindow.
        '''

        def create_window(self, argv):
            gtk_window = Gtk.Window()
            embed = GtkClutter.Embed()
            gtk_window.add(embed)
            gtk_window.stage = embed.get_stage()
            clutter_window = LauncherWindow(self, gtk_window.stage, descriptor)
            clutter_window.wrapper = gtk_window
            gtk_window.stage.set_title('Pisak Main')
            if arg_parser.get_args().debug:
                gtk_window.stage.set_size(800, 600)
                gtk_window.set_default_size(800, 600)
                gtk_window.set_resizable(True)
            else:
                gtk_window.stage.set_fullscreen(True)
                gtk_window.fullscreen()
            return clutter_window

    pisak.app = None
    if descriptor["type"] == "clutter":
        pisak.app = LauncherApp(arg_parser.get_args())
    elif descriptor["type"] == "gtk":
        pisak.app = LauncherGtkApp(arg_parser.get_args())
    pisak.app.window.load_initial_view()
    pisak.app.main()
    pisak.app = None
