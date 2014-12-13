import logging
import argparse

import librosa

import numpy as np
import matplotlib.pyplot as plt



log_level = logging.INFO

def load_song(filename):
    logging.info("About to load sound file %s" % filename)
    y, sr = librosa.load(filename)
    logging.info("Successfully loaded file.")
    return y, sr


def separate_fg_and_bg(y):
    logging.info("About to separate foreground and background")
    y_fg, y_bg = librosa.effects.hpss(y)
    logging.info("Successfully separated foreground and background.")
    return y_fg, y_bg


def frames_to_time(beat_frame):
    logging.info("About to convert a frame to a time")
    beat_times = librosa.frames_to_time(beat_frame)
    logging.info("Successfully converted frame.")
    return beat_times


def beat_track(y):
    logging.info("About to track beats")
    tempo, beat_frames = librosa.beat.beat_track(y=y)
    logging.info("Successfully tracked beats.")
    return tempo, beat_frames


def amplitude(y):
    return np.abs(y)



# main method, parses filename and analyses the sound
if __name__ == '__main__':
    logging.basicConfig(level=log_level)
    parser = argparse.ArgumentParser(description='Process a sound file.')
    parser.add_argument('filename', type=str, help='the path to the sound file')
    args = parser.parse_args()

    # load song that is specified
    y, sr = load_song(args.filename)
    y_harmonic, y_percussive = separate_fg_and_bg(y)

    # graph y_harmonic
    plt.plot(amplitude(y_harmonic))
    plt.show()

    # format beats for graphics
    # beat_times = [0] + [frames_to_time(frame) for frame in beat_frames]





####################################################

def blaze():
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

    print "beginning analysis"
    y, sr = load_song(args.filename, args.duration)
    D = np.abs(librosa.stft(y))
    C = librosa.feature.chromagram(y, sr)
    CQT = librosa.cqt(y, sr=sr)

    # Visualize an STFT with linear/log frequency scaling
    # librosa.display.specshow(D, sr=sr, y_axis='log')

    # Visualize a CQT with note markers
    # librosa.display.specshow(CQT, sr=sr, y_axis='cqt_note', fmin=librosa.midi_to_hz(24))

    # Draw time markers automatically
    # librosa.display.specshow(D, sr=sr, hop_length=hop_length, x_axis='time')

    # Draw a chromagram with pitch classes
    # librosa.display.specshow(C, y_axis='chroma')

    # Force a grayscale colormap (white -> black)
    # librosa.display.specshow(librosa.logamplitude(D), cmap='OrRd')

    # librosa.display.time_ticks([10.0, 20.0, 30.0])


    # trying to visualize spectogram
    plt.plot(D[0],  color="r")
    plt.plot(D[10], color="g")
    plt.plot(D[20], color="b")
    plt.plot(D[200], color="y")


    print "about to display"
    plt.show()

    # tempo, beats = librosa.beat.beat_track(y, sr)
    # librosa.output.frames_csv('beat_times.csv', beats)

    # Separate harmonics and percussives into two waveforms
    #H, P = librosa.effects.hpss(D)















