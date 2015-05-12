'''
Module handles cursor-style (stream of coordinates) input in JSON layout.
'''
import threading
import time

from gi.repository import GObject, Clutter
import sys

import pisak
from pisak import logger
from pisak.libs import scanning, configurator, layout, unit

_LOG = logger.getLogger(__name__)


class Sprite(layout.Bin, configurator.Configurable):
    __gtype_name__ = "PisakSprite"

    __gproperties__ = {
        "timeout": (
            GObject.TYPE_UINT,
            "", "",
            0, GObject.G_MAXUINT, 1600,
            GObject.PARAM_READWRITE),
        "locked": (
            GObject.TYPE_BOOLEAN,
            "", "",
            False,
            GObject.PARAM_READWRITE)
    }
    
    def __init__(self, container=None):
        super().__init__()
        self.container = container or self
        self.timeout = 1000
        self.locked = False
        self._init_sprite()
        self.clickables = None
        self.hover_start = None
        self.hover_actor = None
        self.coords = (0, 0)
        self.apply_props()
        self.set_x_expand(True)
        self.set_y_expand(True)
        self.container.connect("allocation-changed", self._rescan)
        self.worker = threading.Thread(target=self.work, daemon=True)
        self.worker.start()

    def _init_sprite(self):
        self.sprite = Clutter.Actor()
        self.sprite.set_size(20, 20)
        self.sprite.set_background_color(Clutter.Color.new(255, 255, 0, 255))
        self.sprite.set_depth(100)
        self.add_actor(self.sprite)

    @property
    def timeout(self):
        return self._timeout * 1000
    
    @timeout.setter
    def timeout(self, value):
        self._timeout = int(value) / 1000
    
    @property
    def locked(self):
        return self._locked
    
    @locked.setter
    def locked(self, value):
        self._locked = value
    
    def read_coords(self):
        line = pisak.input_process.stdout.readline()
        line = line.decode('utf-8')
        try:
            fields = line.split(" ")
            if fields[0] == "gaze_pos:" and '-' not in fields[1] and '-' not in fields[2]:
                coords = float(fields[1].strip()) * unit.size_pix.width, float(fields[2].strip()) * unit.size_pix.height
                coords = int(coords[0]), int(coords[1])
                self.coords = coords
            return self.coords
        except:
            raise Exception("Protocol error")
    
    def update_sprite(self, coords):
        x, y = (coords[0] - self.sprite.get_width() / 2), (coords[1] - self.sprite.get_height() / 2)
        self.sprite.set_position(x, y)
    
    def _rescan(self, source, *args):
        self.clickables = None

    def scan_clickables(self):
        to_scan = self.container.get_children()
        clickables = []
        while len(to_scan) > 0:
            current = to_scan.pop()
            if isinstance(current, scanning.Scannable):
                clickables.append(current)
            to_scan = to_scan + current.get_children()
        self.clickables = clickables
        _LOG.debug("clickables: {}".format(clickables))
    
    def find_actor(self, coords):
        if self.clickables is None:
            self.scan_clickables()
        for clickable in self.clickables:
            (x, y), (w, h) = clickable.get_transformed_position(), clickable.get_size()
            if (x <= coords[0]) and (coords[0] <= x + w) \
                    and (y <= coords[1]) and (coords[1] <= y + h):
                return clickable
        return None

    def on_new_coords(self, x, y):
        coords = (x, y)
        self.update_sprite(coords)
        actor = self.find_actor(coords)
        if actor is not None:
            if actor == self.hover_actor:
                if time.time() - self.hover_start > self._timeout:
                    actor.emit("clicked")
                    self.hover_start = time.time() + 1.0 # dead time
            else:
                # reset timeout
                if self.hover_actor is not None:
                    self.hover_actor.set_style_pseudo_class("")
                self.hover_actor = actor
                self.hover_actor.set_style_pseudo_class("hover")
                self.hover_start = time.time()
        else:
            if self.hover_actor is not None:
                self.hover_actor.set_style_pseudo_class("")
                self.hover_actor = None

    def work(self):
        while True:
            x, y = self.read_coords()
            Clutter.threads_add_idle(900, self.on_new_coords, x, y)
            time.sleep(0.01)
