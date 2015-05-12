import sys

from pisak import launcher, res
from pisak.libs import handlers

from pisak.libs.speller import widgets  # @UnusedImport
import pisak.libs.speller.handlers  # @UnusedImport



def prepare_main_view(stage, script, data):
    handlers.button_to_view(stage, script, "button_exit")


if __name__ == "__main__":
    _speller_app = {
        "app": "speller",
        "type": "clutter",
        "views": [("main", prepare_main_view)]
    }
    launcher.run(_speller_app)
