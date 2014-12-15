from multiprocessing import Pool
from Queue import Queue
from analysis import gather_data
import os
import graphics
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


def gather_datas(files):
    global pool, data_queue

    for filename in files:
        results = pool.apply_async(gather_data, (filename,))
    return results


def queue():
    global song_info, player, data_queue, thread_queue, files, i

    while i < len(files):
        print "Yielding next song {0}".format(files[0])
        yield Song(files[i])
        i += 1
    graphics.exit()


def peekQueue(n):
    global files, i

    nexti = i + 1
    if nexti >= len(files):
        return None
    return map(Song, (files[nexti:] + files[:nexti])[:n])


def ffwd():
    global data_queue, player, results

    player.playing = False
    song_info = gather_data(files[i])
    print "Got new song info"

    graphics.reset_globals(ffwd, **song_info)
    player.playing = True


def play(file_list, mesh):
    global pool, data_queue, player, files, i, results

    i = 0

    files = file_list
    print files
    player = musicplayer.createPlayer()
    player.queue = queue()
    player.peekQueue = peekQueue

    song_info = gather_data(files[0])

    graphics.initialize(player, mesh, ffwd, **song_info)
    graphics.setup()
    player.playing = True
    graphics.run()
