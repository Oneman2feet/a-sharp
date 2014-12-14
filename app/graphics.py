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


def initialize(_player, _beat_times, _mesh):
    global elapsed_time, bump, bframe, ry, beat_times, player, mesh
    beat_times = _beat_times
    mesh = _mesh
    player = _player
    elapsed_time = bump = ry = 0
    bframe = 1
    pyglet.resource.path.append('textures')
    pyglet.resource.reindex()


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
    global elapsed_time, bump, bframe, ry, radius, diffuse_color
    elapsed_time += dt
    # print elapsed_time

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
    beat_bump = abs(local_spb/2 - time_since_prev_beat)**2 * 5
    beat_bump = 1 if beat_bump > 1 else beat_bump
    radius = 1 + 0.2 * beat_bump

    diffuse_color = [0.5 * cos(elapsed_time/2) + 0.5, -0.5 * cos(elapsed_time/2) + 0.5, 0]

    ry += dt * 80
    ry %= 360
pyglet.clock.schedule(update)


@window.event
def on_draw():
    player.playing = True
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glTranslatef(0, 0, -4)
    glRotatef(0, 0, 0, 1)
    #glRotatef(ry, 0, 1, 0)
    glRotatef(0, 1, 0, 0)

    glPolygonMode(GL_FRONT, GL_FILL)

    shader.bind()

    shader.uniformf('bump', bump)
    shader.uniformf('radius', radius)
    shader.uniformf('diffuse_color', *diffuse_color)

    glActiveTexture(GL_TEXTURE0)
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, color_texture.id)
    shader.uniformi('color_texture', 0)

    pix = []
    for x in range(256):
        for y in range(128):
            pix.append(random.randint(0,50))

    pix = utils.vecb(*pix)

    glActiveTexture(GL_TEXTURE1)
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, disp_tex_id)
    glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_LUMINANCE, 256, 128, 0, GL_LUMINANCE, GL_UNSIGNED_BYTE, pix)

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

    #disp_file = 'disp_map.jpg'
    #print "Loading Texture", disp_file
    #textureSurface = pyglet.resource.texture(disp_file)
    #disp_texture = textureSurface.get_texture()
    #glBindTexture(disp_texture.target, disp_texture.id)
    #print "Displacement texture bound to ", disp_texture.id

    #normal_file = 'Texturemap2.jpg'
    #print "Loading Texture", normal_file
    #textureSurface = pyglet.resource.texture(normal_file)
    #normal_texture = textureSurface.get_texture()
    #glBindTexture(normal_texture.target, normal_texture.id)
    #print "Normal texture bound to ", normal_texture.id

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

    glLightfv(GL_LIGHT0, GL_POSITION, utils.vecf(*light0pos))
    glLightfv(GL_LIGHT0, GL_AMBIENT, utils.vecf(0.9, 0.9, 0.9, 1.0))
    glLightfv(GL_LIGHT0, GL_DIFFUSE, utils.vecf(0.9, 0.9, 0.9, 1.0))
    glLightfv(GL_LIGHT0, GL_SPECULAR, utils.vecf(1.0, 1.0, 1.0, 1.0))

    glLightfv(GL_LIGHT1, GL_POSITION, utils.vecf(*light1pos))
    glLightfv(GL_LIGHT1, GL_AMBIENT, utils.vecf(0.1, 0.1, 0.1, 1.0))
    glLightfv(GL_LIGHT1, GL_DIFFUSE, utils.vecf(0.9, 0.9, 0.9, 1.0))
    glLightfv(GL_LIGHT1, GL_SPECULAR, utils.vecf(1.0, 1.0, 1.0, 1.0))

    glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE,
                 utils.vecf(0.5, 0.5, 0.5, 1.0))
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, utils.vecf(1, 1, 1, 1))
    glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 20)


def run():
    pyglet.app.run()
