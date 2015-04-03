"""
Email application main module.
"""
from pisak import launcher, handlers

from pisak.email import address_book  #@UnusedImport


def prepare_main_view(stage, script, data):
    handlers.button_to_view(stage, script, "button_exit")
    handlers.button_to_view(stage, script, "button_inbox", "email/inbox")
    handlers.button_to_view(stage, script, "button_sent", "email/sent")
    handlers.button_to_view(stage, script, "button_drafts", "email/drafts")
    handlers.button_to_view(
        stage, script, "button_address_book", "email/address_book")
    handlers.button_to_view(
        stage, script, "button_new_message", "email/speller_message_to")


def prepare_drafts_view(stage, script, data):
    pass


def prepare_inbox_view(stage, script, data):
    pass


def prepare_sent_view(stage, script, data):
    pass


def prepare_speller_message_content_view(stage, script, data):
    pass


def prepare_speller_message_subject_view(stage, script, data):
    pass


def prepare_speller_message_to_view(stage, script, data):
    pass


def prepare_address_book_view(stage, script, data):
    pass


if __name__ == "__main__":
    email_app = {
        "app": "email",
        "type": "clutter",
        "views": [
            ("main", prepare_main_view),
            ("drafts", prepare_drafts_view),
            ("inbox", prepare_inbox_view),
            ("sent", prepare_sent_view),
            ("address_book", prepare_address_book_view),
            ("speller_message_content", prepare_speller_message_content_view),
            ("speller_message_to", prepare_speller_message_to_view),
            ("speller_message_subject", prepare_speller_message_subject_view)
        ]
    }
    launcher.run(email_app)