import midi_to_text
from midi_to_text import midiToText

import argparse
import glob

from os.path import isdir

from datetime import datetime

# progress bar
from tqdm import tqdm

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--dir', '-d', help='directory containing midi files', required=True)
    args = parser.parse_args()

    if not isdir(args.dir):
        raise Exception("Directory does not exist / is not a directory: {}".format(args.dir))
    
    files = glob.glob('{}/*.mid*'.format(args.dir))
    print(files)

    output_name = 'output_{}.txt'.format(datetime.now().strftime("%d%h%y_%Hh%Mm%S"))
    with open(output_name, 'w+') as f:
        for mid in tqdm(files):
            f.write(midiToText(mid))
            f.write('\n')

