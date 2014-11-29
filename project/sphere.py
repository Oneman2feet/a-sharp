from __future__ import division
from math import cos, sin, pi
from pyglet.gl import *
import utils


class Sphere(object):
    """
    OpenGL representation of a Sphere. Stores its position, normal, uv, and
    index vectors, as well as a method to draw
    """
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
        positions = utils.vecf(*positions)
        normals = utils.vecf(*normals)
        uvs = utils.vecf(*uvs)

        # Create a list of triangle indices.
        indices = []
        for i in xrange(0, int(len(positions)/3) - divLat - 1, divLat + 1):
            for j in xrange(divLat):
                indices.extend([i + j, i + j + 1, i + j + 2 + divLat])
                indices.extend([i + j, i + j + 2 + divLat, i + j + 1 + divLat])

        indices = utils.veci(*indices)
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
