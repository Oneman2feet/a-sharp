Required packages
-----------------

I. Pyglet
  1. Install mercurial
  2. Install pip
  3. Run ```pip install hg+https://pyglet.googlecode.com/hg/``` (this will take a minute to complete)

II. Shader.py
  1. Go to [http://swiftcoder.wordpress.com/2008/12/19/simple-glsl-wrapper-for-pyglet/](http://swiftcoder.wordpress.com/2008/12/19/simple-glsl-wrapper-for-pyglet/)
  2. Copy/paste the code there into a file called "shader.py"
  3. Add the line ```from ctypes import *``` to the top of the file
  4. Save "shader.py" into the directory where your Python modules are saved (for Mac should be ```/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/site-packages/``` or ```/usr/local/lib/python2.7/site-packages```)

III. AVbin (to run music files)
  1. install this ```http://avbin.github.io/AVbin/Download.html```

IV. LibROSA (see [https://github.com/Oneman2feet/a-sharp/tree/master/learning_librosa] for installation)

Optional Conveniences
---------------------

I. Run ```defaults write org.python.python ApplePersistenceIgnoreState NO``` to stop the weird ```ApplePersistenceIgnoreState``` messages

Running
-------

I. From the parent directory, run ```python app/``` with one of the files in the ```songs/``` directory.

II. Once the song has loaded, the terminal will prompt you to press enter to begin playing.
