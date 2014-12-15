from __future__ import division
import librosa
import numpy as np
import matplotlib.pyplot as plt


# computes the 
def average_pitch(frequency_amplitudes):
    weighted_sum = np.sum([ i*x for i,x in enumerate(frequency_amplitudes) ])
    num = np.sum(frequency_amplitudes)
    if num!=0:
        weighted_sum = weighted_sum / num
    return 2 * weighted_sum / len(frequency_amplitudes) - 1

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
        amplitudes.append(0)
        for t in notes[i]:
            amplitudes[i] += t
    base_key = key_finder(amplitudes)

    # get the average pitches at each frame
    avgpitches = [ average_pitch(freqs) for freqs in frequencies ]

    return {"beats": beats,
            "frequencies": frequencies,
            "fframes": dur / len(frequencies),
            "translations": avgpitches }












