from __future__ import division
import librosa
import numpy as np
import matplotlib.pyplot as plt


'''
Formats the analysis of a sound file into a single easy-to-use dictionary!

filename: the path to the sound file to be analyzed

<<<<<<< HEAD
# formats analysis of sound file into a single easy-to-use dictionary
# beats is a list of times in the sound file for which a beat event occurs
# amplitudes is a list of the amplitude of the sound at a given frame
# complexities is a 2d texture list of the complexity of the sound at a given frame
# times is a list of times when each frame occurs
def gather_data(filename, data_queue):
    print "Gathering Data on {0}".format(filename)
=======
returns: a dictionary with lots of juicy info!
{
    "beats"       : a list of times at which a beat event occurs
    "framerate"   : the size of a frame in seconds
    "frequencies" : a list of frequency spectrums (256 bins) at each frame
    "elevations"  : a list of the relative pitch heights of each frame 
}
'''
def gather_data(filename):
    # get our song
    y, sr = librosa.load(filename)

    # separate the foreground and background
    y_harmonic, y_percussive = librosa.effects.hpss(y)

    # compute the frequency spectrum
    S = librosa.feature.melspectrogram(y, sr=sr, n_fft=2048, hop_length=64, n_mels=316)

    # Convert to log scale (dB) using the peak power as a reference
    log_S = librosa.logamplitude(S, ref_power=np.max)

    # format the frequencies into a list of 256 amplitudes at each frame
    frequencies = [[int(f[t]+80) for f in log_S[30:-30]] for t in xrange(len(log_S[0])) if t%30==0]

    # get the framerate of the frequencies
    dur = librosa.get_duration(y)
    framerate = dur / len(frequencies)

    # calculate the times of each beat event
    tempo, beat_frames = librosa.beat.beat_track(y=y_percussive, sr=sr, hop_length=64)
    beats = [0] + [librosa.frames_to_time(b, sr=sr, hop_length=64) for b in beat_frames] + [dur]

    # get the elevation at each frame
    elevations = [ elevation(freqs) for freqs in frequencies ]

    return {
        "beats": beats,
        "framerate": framerate,
        "frequencies": frequencies,
        "elevations": elevations
    }


# computes the height of the average pitch on a scale of -1 to 1
def elevation(frequency_amplitudes):
    weighted_sum = np.sum([ i*x for i,x in enumerate(frequency_amplitudes) ])
    size = np.sum(frequency_amplitudes)
    if size!=0: weighted_sum = weighted_sum / size
    return 2 * weighted_sum / len(frequency_amplitudes) - 1
