import smtplib
import socket
from ssl import SSLError
from email.mime.text import MIMEText
from email.message import Message
from email.header import Header

from pisak import logger
from pisak.email import config


LOG = logger.getLogger(__name__)


class  EmailSendingError(Exception):
    pass


class SimpleMessage(object):

    def __init__(self):
        self._msg = Message()
        self.recipents = []
        self.charset = "utf-8"

    def add_recipent(self, recipent):
        """
        Add recipent address to the list of all recipents.

        :param recipent: new recipent address
        """
        self._msg["To"] = Header(recipent if not self._msg["To"] else \
            ",".join([self._msg["To"], recipent]), self.charset)
        self.recipents.append(recipent)

    def add_subject(self, subject):
        """
        Set subject of the message.

        :param subject: text subject of the message
        """
        self._msg["Subject"] = Header(subject, self.charset)

    def add_body(self, text):
        """
        Add body of the message.

        :param text: message body as plain text
        """
        body = MIMEText(text, "plain", self.charset)  # only plain text, not any markup
        self._msg.set_payload(body.as_string())

    def send(self):
        """
        Send the message through the SMTP.
        """
        setup = config,get_account_setup()
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
            server.sendmail(setup["user_address"], self.recipents, self._msg.as_string())
            server.quit()
            _LOG.debug("Email was sent successfully.")
            return True
        except (socket.error, smtplib.SMTPException, SSLError) as msg:
            _LOG.error(msg)
            raise EmailSendingError(msg)