import midi2text
from midi2text_gpt import midiToText

import argparse
import glob

import os
from os.path import isdir

from datetime import datetime

# progress bar
from tqdm import tqdm

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--dir', '-d', help='directory containing midi files', required=True)
    parser.add_argument('--csv', '-csv', help='output to comma-separated values file', action='store_true')
    args = parser.parse_args()

    if not isdir(args.dir):
        raise Exception("Directory does not exist / is not a directory: {}".format(args.dir))
    
    files = glob.glob('{}/*.mid*'.format(args.dir))
    print(files)

    if args.csv:
        output_name = 'output_{}.csv'.format(datetime.now().strftime("%d%h%y_%Hh%Mm%S"))
        with open(output_name, 'w+') as f:
            for mid in tqdm(files):

                # remove compilations which do not have chord progression and constant key - affects integrity of piece and training accuracy
                if 'Compilation' in os.path.basename(mid):
                    continue

                f.write(midiToText(mid))
                f.write(',')
    else:
        output_name = 'output_{}.txt'.format(datetime.now().strftime("%d%h%y_%Hh%Mm%S"))
        with open(output_name, 'w+') as f:
            for mid in tqdm(files):

                # remove compilations which do not have chord progression and constant key - affects integrity of piece and training accuracy
                if 'Compilation' in os.path.basename(mid):
                    continue

                f.write(midiToText(mid))
                f.write('\n')

