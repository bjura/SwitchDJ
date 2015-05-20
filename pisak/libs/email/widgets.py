from pisak.libs import pager, widgets

from pisak.libs.email import address_book


class AddressTileSource(pager.DataSource):
    """
    Data source that provides tiles representing different addresses
    from the address book.
    """
    __gtype_name__ = "PisakEmailAddressTileSource"

    def __init__(self):
        super().__init__()

    def _produce_item(self, contact):
        tile = widgets.PhotoTile()
        self._prepare_item(tile)
        frame = widgets.Frame()
        frame.set_x_expand(False)
        frame.set_y_expand(False)
        frame.set_size(*tile.get_size())
        tile.add_frame(frame)
        tile.style_class = "PisakEmailAddressTile"
        tile.hilite_tool = widgets.Aperture()
        tile.connect("clicked", self.item_handler, contact)
        tile.label_text = contact.name if contact.name else contact.address
        if contact.photo:
            tile.preview_path = contact.photo
        return tile


class InboxTileSource(pager.DataSource):
    """
    Data source that provides tiles representing messages in the inbox folder.
    """
    __gtype_name__ = "PisakEmailInboxTileSource"

    def __init__(self):
        super().__init__()

    def _produce_item(self, message):
        tile = widgets.PhotoTile()
        self._prepare_item(tile)
        frame = widgets.Frame()
        tile.add_frame(frame)
        tile.style_class = "PisakEmailInboxTile"
        tile.hilite_tool = widgets.Aperture()
        tile.connect("clicked", self.item_handler, message)
        tile.label_text = "\n\n".join(
            [message["From"][1], message["Subject"], str(message["Date"])])
        return tile


class SentTileSource(pager.DataSource):
    """
    Data source that provides tiles representing messages in the sent folder.
    """
    __gtype_name__ = "PisakEmailSentTileSource"

    def __init__(self):
        super().__init__()

    def _produce_item(self, message):
        tile = widgets.PhotoTile()
        self._prepare_item(tile)
        frame = widgets.Frame()
        tile.add_frame(frame)
        tile.style_class = "PisakEmailSentTile"
        tile.hilite_tool = widgets.Aperture()
        tile.connect("clicked", self.item_handler, message)
        tile.label_text = "\n\n".join(
            [message["To"][1], message["Subject"], str(message["Date"])])
        return tile


class DraftsTileSource(pager.DataSource):
    """
    Data source that provides tiles representing messages in the drafts folder.
    """
    __gtype_name__ = "PisakEmailDraftsTileSource"

    def __init__(self):
        super().__init__()

    def _produce_item(self, message):
        tile = widgets.PhotoTile()
        self._prepare_item(tile)
        tile.style_class = "PisakEmailDraftsTile"
        tile.hilite_tool = widgets.Aperture()
        tile.connect("clicked", self.item_handler, message)
        return tile
