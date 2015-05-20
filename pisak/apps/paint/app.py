"""
Paint application main module
"""
from pisak import launcher
from pisak.libs import widgets
import pisak.libs.paint.widgets  # @UnusedImport
from pisak.libs.paint import handlers # @UnusedImport


def prepare_paint_main_view(window, script, data):
    easel = script.get_object("easel")
    button_start = script.get_object("button_start")
    if button_start is not None and isinstance (button_start, widgets.Button):
        button_start.connect("clicked", easel.clean_up)
        button_start.connect("clicked", lambda *_ : window.stage.destroy())


if __name__ == "__main__":
    _paint_app = {
        "app": "paint",
        "type": "clutter",
        "views": [("main", prepare_paint_main_view)]
    }
    launcher.run(_paint_app)
