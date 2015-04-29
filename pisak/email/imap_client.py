"""
Module providing access to the email account through the imap client.
"""
import socket
import imaplib

from pisak import logger
from pisak.email import config


_LOG = logger.getLogger(__name__)


class IMAPClientError(Exception):
    pass


class IMAPClient(object):
    """
    Class representing an email account connection. Used access protocol - IMAP.
    """
    def __init__(self):
        self.encoding = "utf-8"
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
    def _find_mailboxes(self):
        _ret, mailboxes_data = self._conn.list()
        for mailbox in mailboxes_data:
            str_spec = str(mailbox, self.encoding)
            if "sent" in str_spec.lower():
                self.sent_box_name = str_spec.split()[-1].split('"')[1]

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

    @imap_errors_handler
    def _get_mailbox_status(self, mailbox):
        _ret, status_data = self._conn.status(mailbox, "(MESSAGES UNSEEN)")
        status = str(status_data[0], self.encoding)
        return int(status[status.find("MESSAGES") : ].split()[1]), \
               int(status[status.find("UNSEEN") : ].split()[1].rstrip(")"))

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
