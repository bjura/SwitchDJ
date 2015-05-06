import smtplib
import socket
from ssl import SSLError
from email.mime.text import MIMEText
from email.header import Header

from pisak import logger
from pisak.email import config


_LOG = logger.getLogger(__name__)


class  EmailSendingError(Exception):
    pass


class SimpleMessage(object):

    def __init__(self):
        self.charset = "utf-8"
        self._msg = {
            "recipients": set(),
            "body": "",
            "subject": ""
        }

    @property
    def body(self):
        """
        Body of the message. Body should be a single string
        containing only plain text without any markup.
        """
        return self._msg["body"]

    @body.setter
    def body(self, value):
        assert isinstance(value, str), "Body of an email message should be a string."
        self._msg["body"] = value

    @property
    def subject(self):
        """
        Subject of the message. Subject should be a single string.
        """
        return self._msg["subject"]

    @subject.setter
    def subject(self, value):
        assert isinstance(value, str), "Subject of an email message should be a string."
        self._msg["subject"] = value

    @property
    def recipients(self):
        """
        Recipients of the message. Recipients are stored as a
        set of unique email addresses. New recipients  can be added by setting
        this property with either a single address in a string format or
        with a list of many addresses.
        Each new address will be added to the existing set of recipients.
        Before adding to the set each address is examined and if any of them
        is not correct then ValueError is raised.
        Remove recipients using the `remove_recipient` method.
        """
        return self._msg["recipients"]

    @recipients.setter
    def recipients(self, value):
        assert isinstance(value, str) or isinstance(value, list), \
            "Recipients can be given as a single string or a list of many strings."
        if isinstance(value, str):
            value = [value]
        for address in value:
            if self._validate_address(address):
                self._msg["recipients"].add(address)
            else:
                raise ValueError("Invalid email address: {}.".format(address))

    def _validate_address(self, address):
        return address.count("@") == 1 and "." in address \
               and address.rindex(".") > address.index("@")

    def remove_recipient(self, recipient):
        """
        Remove recipient from the collection of all recipients. All removings should
        be performed by using this method.

        :param recipient: recipient to be removed.
        """
        if recipient in self._msg["recipients"]:
            self._msg["recipients"].remove(recipient)
        else:
            _LOG.warning("Trying to remove not existing recipient: {}.".format(
                recipient))

    def _compose_message(self):
        """
        Compose a message object from all the stored data.

        :returns: fully prepared message object for internal use
        """
        def create_body(self):
            """
            Create new simple message and add its body.
            """
            # only plain text, without any markups:
            return MIMEText(self._msg["body"], "plain", self.charset)

        def add_recipients(self):
            """
            Add recipients to the message.
            """
            msg["To"] = Header(",".join(self._msg["recipients"]), self.charset)

        def add_subject(self):
            """
            Set subject of the message.
            """
            msg["Subject"] = Header(self._msg["subject"], self.charset)

        msg = create_body(self)
        add_subject(self)
        add_recipients(self)
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
            server.sendmail(setup["user_address"], self.recipients, msg.as_string())
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
        self._msg = {
            "recipients": set(),
            "body": "",
            "subject": ""
        }

    def get_pretty(self):
        """
        Compose a prettyfied version of the message that can be saved in a
        human-readable shape, for example as a draft message.

        :returns: dictionary containing all the separate message fields.
        """
        return self._msg