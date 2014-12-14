from __future__ import division
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


def frames_to_time(frame, sr, hop_length):
    logging.info("About to convert a frame to a time")
    times = librosa.frames_to_time(frame, sr=sr, hop_length=hop_length)
    logging.info("Successfully converted frame.")
    return times


def beat_track(y):
    logging.info("About to track beats")
    tempo, beat_frames = librosa.beat.beat_track(y=y)
    logging.info("Successfully tracked beats.")
    return tempo, beat_frames


def amplitude(y):
    return np.abs(y)


def complexity(y):
    np.abs(librosa.stft(y))


def format_complexities(complexities):
    return [ complexities[1:129] for a in np.arange(128) ]


def key_finder_helper(amplitudes, depth, index):
    if index >= 0 and index < len(amplitudes):
        if depth == 0:
            return amplitudes[index]
        else:
            # -7 and +7 for the perfect fifths, -12 and +12 for octaves
            return key_finder_helper(amplitudes, 0, index - 7
                ) + key_finder_helper(amplitudes, 0, index + 7
                ) + key_finder_helper(amplitudes, depth - 1, index + 12
                ) + key_finder_helper(amplitudes, depth - 1, index - 12)
    else:
        return 0.0
    

def key_finder(amplitudes):
    result = []
    for index in range(len(amplitudes)):
        result.append(key_finder_helper(amplitudes, 2, index))
    return result.index(max(result))

# formats analysis of sound file into a single easy-to-use dictionary
# beats is a list of times in the sound file for which a beat event occurs
# amplitudes is a list of the amplitude of the sound at a given frame
# complexities is a 2d texture list of the complexity of the sound at a given frame
# times is a list of times when each frame occurs
def gather_data(filename):
    y, sr = librosa.load(filename)
    dur = librosa.get_duration(y)
    y_harmonic, y_percussive = librosa.effects.hpss(y)

    S = librosa.feature.melspectrogram(y, sr=sr, n_fft=2048, hop_length=64, n_mels=316)

    # Convert to log scale (dB). We'll use the peak power as reference.
    log_S = librosa.logamplitude(S, ref_power=np.max)
    frequencies = [[int(f[t] + 80) for f in log_S[30:-30]] for t in xrange(len(log_S[0])) if t % 30 == 0]
    notes = librosa.feature.chromagram(y_harmonic, sr)
    tempo, beat_frames = librosa.beat.beat_track(y=y_percussive, sr=sr, hop_length=64)
    beats = [0] + [librosa.frames_to_time(beat, sr=sr, hop_length=64) for beat in beat_frames] + [dur]
    amplitudes = []
    for i in range(len(notes)):
        amplitudes.append[0]
        for t in notes[i]:
            amplitudes[i] += t
    base_key = key_finder(amplitudes)
    return {"beats": beats,
            "frequencies": frequencies,
            "fframes": dur / len(frequencies)}

# main method, parses filename and analyses the sound
if __name__ == '__main__':
    # logging.basicConfig(level=log_level)
    # parser = argparse.ArgumentParser(description='Process a sound file.')
    # parser.add_argument('filename', type=str, help='the path to the sound file')
    # args = parser.parse_args()
    # output = gather_data(args.filename)
    # print output
    gather_data("songs/1-01 20th Century Fox Fanfare.m4a")

    '''
    logging.basicConfig(level=log_level)
    parser = argparse.ArgumentParser(description='Process a sound file.')
    parser.add_argument('filename', type=str, help='the path to the sound file')
    args = parser.parse_args()

    # load song that is specified
    y, sr = load_song(args.filename)
    y_harmonic, y_percussive = separate_fg_and_bg(y)

    # graph y_harmonic
    CQT = librosa.cqt(y, sr=sr)
    # librosa.display.specshow(CQT, sr=sr, y_axis='cqt_note', fmin=librosa.midi_to_hz(24))
    plt.plot(CQT)
    plt.show()

    # format beats for graphics
    # beat_times = [0] + [frames_to_time(frame) for frame in beat_frames]





####################################################

def blaze():
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

'''













