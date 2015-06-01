from pisak.libs import signals


@signals.registered_handler("dj/add_sound")
def add_sound(sound_tile, app):
    app.ui.track_box.add_sound(sound_tile)


@signals.registered_handler("dj/new_track")
def add_track(track_box, app):
    track_box.add_track()


@signals.registered_handler("dj/play")
def play(track_box, app):
    song = app.box["song"]
    for track in track_box.get_tracks():
    	song.add_track(track)
    song.done()
    song.play()
