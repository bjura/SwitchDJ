"""
Email application main module.
"""
from gi.repository import GObject

from pisak import launcher, handlers, res, logger
from pisak.viewer import model
from pisak.email import address_book, message, config, imap_client

from pisak.email import widgets  #@UnusedImport
import pisak.email.handlers  #@UnusedImport
import pisak.speller.handlers  #@UnusedImport
import pisak.speller.widgets  #@UnusedImport
import pisak.viewer.widgets  #@UnusedImport


_LOG = logger.getLogger(__name__)


ELEMENTS = {
    "new_message": message.SimpleMessage(),
    "address_book": address_book.AddressBook(),
    "imap_client": imap_client.IMAPClient()
}


BUILTIN_CONTACTS = [
	{
		"name": "PISAK",
		"address": "kontakt@pisak.org",
		"photo": res.get("logo_pisak.png")
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
        app.box["address_book"].add_contact(contact)
    app.box.imap_client.login()


def prepare_drafts_view(stage, script, data):
    handlers.button_to_view(stage, script, "button_exit")
    handlers.button_to_view(
        stage, script, "button_new_message", "email/speller_message_subject")
    handlers.button_to_view(stage, script, "button_back", "email/main")


def prepare_inbox_view(app, script, data):
    handlers.button_to_view(app, script, "button_exit")
    handlers.button_to_view(
        app, script, "button_new_message", "email/speller_message_subject")
    handlers.button_to_view(app, script, "button_back", "email/main")
    data_source = script.get_object("data_source")
    data_source.item_handler = lambda tile, message_preview: \
        app.load_view(
            "email/single_message",
            {
                "message_uid": message_preview["UID"],
                "message_source": app.box.imap_client.get_message_from_inbox,
                "previous_view": "inbox"
            }
        )
    data_source.data = app.box.imap_client.get_inbox_list()[::-1]


def prepare_sent_view(stage, script, data):
    handlers.button_to_view(stage, script, "button_exit")
    handlers.button_to_view(
        stage, script, "button_new_message", "email/speller_message_subject")
    handlers.button_to_view(stage, script, "button_back", "email/main")
    data_source = script.get_object("data_source")
    data_source.item_handler = lambda tile, message_preview: \
        app.load_view(
            "email/single_message",
            {
                "message_uid": message_preview["UID"],
                "message_source": app.box.imap_client.get_message_from_sent_box,
                "previous_view": "sent"
            }
        )
    data_source.data = app.box.imap_client.get_sent_box_list()[::-1]


def prepare_speller_message_body_view(stage, script, data):
    handlers.button_to_view(stage, script, "button_exit")
    handlers.button_to_view(stage, script, "button_proceed",
                    "email/address_book", {"pick_recipients_mode": True})


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
            app.box["new_message"].recipients = contact.address
        else:
            app.box["new_message"].remove_recipient(contact.address)

    handlers.button_to_view(app, script, "button_exit")
    handlers.button_to_view(app, script, "button_back", "email/main")
    data_source = script.get_object("data_source")

    if data and data.get("pick_recipients_mode"):
        specific_button= app.ui.button_send_message
        tile_handler = lambda tile, contact: on_contact_select(tile, contact)
        handlers.button_to_view(app, script,
                                "button_send_message", "email/sent")
    else:
        specific_button = app.ui.button_new_contact
        tile_handler = lambda tile, contact: app.load_view(
            "email/contact", {"contact_id": contact.id})
        handlers.button_to_view(
            app, script, "button_new_contact", "email/contact")

    app.ui.button_menu_box.replace_child(app.ui.button_specific, specific_button)
    data_source.item_handler = tile_handler


def prepare_contact_view(app, script, data):
    handlers.button_to_view(app, script, "button_exit")
    handlers.button_to_view(app, script, "button_back", "email/main")

    if data:
        try:
            contact = app.box["address_book"].get_contact(data["contact_id"])
        except  address_book.AddressBookError as e:
            pass
        else:
            if contact:
                app.ui.contact_address_text.set_text(contact.address)
                if contact.name:
                    app.ui.contact_name_text.set_text(contact.name)
                if contact.photo:
                    try:
                        app.ui.photo.set_from_file(contact.photo)
                    except GObject.GError as e:
                        _LOG.error(e)

                def add_recipient():
                    app.box["new_message"].recipients = contact.address

                handlers.button_to_view(script, "button_create_message", add_recipient)
                handlers.button_to_view(app, script, "button_create_message",
                             "email/speller_message_subject")
                handlers.button_to_view(app, script, "button_edit_name",
                            "email/speller_contact_name", {"contact": contact})
                handlers.button_to_view(app, script, "button_edit_address",
                            "email/speller_contact_address", {"contact": contact})
                handlers.button_to_view(app, script, "button_edit_photo",
                            "email/viewer_contact_library", {"contact": contact})


def prepare_speller_contact_name_view(app, script, data):
    contact = data["contact"]

    def edit_contact_name():
        try:
            app.box["address_book"].edit_contact_name(
                contact.id, app.ui.text_box.get_text())
        except  address_book.AddressBookError as e:
            pass

    handlers.button_to_view(app, script, "button_exit")
    handlers.connect_button(script, "button_proceed", edit_contact_name)
    handlers.button_to_view(app, script, "button_proceed", "email/contact",
                            "contact_id": contact.id})
    if contact.name:
        app.ui.text_box.set_text(contact.name)


def prepare_speller_contact_address_view(stage, script, data):
    contact = data["contact"]

     def edit_contact_address():
         try:
            app.box["address_book"].edit_contact_address(
                contact.id, app.ui.text_box.get_text())
        except  address_book.AddressBookError as e:
            pass

    handlers.button_to_view(stage, script, "button_exit")
    handlers.connect_button(script, "button_proceed", edit_contact_address)
    handlers.button_to_view(stage, script, "button_proceed", "email/contact",
                            {"contact_id": contact.id})
    app.ui.text_box.set_text(contact.address)


def prepare_viewer_contact_library_view(stage, script, data):
    handlers.button_to_view(stage, script, "button_exit")
    handlers.button_to_view(stage, script, "button_back", "email/contact",
                            {"contact_id": data["contact"].id})
    tile_source = script.get_object("library_data")
    tile_source.item_handler = lambda tile, album: stage.load_view(
        "email/viewer_contact_album", {"album_id": album, "contact": data["contact"]})


def prepare_viewer_contact_album_view(app, script, data):
    contact = data["contact"]
    handlers.button_to_view(app, script, "button_exit")
    handlers.button_to_view(
        app, script, "button_library", "email/viewer_contact_library", {"contact": contact})
    album_id = data["album_id"]
    library = model.get_library()
    header = script.get_object("header")
    header.set_text(library.get_category_by_id(album_id).name)
    data_source = script.get_object("album_data")

    def photo_tile_handler(tile, photo_id, album_id):
        try:
            app.box["address_book"].edit_contact_photo(
                contact.id, library.get_item_by_id(photo_id))
        except address_book.AddressBookError as e:
            pass
        app.load_view("email/contact")

    data_source.item_handler = photo_tile_handler
    data_source.data_set_id = album_id


def prepare_single_message_view(app, script, data):
    handlers.button_to_view(app, script, "button_exit")
    handlers.button_to_view(app, script,
                            "button_back", "email/{}".format(data["previous_view"]))
    message = data["message_source"](data["message_uid"])
    app.ui.message_subject.set_text(message["Subject"])
    app.ui.from_content.set_text(
        "; ".join([record[1] for record in message["From"]]))
    app.ui.to_content.set_text(
        ";\n".join([record[1] for record in message["To"]]))
    app.ui.date_content.set_text(str(message["Date"]))
    if "Body" in message:
        app.ui.message_body.set_text(message["Body"])




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
