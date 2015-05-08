"""
Email application specific signal handlers.
"""
from pisak import signals


@signals.registered_handler("email/new_message_add_subject")
def add_subject(text_box, app):
    app.box["new_message"].subject = text_box.get_text()


@signals.registered_handler("email/new_message_add_body")
def add_body(text_box, app):
    app.box["new_message"].body = text_box.get_text()


@signals.registered_handler("email/new_message_send")
def send(source, app):
    app.box["new_message"].send()
    app.box["new_message"].clear()
