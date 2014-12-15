from threading import Thread
from Queue import Queue
from analysis import gather_data
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
    global thread_queue, data_queue

    for filename in files:
        t = Thread(target=gather_data, args=(filename, data_queue))
        thread_queue.put(t)
        t.start()


def queue():
    global song_info, player, data_queue, thread_queue, files, i

    while True:
        print "Yielding next song {0}".format(files[0])
        yield Song(files[i])
        i += 1
        if i == len(files): graphics.exit()


def peekQueue(n):
    global files, i

    nexti = i + 1
    if nexti >= len(files): nexti = 0
    return map(Song, (files[nexti:] + files[:nexti])[:n])


def ffwd():
    print "Called FFWD"
    global thread_queue, data_queue, player

    t = thread_queue.get()
    t.join()
    song_info = data_queue.get()
    print "Got new song info"

    print "Player {0} playing".format(player.playing)
    graphics.reset_globals(ffwd, **song_info)


def play(file_list, mesh):
    global thread_queue, data_queue, player, files, i

    i = 0

    files = file_list
    data_queue = Queue()
    thread_queue = Queue()
    player = musicplayer.createPlayer()
    player.queue = queue()
    player.peekQueue = peekQueue
    # player.onSongChange = ffwd

    gather_datas(files)

    t = thread_queue.get()
    t.join()
    song_info = data_queue.get()

    graphics.initialize(player, mesh, ffwd, **song_info)
    graphics.setup()
    player.playing = True
    graphics.run()
