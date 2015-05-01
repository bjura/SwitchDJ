"""
Module providing access to the email account through the imap client.
"""
import socket
import imaplib
import email

from pisak import logger
from pisak.email import config, parsers


_LOG = logger.getLogger(__name__)


class IMAPClientError(Exception):
    pass


class IMAPClient(object):
    """
    Class representing an email account connection. Used access protocol - IMAP.
    """
    def __init__(self):
        self._conn = None
        self.sent_box_name = None

    def imap_errors_handler(method):
        """
        Decorator. Handles errors related to IMAP server connection.

        :param method: method that should be provided with the error handling
        """
        def handler(*args, **kwargs):
            try:
                return method(*args, **kwargs)
            except (socket.error, imaplib.IMAP4.error) as e:
                _LOG.error(e)
                raise IMAPClientError(e)
        return handler

    @imap_errors_handler
    def login(self):
        setup = config.get_account_setup()
        server_in = "imap.{}".format(setup["server_address"])
        port_in = setup["port_in"]
        if port_in == "993":
            self._conn = imaplib.IMAP4_SSL(server_in, port=port_in,
                                 keyfile=setup.get("keyfile"), certfile=setup.get("certfile"))
        else:
            if port_in != "143":
                msg = "Port {} is not valid for IMAP protocol. Trying through 143."
                _LOG.warning(msg.format(port_in))
                port_in = "143"
            self._conn = imaplib.IMAP4(server_in, port=port_in)
        self._conn.login(setup["user_address"], setup["password"])
        self._find_mailboxes()

    @imap_errors_handler
    def logout(self):
        """
        Logout from the account.
        """
        if self._conn is not None:
            self._conn.close()
            self._conn.logout()
        else:
            _LOG.warning("There is no connection to the email account."
                         "Nowhere to logout from.")

    def get_inbox_status(self):
        """
        Get number of all messages in the inbox and
        number of the unseen messages.

        :returns: tuple with two integers: number of all messages
        and number of unseen messages
        """
        return self._get_mailbox_status("INBOX")

    def get_sent_box_status(self):
        """
        Get number of all messages in the sent box and
        number of the unseen messages.

        :returns: tuple with two integers: number of all messages
        and number of unseen messages
        """
        return self._get_mailbox_status(self.sent_box_name)

    def get_message_from_inbox(self, uid):
        """
        Get message with the given uid from the inbox.

        :param uid: uid of the message.

        :return: dictionary with the message.
        """
        return self._get_message("INBOX", uid)

    def get_inbox_list(self):
        """
        Get list containing previews of all the messages.

        :returns: list of dictionary with message previews.
        Each contain: subject, sender and date.
        """
        return self._get_mailbox_list("INBOX")

    @imap_errors_handler
    def _get_mailbox_list(self, mailbox):
        headers = ["Subject", "From", "Date"]
        self._conn.select(mailbox)
        _ret, uids_data = self._conn.search(None, "ALL")
        uids = uids_data[0].decode(parsers.DEFAULT_CHARSET).split()
        _ret, msg_data = self._conn.fetch(
            ",".join(uids),
            "(BODY.PEEK[HEADER.FIELDS ({})])".format(" ".join(headers).upper()))
        return parsers.parse_mailbox_list(uids, msg_data, headers)

    @imap_errors_handler
    def _find_mailboxes(self):
        _ret, mailboxes_data = self._conn.list()
        for mailbox in mailboxes_data:
            str_spec = mailbox.decode(parsers.DEFAULT_CHARSET)
            if "sent" in str_spec.lower():
                self.sent_box_name = str_spec.split()[-1].split('"')[1]

    @imap_errors_handler
    def _get_message(self, mailbox, uid):
        self._conn.select(mailbox)
        _ret, msg_data = self._conn.fetch(uid, '(RFC822)')
        return parsers.parse_message(
            msg_data[0][1].decode(parsers.DEFAULT_CHARSET))

    @imap_errors_handler
    def _get_mailbox_status(self, mailbox):
        _ret, status_data = self._conn.status(mailbox, "(MESSAGES UNSEEN)")
        status = status_data[0].decode(parsers.DEFAULT_CHARSET)
        return int(status[status.find("MESSAGES") : ].split()[1]), \
               int(status[status.find("UNSEEN") : ].split()[1].rstrip(")"))
