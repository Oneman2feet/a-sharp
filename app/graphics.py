from __future__ import division
from shader import Shader
from pyglet.gl import *
from math import cos, sin, pi
from ctypes import *
from PIL import Image
import utils
import pyglet
import numpy as np
import random


try:
    # Try and create a window with multisampling (antialiasing)
    config = Config(sample_buffers=1, samples=4,
                    depth_size=16, double_buffer=True,)
    window = pyglet.window.Window(resizable=True, config=config)
except pyglet.window.NoSuchConfigException:
    # Fall back to no multisampling for old hardware
    window = pyglet.window.Window(resizable=True)


def initialize(_player, _mesh, **song_info):
    global elapsed_time, bump, bframe, fframe, player, mesh, framerate
    global beats, frequencies, colors
    global position, velocity, acceleration, k, m, translations, damping
    beats = song_info['beats']
    translations = song_info['translations']
    colors = song_info['colors']
    frequencies = [[f for f in time for _ in xrange(256)] for time in list(song_info['frequencies'])]
    mesh = _mesh
    player = _player
    framerate = song_info['fframes']
    elapsed_time = bump = ry = 0
    position = velocity = acceleration = 0
    k = 0.5
    m = 1.5
    damping = 0.8
    bframe = 1
    fframe = 1
    pyglet.resource.path.append('textures')
    pyglet.resource.reindex()
    pyglet.clock.schedule(update)


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
    global elapsed_time, bframe, fframe, radius, diffuse_color, cur_frequencies, framerate
    elapsed_time += dt

    next_beat = beats[bframe]
    cur_frequencies = frequencies[fframe]

    if next_beat < elapsed_time:
        bframe += 1
        if bframe == len(beats):
            pyglet.clock.unschedule(update)
            return
        next_beat = beats[bframe]

    prev_beat = beats[bframe - 1]

    if framerate * fframe < elapsed_time:
        fframe += 1
        if fframe == len(frequencies):
            pyglet.clock.unschedule(update)
            return
        cur_frequencies = frequencies[fframe]

    time_since_prev_beat = elapsed_time - prev_beat
    local_spb = next_beat - prev_beat
    beat_bump = abs(local_spb/2 - time_since_prev_beat)**2 * 5
    beat_bump = 1 if beat_bump > 1 else beat_bump

    radius = 1 + 0.2 * beat_bump


    # diffuse_color = [0.5 * cos(elapsed_time/2) + 0.5, -0.5 * cos(elapsed_time/2) + 0.5, 0]
    diffuse_color = colors[fframe]


@window.event
def on_draw():
    global translations, k, m, position, velocity, acceleration
    player.playing = True
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    

    translation = translations[fframe]
    force = k * (translation - position)
    acceleration = force / (m * radius * radius)

    velocity *= damping
    velocity += acceleration * framerate
    
    position += velocity



    glTranslatef(0, position, -6)
    # glRotatef(0, 0, 0, 1)
    # glRotatef(0, 1, 0, 0)

    # glPolygonMode(GL_FRONT, GL_FILL)

    shader.bind()

    shader.uniformf('bump', bump)
    shader.uniformf('radius', radius)
    shader.uniformf('diffuse_color', *diffuse_color)

    glActiveTexture(GL_TEXTURE0)
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, color_texture.id)
    shader.uniformi('color_texture', 0)

    pix = utils.vecb(*cur_frequencies)

    glActiveTexture(GL_TEXTURE1)
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, disp_tex_id)
    glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_LUMINANCE, 256, 256, 0, GL_LUMINANCE, GL_UNSIGNED_BYTE, pix)


    shader.uniformi('disp_texture', 1)
    shader.uniformf('dispMagnitude', 0.2)
    shader.uniformf('elapsed_time', elapsed_time)

    mesh.draw()

    glActiveTexture(GL_TEXTURE1)
    glDisable(GL_TEXTURE_2D)
    glActiveTexture(GL_TEXTURE0)
    glDisable(GL_TEXTURE_2D)

    shader.unbind()


def setup():
    # One-time GL setup
    global light0pos, light1pos
    global color_texture, disp_texture, shader
    global disp_tex_id

    vert_handle = open("app/shaders/DispMapped.vert")
    vert = ["".join([line for line in vert_handle])]
    frag_handle = open("app/shaders/DispMapped.frag")
    frag = ["".join([line for line in frag_handle])]
    shader = Shader(vert, frag)

    glClearColor(0, 0, 0, 1)
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

    disp_tex_id = GLuint(0)
    glGenTextures(1, byref(disp_tex_id))

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    light0pos = [5.0, 5.0, 5.0, 1.0]  # positional light !

    glLightfv(GL_LIGHT0, GL_POSITION, utils.vecf(*light0pos))
    glLightfv(GL_LIGHT0, GL_AMBIENT, utils.vecf(0.9, 0.9, 0.9, 1.0))
    glLightfv(GL_LIGHT0, GL_DIFFUSE, utils.vecf(0.9, 0.9, 0.9, 1.0))
    glLightfv(GL_LIGHT0, GL_SPECULAR, utils.vecf(1.0, 1.0, 1.0, 1.0))

    glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE,
                 utils.vecf(0.5, 0.5, 0.5, 1.0))
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, utils.vecf(1, 1, 1, 1))
    glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 20)


def run():
    pyglet.app.run()
