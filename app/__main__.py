from __future__ import division
from sphere import Sphere
from analysis import gather_data
import graphics
import argparse
import musicplayer


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
    framerate = 0.1  # change this to adjust video and audio analysis fr
    song_info = gather_data(args.filename, framerate)

    player = musicplayer.createPlayer()
    sphere = Sphere(100, 100)

    graphics.initialize(player, sphere, framerate, *song_info.values())
    graphics.setup()

    raw_input("Analysis complete. Press Enter to continue...\n")

    player.queue = queue(args.filename)
    # player.playing = True
    graphics.run()
