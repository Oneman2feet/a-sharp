LibROSA Installation Instructions
=================================

1.  ```pip install librosa```

2.  If there are problems with getting a Fortran compiler on MacOSX, try ```brew install gcc``` and make sure your XCode is updated.

3.  You're also going to want to get ```scikits.samplerate``` for better performance.

    a. On my mac with homebrew, I got away with ```brew install libsamplerate``` and then ```pip install scikits.samplerate```
