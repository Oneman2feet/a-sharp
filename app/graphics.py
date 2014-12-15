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


'''
Creates a window to display the visualization
'''

# Try and create a window with multisampling (antialiasing)
try:
    config = Config(sample_buffers=1, samples=4, depth_size=16, double_buffer=True)
    window = pyglet.window.Window(resizable=True, config=config)

# Fall back to no multisampling for old hardware
except pyglet.window.NoSuchConfigException:
    window = pyglet.window.Window(resizable=True)

# Override the default on_resize handler to create a 3D projection
@window.event
def on_resize(width, height):
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60., width / float(height), .1, 1000.)
    glMatrixMode(GL_MODELVIEW)
    return pyglet.event.EVENT_HANDLED



'''
Initializes global variables and schedules the update function
'''
def initialize(_player, _mesh, **song_info):
    global DAMPING_FORCE, SPRING_CONSTANT, SPHERE_DENSITY
    global beats, framerate, numframes, frequencies, translations
    global elapsed_time, beat_index, frame
    global player, mesh, position, velocity
    global max_color, mid_color, min_color
    global max_color_index, mid_color_index, min_color_index

    # initialize constants
    DAMPING_FORCE   = 0.8
    SPRING_CONSTANT = 0.5
    SPHERE_DENSITY  = 1.5

    # initialize variables
    elapsed_time = position = velocity = 0
    beat_index = frame = 1
    mesh = _mesh
    player = _player

    # retrieve data from the song
    beats        = song_info['beats']
    framerate    = song_info['framerate']
    numframes    = song_info['numframes']
    frequencies  = song_info['frequencies']
    translations = song_info['elevations']
    base_colors  = song_info['base_colors']

    print base_colors

    # rank the colors according to their values
    sorted_color_indexes = np.argsort(base_colors)
    max_color_index = sorted_color_indexes[2]
    mid_color_index = sorted_color_indexes[1]
    min_color_index = sorted_color_indexes[0]
    max_color = base_colors[max_color_index]
    mid_color = base_colors[mid_color_index]
    min_color = base_colors[min_color_index]

    print max_color
    print mid_color
    print min_color

    # set the limits in change in mid_color and min_color - max_color stays constant
    mid_color_limit = (max_color - mid_color) / 2
    min_color_limit = (max_color - min_color) / 2.5

    # set update function
    pyglet.clock.schedule(update)


def update(dt):
    '''
    Update sphere properties based on sound analysis
    '''
    
    global beats, framerate, numframes, frequencies, translations
    global position, velocity, radius, color, cur_frequencies
    global elapsed_time, beat_index, frame
    global max_color, mid_color, min_color
    global max_color_index, mid_color_index, min_color_index

    # keep track of time
    elapsed_time += dt

    # update the current frame
    if framerate*frame < elapsed_time:
        frame += 1
        # stop the updates on the last frame
        if frame == numframes:
            pyglet.clock.unschedule(update)
            return

    # update beat when the next beat is reached
    if beats[beat_index] < elapsed_time:
        beat_index += 1
        # stop the updates on the last beat
        if beat_index == len(beats):
            pyglet.clock.unschedule(update)
            return

    # set the current values of data to look at
    next_beat       = beats[beat_index]
    cur_frequencies = frequencies[frame]
    cur_translation = translations[frame]

    # get the previous beat time
    prev_beat = beats[beat_index-1]

    # calculate beat bump
    time_since_prev_beat = elapsed_time - prev_beat
    beat_period = next_beat - prev_beat
    bump_size = 4
    beat_bump = abs(beat_period/2 - time_since_prev_beat)**2 * bump_size
    beat_bump = 1 if beat_bump > 1 else beat_bump

    # calculate loudness bump
    frequencyRange = [freq for freq_ls in frequencies[frame - 1:frame + 2] for freq in freq_ls]
    loudness = sum(frequencyRange) / len(frequencyRange)
    loudness_bump = 0.02 * loudness

    # set sphere radius
    radius = 1 + beat_bump + loudness_bump

    # set sphere color
    color = [None, None, None]
    color[max_color_index] = max_color
    mid_color_temp = abs(mid_color + 0.25 * cos(2*pi*((frame*framerate/(32*beat_period))+0.5)))
    color[mid_color_index] = mid_color_temp if mid_color_temp <= 1.0 else 1.0
    min_color_temp = abs(min_color + 0.15 * cos(2*pi*(frame*framerate/(32*beat_period))))
    color[min_color_index] = min_color_temp if min_color_temp <= 1.0 else 1.0

    # calculate new position
    force = SPRING_CONSTANT * (cur_translation - position)
    acceleration = force / (SPHERE_DENSITY * radius * radius)
    velocity *= DAMPING_FORCE
    velocity += acceleration * framerate
    position += velocity


'''
Set sphere properties to most current calculations
'''
@window.event
def on_draw():
    global position, radius, color, cur_frequencies
    global player, mesh

    player.playing = True

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    glTranslatef(0, position, -8)

    shader.bind()
    shader.uniformf('bump', 0)
    shader.uniformf('radius', radius)
    shader.uniformf('diffuse_color', *color)

    pix = utils.vecb(*[4 * x for x in cur_frequencies])

    glActiveTexture(GL_TEXTURE0)
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, disp_tex_id)
    glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_LUMINANCE, 256, 256, 0, GL_LUMINANCE, GL_UNSIGNED_BYTE, pix)

    shader.uniformi('disp_texture', 0)
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
