from __future__ import division
from sphere import Sphere
import song_handling as interface
import os
import argparse


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process a sound file.')
    parser.add_argument('dirname', type=str, help='the path to the sound file directory')
    parser.add_argument('--cache', dest='cache', action='store_true', help='if flag is on, do not play songs, simply store their analyses')
    parser.add_argument('--play', dest='cache', action='store_false', help='if flag is on, do not play songs, simply store their analyses')
    args = parser.parse_args()

    file_list = [args.dirname + f for f in os.listdir(args.dirname)]
    if args.cache:
        interface.cache(file_list)
    else:
        sphere = Sphere(100, 100)

        interface.play(file_list, sphere)
