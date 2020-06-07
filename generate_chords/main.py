import os
from argparse import ArgumentParser
import random
from random import randint

try:
    import numpy as np
except Exception as e:
    parser.exit('{type}: {e}'.format(type=type(e).__name__, e=str(e)))



class ChordProgression:
    def __init__(self, sentiment):

        self.sentiment = sentiment

        self.key = generate_key()
        self.chords = generate_chords()
        
    def generate_key(self):
        key_note = randint(0, 11)
        key_major = randint(0, 1) #0: minor, 1: major
        return (key_note, key_major)

    def generate_chords(self):
        chord_progressions = [
            [1, 6, 3, 7], 
            [3, 1, 5, 2],
            [3, 1, 5, 2],
            [3, 1, 2, 5],
            [3, 5, 1, 2], 
            [4, 5, 6, 1],
            [6, 4, 1, 5],
            [6, 4, 1, 7],
            
        ]


class Chord:
    def __init__(self, key, name, notes, sentiment):

        assert type(key) is tuple, "key is not an tuple: %r" % key
        assert type(name) is str, "name is not an string: %r" % name

        self.key = key # (0-11, 1-0: major/minor)
        self.name = name #0-6 e.g. 0 is tonic, 1 is supertonic etc.
        self.note_distance = #0-....
        self.generate_notes()

    """Returns a more representative key of the chord."""
    def get_key(self):
        octave = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#' 'A', 'A#', 'B']
        return (octave[self.key[0]], ['minor', 'major'][self.key[1]])

    def generate_notes(self):
        tonic = self.key[0]
        
        # 2 is tone, 1 is semitone
        scale = [[2, 1, 2, 1, 1, 2, 2], [2, 2, 1, 2, 2, 2, 1]][self.key[1]] # (melodic) minor, major
        
        # .: scale[0] is key
        interval_to_starting_note = sum(scale[:(self.name - 1)]) # in semitones
        self.starting_note = (self.key + interval_to_starting_note) // 12

        starting_note_major = [[1, 0, 0, 1, 1, 0, 0], [0, 0, 1, 0, 0, 1, 1]][self.key[1]][self.starting_note]

        notes_component = []
        for d in note_distances:
            assert type(d) is int, "note_distances must contain type int: %r" % d

            if d > 0:
                notes_component.append(interval_starting_note)




        


if __name__ == "__main__":
    print(Chord())