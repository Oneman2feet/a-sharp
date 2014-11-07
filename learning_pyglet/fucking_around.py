import sys

import pyglet

if len(sys.argv) > 1:
    # Load the animation from file path.
    animation = pyglet.image.load_animation(sys.argv[1])
else:
    # Load animation from resource (this script's directory).
    animation = pyglet.resource.animation('charmander.gif')
sprite = pyglet.sprite.Sprite(animation)

window = pyglet.window.Window(width=sprite.width, height=sprite.height)

# Set window background color to white.
pyglet.gl.glClearColor(1, 1, 1, 1)

@window.event
def on_draw():
    window.clear()
    sprite.draw()

pyglet.app.run()