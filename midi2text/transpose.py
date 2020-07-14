import glob
import os
from os.path import isdir
import music21

from tqdm import tqdm
import argparse

# majors = dict([("A-", 4),("G#", 4),("A", 3),("A#", 2),("B-", 2),("B", 1),("C", 0),("C#", -1),("D-", -1),("D", -2),("D#", -3),("E-", -3),("E", -4),("F", -5),("F#", 6),("G-", 6),("G", 5)])
# minors = dict([("G#", 1), ("A-", 1),("A", 0),("A#", -1),("B-", -1),("B", -2),("C", -3),("C#", -4),("D-", -4),("D", -5),("D#", 6),("E-", 6),("E", 5),("F", 4),("F#", 3),("G-", 3),("G", 2)])

def generate_transposed_midi(input_dir, output_dir):

    steps = [i for i in range(-5, 7) if i != 0]

    for f in tqdm(glob.glob(input_dir+"*.mid")):
        # print(str(f))
        score = music21.converter.parse(f)
        # print(score.show('text'))

        key = score.analyze('key')
        # print(key.tonic.name, key.mode)

        for step in tqdm(steps):
            new_score = score.transpose(step)
            key = new_score.analyze('key')
            key_name = key.tonic.name.split()[0]

            new_file_name = "{output_dir}/{key_name}_{base_name}".format(output_dir=output_dir, key_name=key_name, base_name=os.path.basename(f))
            tqdm.write(new_file_name)
            new_score.write('midi', new_file_name)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--input', '-i', help='path of input directory', default="../../MIDI Files/piano/")
    parser.add_argument('--output', '-o', help='name/path of output directory', default='transpose_output')
    args = parser.parse_args()

    if not isdir(args.input):
        raise Exception("Input directory does not exist / is not a directory: {}".format(args.input))
    if isdir(args.output):
        raise Exception("Output directory already exists: {}".format(args.output))

    os.makedirs(args.output)
    generate_transposed_midi(args.input, args.output)
