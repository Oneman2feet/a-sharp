import logging
import argparse
import librosa


log_level = logging.DEBUG

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
    beat_frames = librosa.beat.beat_track(y=y)
    logging.info("Successfully tracked beats.")
    return beat_frames


# main method, parses filename and analyses the sound
if __name__ == '__main__':
    logging.basicConfig(level=log_level)
    parser = argparse.ArgumentParser(description='Process a sound file.')
    parser.add_argument('filename', type=str, help='the path to the sound file')
    args = parser.parse_args()

    y, sr = load_song(args.filename)
    y_harmonic, y_percussive = separate_fg_and_bg(y)


    hop_length = 64

    # Beat track on the percussive signal
    tempo, beat_frames = beat_track(y_percussive)

    beat_times = [0] + [frames_to_time(frame) for frame in beat_frames]
