"""
Email parsers.
"""
import email
import time
from datetime import datetime


DEFAULT_CHARSET = "utf-8"


def decode_message(message):
    """
    Decode content of the message.

    :param message: non-multipart message object.

    :return: decoded content of the message
    """
    content = message.get_payload(decode=True)
    charset = message.get_content_charset(DEFAULT_CHARSET)
    return content.decode(charset)


def get_addresses(message, header):
    """
    Extract all addresses from a header with the given name.

    :params message: message object.
    :param header: header name.

    :returns: list of tuples containing name and address for each record.
    """
    return email.utils.getaddresses(message.get_all(header, []))


def parse_date(raw_date):
    """
    Parse date of the message.

    :param raw_date: raw date string.

    :returns: datetime object or None in case of parsing failure
    """
    date_tuple = email.utils.parsedate(raw_date)
    return datetime.fromtimestamp(time.mktime(date_tuple)) \
            if date_tuple else None


def parse_message(raw_message):
    """
    Parse the given raw message.

    :param raw_message: single string with the whole  raw message.

    :returns: dictionary containing all fields of parsed message.
    """
    parsed_msg = {}
    msg = email.message_from_string(raw_message)
    content_type = msg.get_content_maintype()

    # look for plain text message body
    if content_type == "multipart":
        for part in msg.walk():
            content_type = part.get_content_type()
            is_inline = part.get("Content-Disposition") in (None, "inline")
            if content_type == "text/plain" and is_inline:
                parsed_msg["Body"] = decode_message(part)
    elif content_type == "text/plain":
        parsed_msg["Body"] = decode_message(part)

    # put all the message fields into a dictionary
    parsed_msg.update(msg.items())

    # look for all the addresses
    parsed_msg["To"] = get_addresses(msg, "To")
    parsed_msg["From"] = get_addresses(msg, "From")

    # convert date into datetime object if possible
    date = parse_date(parsed_msg.get("Date"))
    if date:
        parsed_msg["Date"] = date

    return parsed_msg

