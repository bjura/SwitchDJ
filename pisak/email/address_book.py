import configobj

from pisak import text_tools, logger, res


_LOG = logger.getLogger(__name__)


EMAIL_ADDRESS_BOOK = res.get("email_address_book.ini")


class AddressBook(text_tools.Predictor):
    """
    Book of mail contacts. Serves also as a predictor
    for new message address inserts.
    """
    __gtype_name__ = "PisakEmailAddressBook"

    def __init__(self):
        super().__init__()
        self.book = None
        self.all  = None
        self._load_book()
        self.apply_props()

    def _load_book(self):
        self.book = configobj.ConfigObj(EMAIL_ADDRESS_BOOK, encoding="UTF-8")
        self.all = self.book.get("all") or []

    def _book_lookup(self, feed):
        return [record for record in self.all if record.startswith(feed)]

    def do_prediction(self, text, position):
        feed = text[0 : position]
        self.content = self._book_lookup(feed)
        Clutter.threads_add_idle(0, self.emit, "content-update")

    def add_address(self, address):
        """
        Add address to the book. If already in, then nothing happens.

        :param address: contact email address
        """
        if address not in self.all:
            self.all.append(address)
            self.book["all"] = self.all
            self.book.write()