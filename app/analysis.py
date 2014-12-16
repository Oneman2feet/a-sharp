from __future__ import division
import librosa
import numpy as np
import matplotlib.pyplot as plt


def key_finder(amplitudes):
    '''
    Finds the key of the piece whose amplitude sums per frequency are
    supplied as the argument.
    
    Coefficients for the tonic, subdominant and dominant are based on
    http://ismir2004.ismir.net/proceedings/p018-page-92-paper164.pdf. The
    average of the corresponding coefficients in the two graphs under the
    section "TONALITY COMPUTATION USING A COGNITION-INSPIRED MODEL" is used.
    '''
    
    result = []
    for index in range(len(amplitudes)):
        result.append(amplitudes[index] * 0.91 + amplitudes[(
            index + 5) % 12] * 0.44 + amplitudes[(index + 7) % 12] * 0.89)
        print result[index]
    return result.index(max(result))


def major_score(amplitudes, base_key, amplitude_sum):
    '''
    Based on http://ismir2004.ismir.net/proceedings/p018-page-92-paper164.pdf.
    The coefficients corresponding to each scale degree are the average of the
    corresponding coefficients in the two graphs under the section "TONALITY
    COMPUTATION USING A COGNITION-INSPIRED MODEL." 5.29 and 5.59 are the sums of
    those coefficients for major_score and minor_score respectively.
    '''
    return abs(amplitudes[base_key] - (1.0 / 6.20) * amplitude_sum) + abs(
        amplitudes[(base_key +  1) % 12] - (0.36 / 6.2) * amplitude_sum) + abs(
        amplitudes[(base_key +  2) % 12] - (0.54 / 6.2) * amplitude_sum) + abs(
        amplitudes[(base_key +  3) % 12] - (0.19 / 6.2) * amplitude_sum) + abs(
        amplitudes[(base_key +  4) % 12] - (0.68 / 6.2) * amplitude_sum) + abs(
        amplitudes[(base_key +  5) % 12] - (0.64 / 6.2) * amplitude_sum) + abs(
        amplitudes[(base_key +  6) % 12] - (0.40 / 6.2) * amplitude_sum) + abs(
        amplitudes[(base_key +  7) % 12] - (0.82 / 6.2) * amplitude_sum) + abs(
        amplitudes[(base_key +  8) % 12] - (0.19 / 6.2) * amplitude_sum) + abs(
        amplitudes[(base_key +  9) % 12] - (0.57 / 6.2) * amplitude_sum) + abs(
        amplitudes[(base_key + 10) % 12] - (0.36 / 6.2) * amplitude_sum) + abs(
        amplitudes[(base_key + 11) % 12] - (0.45 / 6.2) * amplitude_sum)


def minor_score(amplitudes, base_key, amplitude_sum):
    '''
    Based on http://ismir2004.ismir.net/proceedings/p018-page-92-paper164.pdf.
    The coefficients corresponding to each scale degree are the average of the
    corresponding coefficients in the two graphs under the section "TONALITY
    COMPUTATION USING A COGNITION-INSPIRED MODEL." 5.29 and 5.59 are the sums of
    those coefficients for major_score and minor_score respectively.
    '''
    return abs(amplitudes[base_key] - (1.0 / 6.6) * amplitude_sum) + abs(
        amplitudes[(base_key +  1) % 12] - (0.43 / 6.6) * amplitude_sum) + abs(
        amplitudes[(base_key +  2) % 12] - (0.55 / 6.6) * amplitude_sum) + abs(
        amplitudes[(base_key +  3) % 12] - (0.84 / 6.6) * amplitude_sum) + abs(
        amplitudes[(base_key +  4) % 12] - (0.21 / 6.6) * amplitude_sum) + abs(
        amplitudes[(base_key +  5) % 12] - (0.55 / 6.6) * amplitude_sum) + abs(
        amplitudes[(base_key +  6) % 12] - (0.40 / 6.6) * amplitude_sum) + abs(
        amplitudes[(base_key +  7) % 12] - (0.74 / 6.6) * amplitude_sum) + abs(
        amplitudes[(base_key +  8) % 12] - (0.63 / 6.6) * amplitude_sum) + abs(
        amplitudes[(base_key +  9) % 12] - (0.22 / 6.6) * amplitude_sum) + abs(
        amplitudes[(base_key + 10) % 12] - (0.53 / 6.6) * amplitude_sum) + abs(
        amplitudes[(base_key + 11) % 12] - (0.50 / 6.6) * amplitude_sum)


# returns a tuple representing the base HSV color
def mood_finder(isMajor, tempo):
    value = 0.7 if isMajor else 0.5
    tempo2 = -60.0 if tempo < 40.0 else (90.0 if tempo > 190.0 else tempo - 100.0)
    value += tempo2 / 300.0
    tempo2 += 60.0
    red_temp = tempo2 / 150.0
    red_temp = red_temp ** 2 if red_temp < 0.5 else 1 - ((1 - red_temp) ** 2)
    green = 0 if not isMajor else red_temp
    if red_temp > 0.999:
        red_temp = 0.999
    else:
        green += 0.001
    blue = 1.0 - red_temp
    red = 1.0 if isMajor else red_temp
    return red * value, green * value, blue * value


def gather_data(filename):
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
    print "Gathering song data..."

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

    # repeat each value 256 times
    frequencies = [[f for f in frame for _ in xrange(256)] for frame in frequencies]

    # get the framerate of the frequencies
    dur = librosa.get_duration(y)
    numframes = len(frequencies)
    framerate = dur / numframes

    # calculate the times of each beat event
    tempo, beat_frames = librosa.beat.beat_track(y=y_percussive, sr=sr, hop_length=64)
    beats = [0] + [librosa.frames_to_time(b, sr=sr, hop_length=64) for b in beat_frames] + [dur]

    # get the elevation at each frame
    elevations = [ elevation(freqs) for freqs in frequencies ]
    
    # set the list of amplitudes for each semitone
    chromagram = librosa.feature.chromagram(y, sr)
    amplitudes = []
    for i in range(len(chromagram)):
        amplitudes.append(0)
        for t in chromagram[i]:
            amplitudes[i] += t

    # get the key of the whole audio
    base_key = key_finder(amplitudes)
    print base_key
    
    # get the base colors for the sphere
    amplitude_sum = 0.0
    for amplitude in amplitudes:
        amplitude_sum += amplitude
    print major_score(amplitudes, base_key, amplitude_sum)
    print minor_score(amplitudes, base_key, amplitude_sum)
    base_red, base_green, base_blue = mood_finder(major_score(
        amplitudes, base_key, amplitude_sum) < minor_score(
        amplitudes, base_key, amplitude_sum), tempo)

    base_colors = [ base_red, base_green, base_blue ]

    return {
        "beats": beats,
        "framerate": framerate,
        "numframes": numframes,
        "frequencies": frequencies,
        "elevations": elevations,
        "base_colors": base_colors,
    }


# computes the height of the average pitch on a scale of -1 to 1
def elevation(frequency_amplitudes):
    weighted_sum = np.sum([ i*x for i,x in enumerate(frequency_amplitudes) ])
    size = np.sum(frequency_amplitudes)
    if size!=0: weighted_sum = weighted_sum / size
    return 2 * weighted_sum / len(frequency_amplitudes) - 1
