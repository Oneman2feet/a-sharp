import sys
import numpy as np
import librosa

debug = True

# use filename=librosa.util.example_audio_file() for an example
def load_song(filename):
  if (debug):
    print "About to load sound file %s" % filename

  y, sr = librosa.load(filename)

  if (debug):
    print "Successfully loaded file."

  return y, sr

if __name__=='__main__':
  if (len(sys.argv)==1):
    print "No path to sound file provided."
  else:
    load_song(sys.argv[1])


#######################################################################################

def test():
  # Separate harmonics and percussives into two waveforms
  y_harmonic, y_percussive = librosa.effects.hpss(y)

  # Set the hop length
  hop_length = 64

  # Beat track on the percussive signal
  tempo, beat_frames = librosa.beat.beat_track(y=y_percussive,
                                               sr=sr,
                                               hop_length=hop_length)

  print "Tempo: %0.2f" % tempo

  # Compute MFCC features from the raw signal
  mfcc = librosa.feature.mfcc(y=y, sr=sr, hop_length=hop_length, n_mfcc=13)

  # And the first-order differences (delta features)
  mfcc_delta = librosa.feature.delta(mfcc)

  # Stack and synchronize between beat events
  # This time, we'll use the mean value (default) instead of median
  beat_mfcc_delta = librosa.feature.sync(np.vstack([mfcc, mfcc_delta]),
                                         beat_frames)

  # Compute chroma features from the harmonic signal
  chromagram = librosa.feature.chromagram(y=y_harmonic,
                                          sr=sr,
                                          hop_length=hop_length)

  # Aggregate chroma features between beat events
  # We'll use the median value of each feature between beat frames
  beat_chroma = librosa.feature.sync(chromagram,
                                     beat_frames,
                                     aggregate=np.median)

  # Finally, stack all beat-synchronous features together
  beat_features = np.vstack([beat_chroma, beat_mfcc_delta])

  print beat_features