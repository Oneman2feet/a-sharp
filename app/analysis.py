from __future__ import division
import librosa
import numpy as np
import matplotlib.pyplot as plt
import os


'''
Formats the analysis of a sound file into a single easy-to-use dictionary!

filename: the path to the sound file to be analyzed

returns: a dictionary with lots of juicy info!
{
    "beats"       : a list of times at which a beat event occurs
    "framerate"   : the size of a frame in seconds
    "numframes"   : the total number of frames
    "frequencies" : a list of frequency spectrums (256 bins) at each frame
    "elevations"  : a list of the relative pitch heights of each frame 
}
'''
def gather_data(filename):
    print "Gathering song data on {0}...".format(filename)
    # get our song
    y, sr = librosa.load(filename)
    print "Loaded song"
    # separate the foreground and background
    y_harmonic, y_percussive = librosa.effects.hpss(y)
    print "Separated foreground and background"
    # compute the frequency spectrum
    S = librosa.feature.melspectrogram(y, sr=sr, n_fft=2048, hop_length=64, n_mels=316)
    print "Computed frequency spectrum"
    # Convert to log scale (dB) using the peak power as a reference
    log_S = librosa.logamplitude(S, ref_power=np.max)

    # format the frequencies into a list of 256 amplitudes at each frame
    frequencies = [[int(f[t]+80) for f in log_S[30:-30]] for t in xrange(len(log_S[0])) if t%30==0]

    # repeat each value 256 times
    frequencies = [[f for f in frame for _ in xrange(256)] for frame in frequencies]

    # get the framerate of the frequencies
    dur = librosa.get_duration(y)
    numframes = len(frequencies)
    framerate = dur / numframes

    # calculate the times of each beat event
    tempo, beat_frames = librosa.beat.beat_track(y=y_percussive, sr=sr, hop_length=64)
    beats = [0] + [librosa.frames_to_time(b, sr=sr, hop_length=64) for b in beat_frames] + [dur]
    print "Calculated beats"
    # get the elevation at each frame
    elevations = [ elevation(freqs) for freqs in frequencies ]

    song_info = {
        "beats": beats,
        "framerate": framerate,
        "numframes": numframes,
        "frequencies": frequencies,
        "elevations": elevations
    }
    return song_info


# computes the height of the average pitch on a scale of -1 to 1
def elevation(frequency_amplitudes):
    weighted_sum = np.sum([ i*x for i,x in enumerate(frequency_amplitudes) ])
    size = np.sum(frequency_amplitudes)
    if size!=0: weighted_sum = weighted_sum / size
    return 2 * weighted_sum / len(frequency_amplitudes) - 1
