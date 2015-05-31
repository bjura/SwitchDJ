from pisak import launcher


def prepare_main_view(app, window, script, data):
    ...


if __name__ == "__main__":
    dj_app = {
        "app": "dj",
        "type": "clutter",
        "views": [
            ("main", prepare_main_view)
        ]
    }
    launcher.run(dj_app)
