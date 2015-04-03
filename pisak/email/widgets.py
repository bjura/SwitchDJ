from pisak import pager, widgets


class AddressTileSource(pager.DataSource):
    """
    Data source that provides tiles representing different addresses
    from the address book.
    """
    __gtype_name__ = "PisakEmailAddressTileSource"

    def __init__(self):
        super().__init__()

    def _produce_item(self, address):
        tile = widgets.PhotoTile()
        self._prepare_item(tile)
        tile.style_class = "PisakEmailAddressTile"
        tile.hilite_tool = widgets.Aperture()
        tile.connect("clicked", self.item_handler, address)
        tile.label_text = address
        return tile