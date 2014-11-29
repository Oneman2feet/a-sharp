from __future__ import division
from sphere import Sphere
import graphics
import argparse
import librosa
import musicplayer


def load_song(filename, d):
    print "About to load sound file %s" % filename
    y, sr = librosa.load(filename, duration=d)
    print "Successfully loaded file."
    return y, sr


def separate_fg_and_bg(y):
    return librosa.effects.hpss(y)


def frames_to_time(beat_frame):
    return librosa.frames_to_time(beat_frame, sr=sr, hop_length=hop_length)


def beat_track(y_perc):
    return librosa.beat.beat_track(y=y_perc, sr=sr, hop_length=hop_length)


class Song(object):
    def __init__(self, fn):
        self.url = fn
        self.f = open(fn)

    def __eq__(self, other):
        return self.url == other.url

    def readPacket(self, bufSize):
        return self.f.read(bufSize)

    def seekRaw(self, offset, whence):
        self.f.seek(offset, whence)
        return self.f.tell()


def queue(filename):
        while True:
            yield Song(filename)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process a sound file.')
    parser.add_argument('filename', type=str, help='the path to the sound file')
    parser.add_argument('-d', dest='duration', type=float, help='specify the duration of the sound file to be analyzed')
    args = parser.parse_args()

    y, sr = load_song(args.filename, args.duration)
    y_harmonic, y_percussive = separate_fg_and_bg(y)

    print "Separated FG and BG"

    hop_length = 64

    # Beat track on the percussive signal
    tempo, beat_frames = beat_track(y=y_percussive)

    print "Calculated beat frames"

    beat_times = [0] + [frames_to_time(frame) for frame in beat_frames]
    player = musicplayer.createPlayer()
    sphere = Sphere(100, 100)

    graphics.initialize(player, beat_times, sphere)
    graphics.setup()

    raw_input("Analysis complete. Press Enter to continue...\n")

    player.queue = queue(args.filename)
    # player.playing = True
    graphics.run()
