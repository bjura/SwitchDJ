from gi.repository import GObject

from pisak.libs import layout, widgets
from pisak.libs.dj import core


class Track(layout.Box):
    def __init__(self):
        super().__init__()
        self.set_x_expand(True)
        self.set_y_expand(True)
        self._track = core.Track()
        self.tiles = []

    def add_sound(self, sound_tile):
        self._track.add_sound(sound_tile.sound)
        sound_tile = self._copy_sound_tile(sound_tile)
        self.tiles.append(sound_tile)
        self.add_child(sound_tile)

    def _copy_sound_tile(self, sound_tile):
        style_class = "PisakDJSound"
        tile = SoundTile(sound_tile.sound)
        tile.set_x_expand(True)
        tile.set_y_expand(True)
        frame = widgets.Frame()
        frame.set_style_class(style_class)
        tile.add_child(frame)
        tile.style_class = style_class
        return tile

    def get_track(self):
        return self._track


class TrackBox(layout.Box):
    __gtype_name__ = "PisakDJTrackBox"

    def __init__(self):
        super().__init__()
        self.current_track = None
        self.tracks = []
        self.add_track()

    def add_track(self):
        if self.current_track is None or \
                len(self.current_track.tiles) > 0:
            self.current_track = Track()
            self.tracks.append(self.current_track)
            self.add_child(self.current_track)

    def add_sound(self, sound_tile):
        self.current_track.add_sound(sound_tile)

    def get_tracks(self):
        tracks = []
        for track in self.tracks:
            tracks.append(track.get_track())
        return tracks


class SoundTile(widgets.PhotoTile):
    def __init__(self, sound):
        super().__init__()
        self.sound = sound
        self.label_text = sound.name
        self.hilite_tool = widgets.Aperture()

    def enable_hilite(self):
        super().enable_hilite()
        self.sound.play()


class SoundPoolBox(layout.Box):
    __gtype_name__ = "PisakDJSoundPoolBox"

    __gproperties__ = {
        "target_box": (
            TrackBox.__gtype__, "", "", 
            GObject.PARAM_READWRITE)
    }

    def __init__(self):
        super().__init__()
        self.init_set = ("piano", core.PianoSound)

        self._target_box = None
        self._pool = None
        self.tiles = []
        self.sounds = []
        self.switch_set(*self.init_set)

    @property
    def target_box(self):
        return self._target_box

    @target_box.setter
    def target_box(self, value):
        self._target_box = value

    def switch_set(self, name, sound_type):
        style_class = "PisakDJSound"
        self.tiles.clear()
        self.sounds.clear()
        self.remove_all_children()
        self._pool = core.SoundPool(name, sound_type)
        for sound in self._pool.sounds:
            tile = SoundTile(sound)
            tile.set_x_expand(True)
            tile.set_y_expand(True)
            tile.connect("clicked", self.pick_sound)
            frame = widgets.Frame()
            frame.set_style_class(style_class)
            tile.add_child(frame)
            tile.style_class = style_class
            self.add_child(tile)

            self.tiles.append(tile)
            self.sounds.append(sound)
    
    def pick_sound(self, tile):
        self.target_box.add_sound(tile)
