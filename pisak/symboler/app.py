"""
Main module of the symboler application. Launching and managing all the
application's views takes place here.
"""
import sys

from pisak import launcher, res, handlers
from pisak.symboler import symbols_manager

import pisak.symboler.widgets  # @UnusedImport
import pisak.symboler.handlers  # @UnusedImport


def prepare_symboler_view(stage, script, data):
    handlers.button_to_view(stage, script, "button_exit")


if __name__ == "__main__":
    _symboler_app = {
        "app": "symboler",
        "type": "clutter",
        "views": [("main", prepare_symboler_view)]
    }
    symbols_manager.create_model()
    launcher.run(_symboler_app)
