from __future__ import division
from math import pi, sin, cos
from shader import Shader
from pyglet.gl import *
import pyglet
import argparse
import librosa
import numpy as np
import time

pyglet.resource.path.append('textures')
pyglet.resource.reindex()

try:
    # Try and create a window with multisampling (antialiasing)
    config = Config(sample_buffers=1, samples=4,
                    depth_size=16, double_buffer=True,)
    window = pyglet.window.Window(resizable=True, config=config)
except pyglet.window.NoSuchConfigException:
    # Fall back to no multisampling for old hardware
    window = pyglet.window.Window(resizable=True)


@window.event
def on_resize(width, height):
    # Override the default on_resize handler to create a 3D projection
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60., width / float(height), .1, 1000.)
    glMatrixMode(GL_MODELVIEW)
    return pyglet.event.EVENT_HANDLED


def update(dt):
    global ry, elapsed_time, bps, bump, bframe
    elapsed_time += dt

    if currSong == len(master):
        pyglet.clock.unschedule(update)
        pyglet.app.exit()
        return

    beat_times = master[currSong]

    next_beat = beat_times[bframe]

    if next_beat - elapsed_time < 0:
        bframe += 1
        if bframe == len(beat_times):
            pyglet.clock.unschedule(update)
            pyglet.app.exit()
            return
        next_beat = beat_times[bframe]

    prev_beat = beat_times[bframe - 1]

    time_since_prev_beat = elapsed_time - prev_beat
    local_spb = next_beat - prev_beat
    bump = abs(local_spb/2 - time_since_prev_beat)**2 * 5

    ry += dt * 80
    ry %= 360
pyglet.clock.schedule(update)


# Define a simple function to create ctypes arrays of floats:
def vec(*args):
    return (GLfloat * len(args))(*args)


@window.event
def on_draw():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glTranslatef(0, 0, -4)
    glRotatef(0, 0, 0, 1)
    glRotatef(ry, 0, 1, 0)
    glRotatef(0, 1, 0, 0)

    glPolygonMode(GL_FRONT, GL_FILL)

    shader.bind()

    shader.uniformf('bump', bump)

    glActiveTexture(GL_TEXTURE0)
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, color_texture.id)
    shader.uniformi('color_texture', 0)
    glActiveTexture(GL_TEXTURE0+1)
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, disp_texture.id)
    shader.uniformi('disp_texture', 1)
    shader.uniformf('dispMagnitude', 0.2)
    glActiveTexture(GL_TEXTURE0+2)
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, disp_texture.id)
    shader.uniformi('normal_texture', 2)
    shader.uniformf('elapsed_time', elapsed_time)
    shader.uniformf('bps', bps)

    sphere.draw()

    glActiveTexture(GL_TEXTURE0+2)
    glDisable(GL_TEXTURE_2D)
    glActiveTexture(GL_TEXTURE0+1)
    glDisable(GL_TEXTURE_2D)
    glActiveTexture(GL_TEXTURE0)
    glDisable(GL_TEXTURE_2D)

    shader.unbind()


def setup():
    # One-time GL setup
    global light0pos
    global light1pos
    global toggletexture
    global color_texture
    global disp_texture
    global shader

    vert_handle = open("DispMapped.vert")
    vert = ["".join([line for line in vert_handle])]
    frag_handle = open("DispMapped.frag")
    frag = ["".join([line for line in frag_handle])]
    shader = Shader(vert, frag)

    glClearColor(1, 1, 1, 1)
    glColor4f(1, 1, 1, 1)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_CULL_FACE)

    # Uncomment this line for a wireframe view
    glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    # Simple light setup.  On Windows GL_LIGHT0 is enabled by default,
    # but this is not the case on Linux or Mac, so remember to always
    # include it.
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)

    color_file = 'bluesphere.jpg'
    print "Loading Texture", color_file
    textureSurface = pyglet.resource.texture(color_file)
    color_texture = textureSurface.get_texture()
    glBindTexture(color_texture.target, color_texture.id)
    print "Color texture bound to ", color_texture.id

    disp_file = 'Texturemap1.jpg'
    print "Loading Texture", disp_file
    textureSurface = pyglet.resource.texture(disp_file)
    disp_texture = textureSurface.get_texture()
    glBindTexture(disp_texture.target, disp_texture.id)
    print "Displacement texture bound to ", disp_texture.id

    normal_file = 'Texturemap2.jpg'
    print "Loading Texture", normal_file
    textureSurface = pyglet.resource.texture(normal_file)
    normal_texture = textureSurface.get_texture()
    glBindTexture(normal_texture.target, normal_texture.id)
    print "Normal texture bound to ", normal_texture.id

    # Uncomment this line for a wireframe view
    # glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    # Simple light setup.  On Windows GL_LIGHT0 is enabled by default,
    # but this is not the case on Linux or Mac, so remember to always
    # include it.
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_LIGHT1)

    light0pos = [5.0, 5.0, 5.0, 1.0]  # positional light !
    light1pos = [-5.0, 5.0, 5.0, 1.0]

    glLightfv(GL_LIGHT0, GL_POSITION, vec(*light0pos))
    glLightfv(GL_LIGHT0, GL_AMBIENT, vec(0.9, 0.9, 0.9, 1.0))
    glLightfv(GL_LIGHT0, GL_DIFFUSE, vec(0.9, 0.9, 0.9, 1.0))
    glLightfv(GL_LIGHT0, GL_SPECULAR, vec(1.0, 1.0, 1.0, 1.0))

    glLightfv(GL_LIGHT1, GL_POSITION, vec(*light1pos))
    glLightfv(GL_LIGHT1, GL_AMBIENT, vec(0.1, 0.1, 0.1, 1.0))
    glLightfv(GL_LIGHT1, GL_DIFFUSE, vec(0.9, 0.9, 0.9, 1.0))
    glLightfv(GL_LIGHT1, GL_SPECULAR, vec(1.0, 1.0, 1.0, 1.0))

    glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE,
                 vec(0.5, 0.5, 0.5, 1.0))
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, vec(1, 1, 1, 1))
    glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 20)


class Sphere(object):
    """docstring for Sphere"""
    def __init__(self, divLong, divLat):
        # Create the vertex and normal arrays.
        positions = []
        normals = []
        uvs = []

        for i in xrange(divLong + 1):
            theta = 2 * pi * i/divLong + pi
            for j in xrange(divLat + 1):
                phi = pi * j / divLat
                z = cos(theta) * sin(phi)
                x = sin(theta) * sin(phi)
                y = cos(phi)

                positions.extend([x, y, z])
                normals.extend([x, y, z])
                uvs.extend([i/divLong, 1-(j/divLat)])
        # Create ctypes arrays of the lists
        positions = vec(*positions)
        normals = vec(*normals)
        uvs = vec(*uvs)

        # Create a list of triangle indices.
        indices = []
        for i in xrange(0, int(len(positions)/3) - divLat - 1, divLat + 1):
            for j in xrange(divLat):
                indices.extend([i + j, i + j + 1, i + j + 2 + divLat])
                indices.extend([i + j, i + j + 2 + divLat, i + j + 1 + divLat])

        indices = (GLuint * len(indices))(*indices)
        # Compile a display list
        self.list = glGenLists(1)
        glNewList(self.list, GL_COMPILE)

        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_NORMAL_ARRAY)
        glEnableClientState(GL_TEXTURE_COORD_ARRAY)
        glVertexPointer(3, GL_FLOAT, 0, positions)
        glNormalPointer(GL_FLOAT, 0, normals)
        glTexCoordPointer(2, GL_FLOAT, 0, uvs)
        glDrawElements(GL_TRIANGLES, len(indices), GL_UNSIGNED_INT, indices)

        glEndList()

    def draw(self):
        glCallList(self.list)


def load_song(filename, d):
    print "About to load sound file %s" % filename
    y, sr = librosa.load(filename, duration=d)
    print "Successfully loaded file."
    return y, sr


def separate_fg_and_bg(y):
    return librosa.effects.hpss(y)

def next_song(dt):
    global currSong
    currSong += 1
    player.next()
    bframe = 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process a sound file.')
    parser.add_argument('songs', type=str, nargs='*', help='the paths to the sound files')
    args = parser.parse_args()

    # build my song infos
    currSong = 0
    clip_length = 30 # 30 second clip
    master = []
    player = pyglet.media.Player()
    for i, song in enumerate(args.songs):
        print "Analyzing " + song + "..."
        y, sr = load_song(song, clip_length)
        y_harmonic, y_percussive = separate_fg_and_bg(y)
        print "Separated FG and BG"
        hop_length = 64
        tempo, beat_frames = librosa.beat.beat_track(y=y_percussive,
                                                     sr=sr,
                                                     hop_length=hop_length)
        print "Calculated beat frames"
        beat_times = [0] + [librosa.frames_to_time(beat_frame,
                                                   sr=sr,
                                                   hop_length=hop_length)
                            for beat_frame in beat_frames]
        master.append(beat_times)

        # put in player
        song = pyglet.media.load(song)
        player.queue(song)

    setup()
    sphere = Sphere(100, 100)
    ry = 0
    bpm = tempo
    bps = 60 / bpm
    bump = 0
    elapsed_time = 0
    bframe = 1

    raw_input("Analysis complete. Press Enter to continue...\n")

    # go to the next song every n seconds
    n = 20
    pyglet.clock.schedule_interval(next_song, n)

    player.play()
    pyglet.app.run()
