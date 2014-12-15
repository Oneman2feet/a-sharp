from __future__ import division
from sphere import Sphere
import song_handling as interface
import os
import argparse


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process a sound file.')
    parser.add_argument('dirname', type=str, help='the path to the sound file')
    parser.add_argument('-d', dest='duration', type=float, help='specify the duration of the sound file to be analyzed')
    args = parser.parse_args()

    file_list = [args.dirname + f for f in os.listdir(args.dirname)]
    sphere = Sphere(100, 100)

    interface.play(file_list, sphere)
