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
        self._conn = None
        self.sent_box_name = None
        self._login()
        self._find_boxes()

    def imap_errors_handler(method):
        """
        Decorator. Handles errors related to IMAP server connection.

        :param method: method that should be provided with the error handling
        """
        def handler(*args, **kwargs):
            try:
                method(*args, **kwargs)
            except (socket.error, imaplib.IMAP4.error) as e:
                _LOG.error(e)
                raise IMAPClient(e)
        return handler

    @imap_errors_handler
    def _login(self):
        setup = config.get_account_setup()
        server_in = "imap.{}".format(setup["server_address"])
        port_in = setup["port_in"]
        if port_in == 993:
            self._conn = imaplib.IMAP4_SSL(server_in, port=port_in,
                                 keyfile=setup.get("keyfile"), certfile=setup.get("certfile"))
        else:
            if port_in != 143:
                msg = "Port {} is not valid for IMAP protocol. Trying through 143."
                _LOG.warning(msg.format(port_in))
                port_in = 143
            self._conn = imaplib.IMAP4(server_in, port=port_in)
        self._conn.login(setup["user_address"], setup["password"])

    @imap_errors_handler
    def _find_boxes(self):
        for box in self._conn.list()[1]:
            spec, _, name = str(box).split()
            if "sent" in spec.lower() or "sent" in name.lower():
                self.sent_box_name = name.split('"')[1]

    @imap_errors_handler
    def logout(self):
        """
        Logout from the account.
        """
        if self._conn is not None:
            self._conn.logout()
        else:
            _LOG.warning("There is no connection to the email account."
                         "Nowhere to logout from.")