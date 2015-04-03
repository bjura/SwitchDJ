"""
Module providing access to the email account through the imap client.
"""
import socket
import imaplib

from pisak import logger
from pisak.email import config


LOG = logger.getLogger(__name__)


class IMAPClientError(Exception):
    pass


class IMAPClient(object):
    """
    Class representing an email account connection. Used access protocol - IMAP.
    """
    def __init__(self):
        self._conn = None
        self._login()

    def _login(self):
        setup = config,get_account_setup()
        server_in = "imap.{}".format(setup["server_address"])
        port_in = setup["port_in"]
        try:
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
        except (socket.error, imaplib.IMAP4.error) as msg:
            _LOG.error(msg)
            raise IMAPClient(msg)

    def logout(self):
        """
        Logout from the account.
        """
        if self._conn is not None:
            self._conn.logout()
        else:
            _LOG.warning("There is no connection to the email account."
                         "Nowhere to logout from.")