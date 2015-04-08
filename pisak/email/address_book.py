import configobj

from pisak import text_tools, logger, dirs


_LOG = logger.getLogger(__name__)


class AddressBook(text_tools.Predictor):
    """
    Book of mail contacts. Serves also as a predictor
    for new message address inserts.
    """
    __gtype_name__ = "PisakEmailAddressBook"

    def __init__(self):
        super().__init__()
        self.book = None
        self._load_book()
        self.basic_content = sorted([contact["address"]
                for contact in self.book.values() if contact.get("address")])
        self.apply_props()

    def add_contact(self, contact):
        """
        Add contact to the book.

        :param contact: contact dictionary with optional 'name',
        'address' and 'photo' keys
        """
        keys = self.book.keys()
        contact_id = str(len(keys))
        while contact_id in keys:
            contact_id = str(int(contact_id + 1))
        self.book[contact_id] = contact
        self.book.write()

    def remove_contact(self, contact_id):
        """
        Remove contact from the book. If the book does not contain
        the given contact then nothing happens.

        :param contact: id of the contact to be removed
        """
        try:
            self.book.pop(contact_id)
            self.book.write()
        except KeyError:
            _LOG.warning("No contact with id {} in the "
                         "address book".format(contact_id))

    def edit_contact_photo(self, contact_id, photo_path):
        """
        Edit photo path for a contact.

        :param contact_id: id of the contact
        :param photo_path: path to the new photo
        """
        self._edit_contact(contact_id, "photo", photo_path)

    def edit_contact_name(self, contact_id, name):
        """
        Edit name of a contact.

        :param contact_id: id of the contact
        :param name: new name
        """
        self._edit_contact(contact_id, "name", name)

    def edit_contact_address(self, contact_id, address):
        """
        Edit email address of a contact.

        :param contact_id: id of the contact
        :param name: new email address
        """
        self._edit_contact(contact_id, "address", address)

    def list_all(self):
        """
        Get all contacts as a list of dictionaries with contact id as one of the keys.

        :returns: list of contact dictionaries
        """
        all = []
        for contact_id, contact in self.book.items():
            contact["id"] = contact_id
            all.append(contact)
        return all

    def _edit_contact(self, contact_id, key, value):
         if self.book.get(contact_id):
            self.book[contact_id][key] = value
            self.book.write()

    def _load_book(self):
        self.book = configobj.ConfigObj(dirs.HOME_EMAIL_ADDRESS_BOOK,
                                        encoding="UTF-8")

    def _book_lookup(self, feed):
        return sorted([contact["address"] for contact in self.book.values()
                if (contact.get("address") and contact["address"].startswith(feed))
                    or (contact.get("name") and contact["name"].startswith(feed))])

    def do_prediction(self, text, position):
        feed = text[0 : position]
        self.content = self._book_lookup(feed)
        self.notify_content_update()