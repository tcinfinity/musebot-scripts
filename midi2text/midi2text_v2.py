import fnmatch
import os
import argparse
import warnings

import mido
from mido import MidiFile, MidiTrack

import music21
from music21 import *

import numpy as np
import math


"""Converts MIDI file to text"""
def midiToText(filename):

    print('File: {}'.format(filename))

    # read from input filename
    mid = MidiFile(filename)

    print('Length (sec): {}'.format(mid.length))
    print('Ticks per beat: {}'.format(mid.ticks_per_beat)) # e.g. 96/480 per beat (crotchet)


    # check for muliple tempos (e.g. change in tempo halfway through piece)
    check_multiple_tempos = []

    # instantiate final tempo for piece
    tempo = None

    """
    What is a channel? vs What is a track?
    e.g.:
    • Track 1 contains the notes played by right hand with a piano voice on channel 0.
    • Track 2 contains the notes played by left hand with the same piano voice on channel 0, too.
    • Track 3 contains the bass voice on channel 1.
    • Track 4 contains a clarinet voice on channel 2.
    • Track 5 contains the drums on channel 9.
    """

    for i, track in enumerate(mid.tracks):

        print('Track {}: {}'.format(i, track.name))

        for msg in track:
            print(msg)
            if msg.type == 'set_tempo': # Note: is_meta
                msg_bpm = mido.tempo2bpm(msg.tempo) # convert from microseconds to bpm (e.g. 500000 us to 120 bpm)
                msg_bpm_int = int(msg_bpm)
                if msg_bpm != msg_bpm_int:
                    warnings.warn('Non-integer bpm: {} (tempo) -> {} (bpm)'.format(msg.tempo, msg_bpm))
                check_multiple_tempos.append(msg_bpm_int)

    if len(check_multiple_tempos) > 1:
        warnings.warn('Multiple tempos: {}'.format(check_multiple_tempos))
    
    elif len(check_multiple_tempos) == 0: # does this even happen?
        warnings.warn('No tempo: setting default 120')
        tempo = 120

    else: # only one tempo
        tempo = check_multiple_tempos[0]

    print('Tempo: {}'.format(tempo))


    # get total time of piece
    # mid.length returns total playback time in seconds
    length_in_ticks = mid.length/60*tempo*mid.ticks_per_beat #mido.second2tick(mid.length, ticks_per_beat=mid.ticks_per_beat, tempo=tempo)
    print(length_in_ticks)


    # contains arrays of messages (only notes) for each track
    messages_list = []

    for i, track in enumerate(mid.tracks):

        # create new nested list for each track
        messages_list.append([])

        for msg in track:

            if msg.type == 'note_on':
                messages_list[i].append(msg)

            elif msg.type == 'note_off':
                # convert to note_on with velocity=0
                new_msg = mido.Message('note_on', note=msg.note, velocity=0, time=msg.time)
                messages_list[i].append(new_msg)

        
    # remove empty lists
    messages_list = [track for track in messages_list if len(track) > 0]



    # group elements into similar delta times (e.g. time: [48, 0], [96, 0, 0, 0])

    grouped_messages_list = []
    for x, track in enumerate(messages_list):
        grouped_messages_list.append([])

        count = 0
        temp_count = 0
        while count < len(track):

            # add current msg (should be time ≠ 0)
            new_group = {
                'group': [track[count]], 
                'time': track[count].time
            }
            
            # add one for current msg added at start
            count += 1

            # freeze current value of count
            temp_count = count

            # add all following msgs that are time = 0
            for i in range(len(track) - temp_count):

                msg = track[temp_count+i]
                if msg.time == 0:
                    new_group['group'].append(msg)
                    count += 1

                # break before next non-zero time
                else:
                    break

            # append temp grouped msgs back to group_messages
            grouped_messages_list[x].append(new_group)



    """
    Generation of text
    
    Set top track (lowest index) to be 'melody'
    With all other tracks to be 'accomp<n>' where <n> will be an integer starting from 0 (accompaniment)
    
    Note: Actual "theoretical" melody may cross over into other tracks (i.e. "accompaniment")
    """

    # instantiate text list
    # [CLS] (classification) used for indicating start of input (using other model standards)
    result_list = ['[CLS]', 'tempo{}'.format(tempo), '[127]']


    # loop through grouped messages and check for delta time differences between tracks

    # to keep track of time passed during the piece
    current_wait_time_elapsed = 0
    time_embed_counter = 126
    time_embed_interval = math.ceil(length_in_ticks / 127) # rounding up - should prevent underflow of time i.e. [0] comes before end of piece

    while max(len(track) for track in grouped_messages_list) > 0:

        all_first_groups = []
        for t in grouped_messages_list:

            # if track is empty replace with None
            if len(t) == 0:
                all_first_groups.append(None)

            else:
                # use pop to remove from list
                all_first_groups.append(t.pop(0))
    
        # all first times - use None for empty tracks (already replaced with None above)
        all_first_times = [group['time'] if group is not None else None for group in all_first_groups]


        # get min times in all_first_times ignoring None
        min_dt = min(t for t in all_first_times if t is not None)

        # append wait
        if min_dt != 0:
            wait_text = 'wait:{}'.format(min_dt)
            result_list.append(wait_text)

            current_wait_time_elapsed += min_dt

            if time_embed_counter != 0:

                # check for insertion of wait (word) embedding
                if current_wait_time_elapsed > time_embed_interval:

                    time_embed_multiple = current_wait_time_elapsed // time_embed_interval
                    time_pushover = current_wait_time_elapsed - time_embed_interval * time_embed_multiple

                    word_embedding = '[{}]'.format(time_embed_counter)
                    result_list.append(word_embedding)

                    current_wait_time_elapsed = time_pushover
                    time_embed_counter -= time_embed_multiple

                    # time_embed_counter cannot be 0 due to integer rounding

        for i, track_group in enumerate(all_first_groups):

            # check if None (no notes left in that track)
            if track_group is None:
                continue


            if all_first_times[i] == min_dt:
                for msg in track_group['group']:

                    # convert from 1-88 to A4
                    note = music21.note.Note(msg.note)
                    note_name = note.nameWithOctave

                    track_type = 'melody' if i == 0 else 'accomp{}'.format(i-1)
                    new_text = '{track_type}:v{vel}:{note}'.format(track_type=track_type, vel=msg.velocity, note=note_name)

                    result_list.append(new_text)


            elif all_first_times[i] > min_dt:

                time_difference = all_first_times[i] - min_dt

                # prepend filler wait to remaining track
                new_filler_group = {'group': all_first_groups[i]['group'], 'time': time_difference}    # no need to .copy()
                grouped_messages_list[i].insert(0, new_filler_group)



        # Possible scenario: ONLY if at the start, one track has a rest e.g. time=96

    print('Final time embedding: {}'.format(time_embed_counter))
    result_list.append('[0]')
    result_list.append('[END]')

    result_string = ' '.join(result_list)

    return result_string



# Testing purposes
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', '-f', help='midi filename')
    args = parser.parse_args()

    if args.file:
        print(midiToText(args.file))