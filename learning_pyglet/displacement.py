from __future__ import division
from math import pi, sin, cos
from shader import Shader
from pyglet.gl import *
import pyglet

pyglet.resource.path.append('textures')
pyglet.resource.reindex()
texturecnt = 1

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
    global rx, ry, rz, tx, ty
    rx += dt * 1
    ry += dt * 80
    rz += dt * 30
    rx %= 360
    ry %= 360
    rz %= 360
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
    for i in range(texturecnt):
        glActiveTexture(GL_TEXTURE0+i)
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, texture[i].id)
        shader.uniformi('my_color_texture[' + str(i) + ']', i)
    sphere.draw()
    for i in range(texturecnt):
        glActiveTexture(GL_TEXTURE0+i)
        glDisable(GL_TEXTURE_2D)
    shader.unbind()


def setup():
    # One-time GL setup
    global light0pos
    global light1pos
    global toggletexture
    global texture

    light0pos = [20.0, 20.0, 0.0, 1.0]  # positional light !
    light1pos = [-20.0, -20.0, 20.0, 0.0]  # infinitely away light !
    glClearColor(1, 1, 1, 1)
    glColor4f(1, 1, 1, 1)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_CULL_FACE)

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

    glLightfv(GL_LIGHT0, GL_POSITION, vec(*light0pos))
    glLightfv(GL_LIGHT0, GL_AMBIENT, vec(0.3, 0.3, 0.3, 1.0))
    glLightfv(GL_LIGHT0, GL_DIFFUSE, vec(0.9, 0.9, 0.9, 1.0))
    glLightfv(GL_LIGHT0, GL_SPECULAR, vec(1.0, 1.0, 1.0, 1.0))

    glLightfv(GL_LIGHT1, GL_POSITION, vec(*light1pos))
    glLightfv(GL_LIGHT1, GL_DIFFUSE, vec(.6, .6, .6, 1.0))
    glLightfv(GL_LIGHT1, GL_SPECULAR, vec(1.0, 1.0, 1.0, 1.0))

    glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, vec(0.5, 0.5, 0.5, 1.0))
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, vec(1, 1, 1, 1))
    glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 50)

    texture = []
    for i in xrange(texturecnt):
        texturefile = 'Texturemap' + str(i) + '.jpg'
        print "Loading Texture", texturefile
        textureSurface = pyglet.resource.texture(texturefile)
        texture.append(textureSurface.get_texture())
        glBindTexture(texture[i].target, texture[i].id)
        print "Texture ", i, " bound to ", texture[i].id

    glLightfv(GL_LIGHT0, GL_POSITION, vec(.5, .5, 1, 0))
    glLightfv(GL_LIGHT0, GL_SPECULAR, vec(.5, .5, 1, 1))
    glLightfv(GL_LIGHT0, GL_DIFFUSE, vec(1, 1, 1, 1))
    glLightfv(GL_LIGHT1, GL_POSITION, vec(1, 0, .5, 0))
    glLightfv(GL_LIGHT1, GL_DIFFUSE, vec(.5, .5, .5, 1))
    glLightfv(GL_LIGHT1, GL_SPECULAR, vec(1, 1, 1, 1))

    glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, vec(0.5, 0.5, 0.5, 1))
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, vec(1, 1, 1, 1))
    glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 50)


shader = Shader(['''
    varying vec3 normal, lightDir0, lightDir1, eyeVec;

    void main()
    {
        normal = gl_NormalMatrix * gl_Normal;

        vec3 vVertex = vec3(gl_ModelViewMatrix * gl_Vertex);

        lightDir0 = vec3(gl_LightSource[0].position.xyz - vVertex);
        lightDir1 = vec3(gl_LightSource[1].position.xyz - vVertex);
        eyeVec = -vVertex;

        gl_Position = ftransform();
        gl_TexCoord[0] = gl_TextureMatrix[0] * gl_MultiTexCoord0;
    }
    '''], ['''
    varying vec3 normal, lightDir0, lightDir1, eyeVec;
    uniform sampler2D my_color_texture['''+str(texturecnt)+'''];

    void main(void)
    {
        vec4 texColor = texture2D(my_color_texture[0], gl_TexCoord[0].st);
        vec4 final_color;

        vec4 sceneColor = gl_FrontLightModelProduct.sceneColor;
        vec4 rgb = vec4(texColor.rgb,1.0);
        final_color = (sceneColor * rgb) +
            (gl_LightSource[0].ambient * rgb) +
            (gl_LightSource[1].ambient * rgb);

        vec3 N = normalize(normal);
        vec3 L0 = normalize(lightDir0);
        vec3 L1 = normalize(lightDir1);

        float lambertTerm0 = dot(N, L0);
        float lambertTerm1 = dot(N, L1);

        if(lambertTerm0 > 0.0)
        {
            final_color += gl_LightSource[0].diffuse *
                gl_FrontMaterial.diffuse * lambertTerm0;

            vec3 E = normalize(eyeVec);
            vec3 R = reflect(-L0, N);
            float specular = pow(max(dot(R,E),0.0),gl_FrontMaterial.shininess);
            final_color += gl_LightSource[0].diffuse *
                gl_FrontMaterial.diffuse * specular;
        }
        if(lambertTerm1 > 0.0)
        {
            final_color += gl_LightSource[1].diffuse *
                gl_FrontMaterial.diffuse * lambertTerm1;

            vec3 E = normalize(eyeVec);
            vec3 R = reflect(-L0, N);
            float specular = pow(max(dot(R,E),0.0),gl_FrontMaterial.shininess);
            final_color += gl_LightSource[1].diffuse *
                gl_FrontMaterial.diffuse * specular;
        }
        gl_FragColor = final_color;
    }
    '''])


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
                print [i/divLong, 1-(j/divLat)]
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

        glPushClientAttrib(GL_CLIENT_VERTEX_ARRAY_BIT)
        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_NORMAL_ARRAY)
        glEnableClientState(GL_TEXTURE_COORD_ARRAY)
        glVertexPointer(3, GL_FLOAT, 0, positions)
        glNormalPointer(GL_FLOAT, 0, normals)
        glTexCoordPointer(2, GL_FLOAT, 0, uvs)
        glDrawElements(GL_TRIANGLES, len(indices), GL_UNSIGNED_INT, indices)
        glPopClientAttrib()

        glEndList()

    def draw(self):
        glCallList(self.list)

setup()
sphere = Sphere(100, 100)
rx = ry = rz = 0

pyglet.app.run()
