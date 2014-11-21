from __future__ import division
from math import pi, sin, cos
from shader import Shader
from pyglet.gl import *
import pyglet

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
    global ry, total_time, bps, bump
    total_time += dt
    total_time %= bps
    ry += dt * 80
    ry %= 360
    bump = abs(total_time - bps/2)**2 * 5
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
    # glRotatef(ry, 0, 1, 0)
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

    color_file = 'Texturemap0.jpg'
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

setup()
sphere = Sphere(100, 100)
ry = 0
bpm = 120
bps = 60 / bpm
bump = 0
total_time = 0

pyglet.app.run()
