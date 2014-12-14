from pyglet.gl import GLfloat, GLuint, GLubyte


# Define a simple function to create ctypes arrays of floats:
def vecf(*args):
    return (GLfloat * len(args))(*args)


# Define a simple function to create ctypes arrays of floats:
def veci(*args):
    return (GLuint * len(args))(*args)


# Define a simple function to create ctypes arrays of floats:
def vecb(*args):
    return (GLubyte * len(args))(*args)
