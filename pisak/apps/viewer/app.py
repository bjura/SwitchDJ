'''
Module with app-specific code for photo viewer.
'''
from pisak import launcher
from pisak.libs import handlers
from pisak.libs.viewer import model

from pisak.libs.viewer import widgets  # @UnusedImport
import pisak.libs.viewer.handlers  # @UnusedImport


def prepare_photo_view(stage, script, data):
    album_id = data["album_id"]
    photo_id = data["photo_id"]

    data_source = script.get_object("photo_data_source")
    data_source.data_set_id = album_id

    slideshow = script.get_object("slideshow_widget")
    slideshow.show_initial_photo_id(photo_id)

    handlers.button_to_view(stage, script, "button_edition",
                    "viewer/photo_editing", (slideshow, album_id, photo_id))
    handlers.button_to_view(stage, script, "button_album",
                            "viewer/album", {"album_id": album_id})
    handlers.button_to_view(stage, script, "button_library", "viewer/main")

    library = model.get_library()
    header = script.get_object("header")
    header.set_text(library.get_category_by_id(album_id).name)


def prepare_album_view(stage, script, data):
    album_id = data["album_id"]

    handlers.button_to_view(stage, script, "button_library", "viewer/main")
    handlers.button_to_view(stage, script, "button_start")

    library = model.get_library()
    header = script.get_object("header")
    header.set_text(library.get_category_by_id(album_id).name)

    data_source = script.get_object("library_data")
    def photo_tile_handler(tile, photo_id, album_id):
        stage.load_view(
            "viewer/photo", {"photo_id": photo_id, "album_id": album_id})
    data_source.item_handler = photo_tile_handler
    data_source.data_set_id = album_id


def prepare_library_view(stage, script, data):
    library_data = script.get_object("library_data")
    library_data.item_handler = lambda tile, album: stage.load_view(
        "viewer/album", {"album_id": album})
    handlers.button_to_view(stage, script, "button_start")


def prepare_photo_editing_view(stage, script, data):
    photo = script.get_object("slide")
    photo.photo_path = data[0].slide.photo_path
    handlers.button_to_view(stage, script, "button_photo", "viewer/photo",
                        {"photo_id": data[2], "album_id": data[1]})
    handlers.button_to_view(stage, script, "button_start")


if __name__ == "__main__":
    model.get_library()
    _viewer_app = {
        "app": "viewer",
        "type": "clutter",
        "views": [("photo", prepare_photo_view),
                 ("album", prepare_album_view),
                 ("main", prepare_library_view),
                 ("photo_editing", prepare_photo_editing_view)]
    }
    launcher.run(_viewer_app)
