from __future__ import division
from sphere import Sphere
from analysis import gather_data
from Queue import Queue
from threading import Thread
import os
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


def gather_datas(file_list):
    global data_queue, thread_queue
    for filename in file_list:
        t = Thread(target=gather_data, args=(filename, data_queue))
        thread_queue.put(t)
        t.start()


def queue(file_list):
    global song_info, player, data_queue, thread_queue
    yield Song(file_list.pop(0))
    while file_list:
        t = thread_queue.get()
        print "Loading next song"
        t.join()
        song_info = data_queue.get()
        graphics.initialize(player, sphere, **song_info)
        song = Song(file_list.pop(0))
        yield song
        print "About to pause player"
        player.playing = False
        print "Getting new song info"


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process a sound file.')
    parser.add_argument('dirname', type=str, help='the path to the sound file')
    parser.add_argument('-d', dest='duration', type=float, help='specify the duration of the sound file to be analyzed')
    args = parser.parse_args()
    framerate = 0.1  # change this to adjust video and audio analysis fr
    file_list = [args.dirname + f for f in os.listdir(args.dirname)]

    data_queue = Queue()
    gather_data(file_list.pop(0), data_queue)
    song_info = data_queue.get()

    thread_queue = Queue()
    gather_datas(file_list)

    player = musicplayer.createPlayer()
    sphere = Sphere(100, 100)

    graphics.initialize(player, sphere, **song_info)
    graphics.setup()

    raw_input("Analysis complete. Press Enter to continue...\n")

    player.queue = queue(file_list)
    player.playing = True
    graphics.run()
