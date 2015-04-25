import smtplib
import socket
from ssl import SSLError
from email.mime.text import MIMEText
from email.message import Message
from email.header import Header

from pisak import logger
from pisak.email import config


_LOG = logger.getLogger(__name__)


class  EmailSendingError(Exception):
    pass


class SimpleMessage(object):

    def __init__(self):
        self.charset = "utf-8"
        self.recipents = []
        self.body = ""
        self.subject = ""

    def _add_recipents(self, msg):
        """
        Add recipents to the message.

        :param msg: internal message object
        """
        if len(self.recipents) > 0:
            msg["To"] = Header(",".join(self.recipents), self.charset)
        else:
            e = "No recipents of the new message specified."
            _LOG.error(e)
            raise EmailSendingError(e)

    def _add_subject(self, msg):
        """
        Set subject of the message.

        :param msg: internal message object
        """
        msg["Subject"] = Header(self.subject, self.charset)

    def _create_body(self):
        """
        Create new simple message and add its body.
        """
        # only plain text, not any markups:
        return MIMEText(self.body, "plain", self.charset)

    def _compose_message(self):
        """
        Compose a message object from all the stored data.

        :returns: fully prepared message object for internal use
        """
        msg = self._create_body()
        self._add_subject(msg)
        self._add_recipents(msg)
        return msg

    def send(self):
        """
        Send the message through the SMTP.
        """
        msg = self._compose_message()
        setup = config.get_account_setup()
        server_out = "smtp.{}:{}".format(
                setup["server_address"], setup["port_out"])
        try:
            server = smtplib.SMTP(server_out)
            server.ehlo_or_helo_if_needed()
            if server.has_extn("STARTTLS"):
                server.starttls(keyfile=setup.get("keyfile"), certfile=setup.get("certfile"))
            else:
                _LOG.warning("Server does not support STARTTLS.")
            server.ehlo_or_helo_if_needed()
            server.login(setup["user_address"], setup["password"])
            server.sendmail(setup["user_address"], self.recipents, msg.as_string())
            server.quit()
            _LOG.debug("Email was sent successfully.")
            return True
        except (socket.error, smtplib.SMTPException, SSLError) as e:
            _LOG.error(e)
            raise EmailSendingError(e)

    def clear(self):
        """
        Clear the whole message, all headers etc
        and start creating a new one from the very beginning.
        """
        self.recipents = []
        self.body = ""
        self.subject = ""

    def get_pretty(self):
        """
        Compose a prettyfied version of the message that can be saved in a
        human-readable shape, for example as a draft message.

        :returns: dictionary containing all the separate message fields.
        """
        return {
            "recipents": self.recipents,
            "subject": self.subject,
            "body": self.body
        }