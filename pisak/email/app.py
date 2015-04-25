"""
Email application main module.
"""
import time

from gi.repository import GObject

from pisak import launcher, handlers, res, logger
from pisak.viewer import model
from pisak.email import address_book, message, config

from pisak.email import widgets  #@UnusedImport
import pisak.email.handlers  #@UnusedImport
import pisak.speller.handlers  #@UnusedImport
import pisak.speller.widgets  #@UnusedImport
import pisak.viewer.widgets  #@UnusedImport


_LOG = logger.getLogger(__name__)


ELEMENTS = {
    "new_message": message.SimpleMessage(),
    "address_book": address_book.AddressBook()
}


BUILTIN_CONTACTS = [
	{
		"name": "PISAK",
		"address": "kontakt@pisak.org",
		"photo": res.get("logo_pisak.jpg")
	}
 ]


def prepare_main_view(app, script, data):
    handlers.button_to_view(app, script, "button_exit")
    handlers.button_to_view(app, script, "button_inbox", "email/inbox")
    handlers.button_to_view(app, script, "button_sent", "email/sent")
    handlers.button_to_view(app, script, "button_drafts", "email/drafts")
    handlers.button_to_view(
        app, script, "button_address_book", "email/address_book")
    handlers.button_to_view(
        app, script, "button_new_message", "email/speller_message_subject")
    for contact in BUILTIN_CONTACTS:
	    app.box.address_book.add_contact(contact)


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
                    "email/address_book", {"pick_recipents_mode": True})


def prepare_speller_message_subject_view(stage, script, data):
    handlers.button_to_view(stage, script, "button_exit")
    handlers.button_to_view(stage, script, "button_proceed",
                            "email/speller_message_body")


def prepare_speller_message_to_view(stage, script, data):
    handlers.button_to_view(stage, script, "button_exit")
    handlers.button_to_view(stage, script, "button_proceed", "email/sent")


def prepare_address_book_view(app, script, data):

    def on_contact_select(tile, contact):
        """
        On contact tile select.

        :param tile: tile representing single contact
        :param contact: contact dictionary
        """
        tile.toggled = not tile.toggled
        if tile.toggled:
            app.box.new_message.recipents.append(contact["address"])
        else:
            app.box.new_message.recipents.remove(contact["address"])

    handlers.button_to_view(app, script, "button_exit")
    handlers.button_to_view(app, script, "button_back", "email/main")
    today = "DATA:   " + time.strftime("%d-%m-%Y")
    app.ui.date.set_text(today)
    data_source = script.get_object("data_source")

    if data and data.get("pick_recipents_mode"):
        specific_button= app.ui.button_send_message
        tile_handler = lambda tile, contact: on_contact_select(tile, contact)
    else:
        specific_button = app.ui.button_new_contact
        tile_handler = lambda tile, contact: app.load_view(
            "email/contact", {"contact": contact})
        handlers.button_to_view(
            app, script, "button_new_contact", "email/contact")

    app.ui.button_menu_box.replace_child(app.ui.button_specific, specific_button)
    data_source.item_handler = tile_handler


def prepare_contact_view(app, script, data):
    handlers.button_to_view(app, script, "button_exit")
    handlers.button_to_view(app, script, "button_back", "email/main")
    handlers.button_to_view(app, script, "button_edit_name",
                            "email/speller_contact_name")
    handlers.button_to_view(app, script, "button_edit_address",
                            "email/speller_contact_address")
    handlers.button_to_view(app, script, "button_edit_photo",
                            "email/viewer_contact_library")
    handlers.button_to_view(app, script, "button_create_message",
                             "email/speller_message_subject")
    if data:
        contact = data["contact"]
        if "photo" in contact:
            try:
                app.ui.photo.set_from_file(contact["photo"])
            except GObject.GError as e:
                _LOG.error(e)
        if "name" in contact:
            app.ui.contact_name_text.set_text(contact["name"])
        if "address" in contact:
            app.ui.contact_address_text.set_text(contact["address"])


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
        "elements": ELEMENTS,
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
