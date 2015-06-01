from pisak import launcher
from pisak.libs.dj import core

import pisak.libs.dj.widgets  # @UnusedImport
import pisak.libs.dj.handlers  # @UnusedImport


ELEMENTS = {
    "song": core.Song()
}


def prepare_main_view(app, script, data):
    ...


if __name__ == "__main__":
    dj_app = {
        "app": "dj",
        "type": "clutter",
        "elements": ELEMENTS,
        "views": [
            ("main", prepare_main_view)
        ]
    }
    launcher.run(dj_app)
