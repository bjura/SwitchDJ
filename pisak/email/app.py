"""
Email application main module.
"""
import time

from pisak import launcher, handlers
from pisak.viewer import model

from pisak.email import address_book, widgets  #@UnusedImport
import pisak.speller.handlers  #@UnusedImport
import pisak.speller.widgets  #@UnusedImport
import pisak.viewer.widgets  #@UnusedImport


def prepare_main_view(stage, script, data):
    handlers.button_to_view(stage, script, "button_exit")
    handlers.button_to_view(stage, script, "button_inbox", "email/inbox")
    handlers.button_to_view(stage, script, "button_sent", "email/sent")
    handlers.button_to_view(stage, script, "button_drafts", "email/drafts")
    handlers.button_to_view(
        stage, script, "button_address_book", "email/address_book")
    handlers.button_to_view(
        stage, script, "button_new_message", "email/speller_message_subject")


def prepare_drafts_view(stage, script, data):
    handlers.button_to_view(stage, script, "button_exit")
    handlers.button_to_view(
        stage, script, "button_new_message", "email/speller_message_subject")
    handlers.button_to_view(stage, script, "button_back", "email/main")
    date_widget = script.get_object("date")
    today = "DATA:   " + time.strftime("%d-%m-%Y")
    date_widget.set_text(today)


def prepare_inbox_view(stage, script, data):
    handlers.button_to_view(stage, script, "button_exit")
    handlers.button_to_view(
        stage, script, "button_new_message", "email/speller_message_subject")
    handlers.button_to_view(stage, script, "button_back", "email/main")
    date_widget = script.get_object("date")
    today = "DATA:   " + time.strftime("%d-%m-%Y")
    date_widget.set_text(today)

def prepare_sent_view(stage, script, data):
    handlers.button_to_view(stage, script, "button_exit")
    handlers.button_to_view(
        stage, script, "button_new_message", "email/speller_message_subject")
    handlers.button_to_view(stage, script, "button_back", "email/main")
    date_widget = script.get_object("date")
    today = "DATA:   " + time.strftime("%d-%m-%Y")
    date_widget.set_text(today)


def prepare_speller_message_body_view(stage, script, data):
    handlers.button_to_view(stage, script, "button_exit")
    handlers.button_to_view(stage, script, "button_proceed",
                            "email/speller_message_to")

def prepare_speller_message_subject_view(stage, script, data):
    handlers.button_to_view(stage, script, "button_exit")
    handlers.button_to_view(stage, script, "button_proceed",
                            "email/speller_message_body")


def prepare_speller_message_to_view(stage, script, data):
    handlers.button_to_view(stage, script, "button_exit")
    handlers.button_to_view(stage, script, "button_proceed", "email/sent")


def prepare_address_book_view(stage, script, data):
    handlers.button_to_view(stage, script, "button_exit")
    handlers.button_to_view(
        stage, script, "button_new_contact", "email/contact")
    handlers.button_to_view(stage, script, "button_back", "email/main")
    date_widget = script.get_object("date")
    today = "DATA:   " + time.strftime("%d-%m-%Y")
    date_widget.set_text(today)


def prepare_contact_view(stage, script, data):
    handlers.button_to_view(stage, script, "button_exit")
    handlers.button_to_view(stage, script, "button_back", "email/main")
    handlers.button_to_view(stage, script, "button_edit_name",
                            "email/speller_contact_name")
    handlers.button_to_view(stage, script, "button_edit_address",
                            "email/speller_contact_address")
    handlers.button_to_view(stage, script, "button_edit_photo",
                            "email/viewer_contact_library")

def prepare_speller_contact_name_view(stage, script, data):
    handlers.button_to_view(stage, script, "button_exit")
    handlers.button_to_view(stage, script, "button_proceed", "email/contact")


def prepare_speller_contact_address_view(stage, script, data):
    handlers.button_to_view(stage, script, "button_exit")
    handlers.button_to_view(stage, script, "button_proceed", "email/contact")


def prepare_viewer_contact_library_view(stage, script, data):
    handlers.button_to_view(stage, script, "button_exit")
    handlers.button_to_view(stage, script, "button_back", "email/contact")
    tile_source = script.get_object("library_data")
    tile_source.item_handler = lambda tile, album: stage.load_view(
        "email/viewer_contact_album", {"album_id": album})

def prepare_viewer_contact_album_view(stage, script, data):
    handlers.button_to_view(stage, script, "button_exit")
    handlers.button_to_view(
        stage, script, "button_library", "email/viewer_contact_library")
    album_id = data["album_id"]
    library = model.get_library()
    header = script.get_object("header")
    header.set_text(library.get_category_by_id(album_id).name)
    data_source = script.get_object("album_data")
    def photo_tile_handler(tile, photo_id, album_id):
        stage.load_view("email/contact")
    data_source.item_handler = photo_tile_handler
    data_source.data_set_id = album_id

def prepare_single_message_view(stage, script, data):
    handlers.button_to_view(stage, script, "button_exit")


if __name__ == "__main__":
    email_app = {
        "app": "email",
        "type": "clutter",
        "views": [
            ("main", prepare_main_view),
            ("drafts", prepare_drafts_view),
            ("inbox", prepare_inbox_view),
            ("sent", prepare_sent_view),
            ("single_message", prepare_single_message_view),
            ("address_book", prepare_address_book_view),
            ("contact", prepare_contact_view),
            ("speller_message_body", prepare_speller_message_body_view),
            ("speller_message_to", prepare_speller_message_to_view),
            ("speller_message_subject", prepare_speller_message_subject_view),
            ("speller_contact_name", prepare_speller_contact_name_view),
            ("speller_contact_address", prepare_speller_contact_address_view),
            ("viewer_contact_library", prepare_viewer_contact_library_view),
            ("viewer_contact_album", prepare_viewer_contact_album_view)
        ]
    }
    launcher.run(email_app)