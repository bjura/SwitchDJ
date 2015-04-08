"""
Email application main module.
"""
from pisak import launcher, handlers

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


def prepare_inbox_view(stage, script, data):
    handlers.button_to_view(stage, script, "button_exit")


def prepare_sent_view(stage, script, data):
    handlers.button_to_view(stage, script, "button_exit")


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


def prepare_contact_view(stage, script, data):
    handlers.button_to_view(stage, script, "button_exit")


def prepare_speller_contact_name_view(stage, script, data):
    handlers.button_to_view(stage, script, "button_exit")


def prepare_speller_contact_address_view(stage, script, data):
    handlers.button_to_view(stage, script, "button_exit")


def prepare_viewer_contact_library_view(stage, script, data):
    handlers.button_to_view(stage, script, "button_exit")


def prepare_viewer_contact_album_view(stage, script, data):
    handlers.button_to_view(stage, script, "button_exit")


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