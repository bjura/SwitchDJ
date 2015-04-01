"""
Module contains tools responsible for management of Pisak applications,
that is, launching them as stand-alone proccesses
handling their closure and switching between them.
It also contains the waiting panel that is launched in order to indicate
that some application is being loaded.
"""
import subprocess
import threading
import importlib
import sys

from gi.repository import GObject, Clutter, Mx

import pisak
from pisak import launcher, configurator, properties, widgets, arg_parser


class LoadingStage(Clutter.Stage):

    """
    Stage for the time a new app is being loaded.
    """

    def __init__(self):
        super().__init__()
        self.set_layout_manager(Clutter.BinLayout())
        self._init_background()
        self._init_text()

    def _init_background(self):
        background = widgets.BackgroundPattern()
        background.ratio_width = 1
        background.ratio_height = 1
        self.add_child(background)

    def _init_text(self):
        text = Mx.Label()
        text.set_style_class("LoadingPanel")
        text.set_text("Wczytywanie aplikacji...")
        text.set_x_align(Clutter.ActorAlign.CENTER)
        text.set_y_align(Clutter.ActorAlign.CENTER)
        self.add_child(text)


class AppManager(GObject.GObject,
                 configurator.Configurable,
                 properties.PropertyAdapter,
                 widgets.ButtonSource):
    """
    Class for running and managing different Pisak applications.
    Applications to be avalaible within the given Pisak session can be
    specified in a config file.
    """
    __gtype_name__ = "PisakAppManager"

    def __init__(self):
        super().__init__()
        self.current_app = None
        self.apps = []
        self.apply_props()
        self.loading_stage = LoadingStage()

    def launch_app(self, app_descriptor):
        """
        Launch an app with the given descriptor through the
        pisak.launcher module.

        :param app_descriptor: :see: :class: pisak.launcher.LauncherApp
        """
        launcher.run(app_descriptor)

    def get_buttons_descriptor(self):
        """
        Implementation of the widgets.ButtonSource method for getting
        buttons responsible for launching proper applications.

        :return: list of available buttons descriptions
        """
        buttons_list = []
        for app, values in self.apps.items():
            desc = {}
            desc["exec_path"] = self._get_exec_path(values["module"])
            desc["icon_size"] = values["icon_size"]
            desc["icon_name"] = values["icon_name"]
            desc["label"] = values["label"]
            desc["style_class"] = "PisakMainPanelButton"
            buttons_list.append(desc)
        return buttons_list

    def minimize_panel(self):
        """
        Deactivate the main panel and all its content.
        """
        pisak.app.window.input_group.stop_middleware()
        self.loading_stage.show()
        if not arg_parser.get_args().debug:
            self.loading_stage.set_fullscreen(True)

    def maximize_panel(self, event):
        """
        Reactivate the main panel and all its content.
        """
        self.loading_stage.hide()
        pisak.app.window.input_group.run_middleware()

    def run_app(self, button, app_exec):
        """
        Run an app with the given name as a new subprocess.
        Hide the current app stage.

        :param app_exec: name of an app
        """
        if self.current_app is None:
            self.minimize_panel()
            worker = threading.Thread(
                target=self._do_run_app,
                args=(app_exec, ),
                daemon=True)
            worker.start()

    def _do_run_app(self, app_exec):
        cmd = ["python3", app_exec]
        cmd.extend(sys.argv[1:])
        self.current_app = subprocess.Popen(cmd)
        self.current_app.wait()
        Clutter.threads_add_idle(0, self.maximize_panel, None)
        self.current_app = None

    def _get_exec_path(self, module_name):
        return importlib.import_module(".".join(["pisak",
                                                 module_name])).EXEC_PATH
