"""
Compose and play music using a binary-choice switch.



Notes or just some TODOs:

- all the sounds displayed in GUI should be ordered properly.
- each sound should be labeled.
- picked sounds should be displayed properly.
- composed tracks should be displayed below each other.
- playing sounds while scanning them should be optional.
- type of sounds to be displayed should be switchable easly.
- current type of sounds should be labeled with an icon.
- it should be possible to play a current song at all times - after each new sound th song should be mixed.
- currently edited track should be switchable easly.
- erase, pop and modify sounds on each track.
- autosave after each new modification.

(GAME IDEA:
    play sounds - different types and different tones - and player has to find the correct one;
    display type and tone or a symbol of the sound and player has to play or react to the correct one.)
"""
import os
import subprocess

from pisak import res


BACKEND = 'pydub'

PLAYER = "avplay"


#------------------------------------------------

# -----   backend specific stuff ---------------


# PYDUB:

if BACKEND == 'pydub':

    import pydub


    def get_empty_segment():
        return pydub.AudioSegment.empty()

    def get_silent_segment(duration):
        return pydub.AudioSegment.silent(duration)

    def get_wav_segment(filename):
        return pydub.AudioSegment.from_wav(filename)

    def concatenate_segments(seg1, seg2):
        return seg1 + seg2

    def overlay_segment(base, overlaid, looped, delay):
        return base.overlay(overlaid, loop=looped, position=delay)

    def get_segment_duration(segment):
        return len(segment)

    def save_segment(segment, filename):
        segment.export(filename)


#-------------------------------------------


class Player:
    def __init__(self):
        self._engine = PLAYER

    def play_audio_segment(self, audio_segment):
        assert isinstance(audio_segment, AudioSegment), "Arg should be an `AudioSegment` instance."
        self._play(audio_segment.filename)

    def _play(self, filename):
        subprocess.Popen([self._engine, filename])


class AudioSegment:
    def __init__(self):
        self._player = Player()
        self.filename = None
        self.segment = None

    def save(self, filename):
        save_segment(self.segment, filename)

    def play(self):
        if not os.path.isfile(self.filename):
            self.save(self.filename)
        self._player.play_audio_segment(self)


class Sound(AudioSegment):
    """
    Base class for all kinds of sounds.

    TODO: adjust duration, tone ... of the sound.

    :param filename: name of audio file in wav format.
    """
    def __init__(self, filename, name):
        super().__init__()

        self.filename = filename

        self.segment = get_wav_segment(filename)

        # name of the sound
        self.name = name


class NaturalSound(Sound):
    """
    Base class for all the natural sound, e.g. animals, natural forces, etc...
    """
    ...


class InstrumentalSound(Sound):
    """
    Base class for all the instrumental sounds.
    """
    ...


class PianoSound(InstrumentalSound):
    ...


class AcusticGuitarSound(InstrumentalSound):
    ...


class ElectricGuitarSound(InstrumentalSound):
    ...



class Repeater(AudioSegment):
    def __init__(self, sound):
        self.sound = sound

        self.segment = None

        # how many times the sound should be repeated
        self.count = 2

        # interval between consecutive repetitions, in miliseconds
        self.interval = 1000

        self._create()

    def _create(self):
        self.segment = get_empty_segment()
        for rep in range(self.count):
            self.segment = concatenate_segments(self.segment, self.sound.segment)
            if rep < self.count - 1:
                self.segment = concatenate_segments(self.segment, get_silent_segment(self.interval))



class Track(AudioSegment):
    def __init__(self):
        # temp filename
        self.filename = os.path.join(os.path.expanduser('~'),
                                          "switch_DJ_temp_track.wav")

        # delay before the track starts playing, in miliseconds
        self.delay = 0

        # if the track should be looped
        self.looped = False

        self._content = []
        self.segment = get_empty_segment()

    def add_sound(self, sound):
        assert isinstance(sound, Sound), "Arg should be a `Sound` instance."
        self._content.append(sound)
        self._concatenate_segment(sound.segment)

    def add_repeater(self, repeater):
        assert isinstance(repeater, Repeater), "Arg should be a `Repeater` instance."
        self._content.append(repeater)
        self._concatenate_segment(repeater.segment)

    def _contatenate_segment(self, segment):
        concatenate_segments(self.segment, segment)


class Song(AudioSegment):
    def __init__(self):
        self.filename = None
        self._tracks = []
        self.segment = get_empty_segment()

    def add_track(self, track):
        assert isinstance(track, Track), "Song can be composed of the `Track` instances only."
        self._tracks.append(track)

    def _mix_track(self, track):
        self.segment = overlay_segment(
            self.segment, track.segment, track.looped, track.delay)

    def _mix(self):
        """
        Mix all the ingredients in order to create a song.
        """
        # sort from the longest to the shortest as overlaid tracks are truncated
        self._tracks.sort(key=lambda track: get_segment_duration(track.segment)).reverse()
        for track in self._tracks:
            self._mix_track(track)

    def get_duration(self):
        """
        Get duration of the song.
        """
        return get_segment_duration(self.segment)

    def done(self):
        """
        When the song is ready, let's put all the pieces together.
        """
        self._mix()


class SoundPool:
    """
    Pool of avalaible sounds of the given type. Sounds should be ordered according to their tones.
    """
    def __init__(self, category, sound_type):
        self.sound_type = sound_type
        self.category = category
        self.sounds = []
        self._generate_sounds()

    def _generate_sounds(self):
        loc = res.get(os.path.join("sounds", "dj", self.category))
        for file in os.listdir(loc):
            self.sounds.append(self.sound_type(os.path.join(loc, file),
                                               os.path.stripext(file)[0]))