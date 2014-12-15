import sys
import argparse
import librosa
import numpy as np
import matplotlib.pyplot as plt

# matplotlib for displaying the output
#import matplotlib.pyplot as plt
#%matplotlib inline

# and IPython.display for audio output
#import IPython.display

# use filename=librosa.util.example_audio_file() for an example
def load_song(filename, d):
    print "About to load sound file %s" % filename
    y, sr = librosa.load(filename, duration=d)
    print "Successfully loaded file."
    return y, sr

def separate_fg_and_bg(y):
    return librosa.effects.hpss(y)

if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Process a sound file.')
    parser.add_argument('filename', type=str, help='the path to the sound file')
    parser.add_argument('-d', dest='duration', type=float, help='specify the duration of the sound file to be analyzed')
    args = parser.parse_args()

    print "beginning analysis"
    y, sr = load_song(args.filename, args.duration)
    #D = np.abs(librosa.stft(y))
    C = librosa.feature.chromagram(y, sr)
    #CQT = librosa.cqt(y, sr=sr)

    # Visualize an STFT with linear/log frequency scaling
    # librosa.display.specshow(D, sr=sr, y_axis='log')

    # Visualize a CQT with note markers
    # librosa.display.specshow(CQT, sr=sr, y_axis='cqt_note', fmin=librosa.midi_to_hz(24))

    # Draw time markers automatically
    # librosa.display.specshow(D, sr=sr, hop_length=hop_length, x_axis='time')

    # Draw a chromagram with pitch classes
    librosa.display.specshow(C, y_axis='chroma')

    # Force a grayscale colormap (white -> black)
    # librosa.display.specshow(librosa.logamplitude(D), cmap='OrRd')

    # librosa.display.time_ticks([10.0, 20.0, 30.0])


    # trying to visualize spectogram
    #plt.plot(D[0],  color="r")
    #plt.plot(D[10], color="g")
    #plt.plot(D[20], color="b")
    #plt.plot(D[200], color="y")


    print "about to display"
    plt.show()

    # tempo, beats = librosa.beat.beat_track(y, sr)
    # librosa.output.frames_csv('beat_times.csv', beats)

    # Separate harmonics and percussives into two waveforms
    #H, P = librosa.effects.hpss(D)


#######################################################################################

def test():
    
    # Set the hop length
    hop_length = 64

    # Beat track on the percussive signal
    tempo, beat_frames = librosa.beat.beat_track(y=y_percussive, sr=sr, hop_length=hop_length)

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