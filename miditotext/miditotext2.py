import fnmatch
import os
import argparse
import warnings

import mido
from mido import MidiFile, MidiTrack

import music21
from music21 import *

import numpy as np


"""Converts MIDI file to text"""
def midiToText(filename):

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
        while count < len(track):

            # add current msg (should be time ≠ 0)
            new_group = {
                'group': [track[count]], 
                'time': track[count].time
            }

            # add all following msgs that are time = 0
            for i in range(1, len(track) - count):
                msg = track[count+i]
                if msg.time == 0:
                    new_group['group'].append(msg)
                    count += 1

                # break before next non-zero time
                else:
                    break

            # append temp grouped msgs back to group_messages
            grouped_messages_list[x].append(new_group)

            # add one for current msg added at start
            count += 1



    """
    Generation of text
    
    Set top track (lowest index) to be 'melody'
    With all other tracks to be 'accomp<n>' where <n> will be an integer starting from 0 (accompaniment)
    
    Note: Actual "theoretical" melody may cross over into other tracks (i.e. "accompaniment")
    """

    # instantiate text list
    result_list = ['start', 'tempo{}'.format(tempo)]


    # loop through grouped messages and check for delta time differences between tracks

    while max(len(track) for track in grouped_messages_list) > 0:

        all_first_groups = [t.pop(0) for t in grouped_messages_list]        # use pop to remove from list
        all_first_times = [group['time'] for group in all_first_groups]

        min_dt = min(all_first_times)

        # append wait
        if min_dt != 0:
            wait_text = 'wait:{}'.format(min_dt)
            result_list.append(wait_text)

        for i, track_group in enumerate(all_first_groups):

            # if no notes available, i.e. only filler wait
            # ['group'] will be empty list
            # causing for loop (below) to be skipped

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
                new_filler_group = {'group': [], 'time': time_difference}
                grouped_messages_list[i].insert(0, new_filler_group)



        # Possible scenario: ONLY if at the start, one track has a rest e.g. time=96


    result_list.append('end')

    result_string = ' '.join(result_list)

    return result_string


        # # check if all time difference are equal
        # if checkEqual(all_first_times):
            
        #     # Possible scenario: if at the start, all tracks start immediately, time=0
        #     for i, group in enumerate(all_first_groups):
        #         for msg in group:

        #             note = music21.note.Note(msg.note)
        #             note_name = note.nameWithOctave

        #             track_type = 'melody' if i == 0 else 'accomp{}'.format(i-1)
        #             new_text = '{track_type}:v{vel}:{note}'.format(track_type=track_type, vel=msg.velocity, note=note_name)

        #             result_list.append(new_text)

        #     # append wait (any since all are the same)
        #     wait_text = 'wait:{}'.format(all_first_times[0])
        #     result_list.append(wait_text)


        # # Time differences are different
        # else:

        #     """
        #     e.g. Track 1: 0 --- 10
        #          Track 2: 0 -------- 20
        #                         ^ 
        #                         currently here
            
        #     Note: time differences cannot be 0 (due to grouping) UNLESS start
        #     """

        #     # get smallest time difference
        #     min_dt = min(all_first_times)
        #     min_index = [i for i, time in enumerate(all_first_times) if time == min_value]

        #     # find next smallest time to check if next group exceeds
        #     remaining_times = [(i, time) for i, time in enumerate(all_first_times) if time != min_value]
        #     sorted_remaining_times = remaining_times.sort(key=lambda x: x[1]) # sort by time
        #     min_remaining_dt = sorted_remaining_times[0][1]
        #     min_remaining_tuples = [t for t in sorted_remaining_times if t[1] == min_remaining_time] # [(i, time), ...]

        #     # check if only one index smallest
        #     if len(min_index) == 0:
        #         min_index = min_index[0]
                
        #         # get next group for this particular track
        #         next_group = grouped_messages_list[min_index].pop(0)
        #         next_group_dt = next_group[0].time

        #         """
        #                                         *
        #         e.g. Track 1: 0 --- 10 ------- [20]
        #              Track 2: 0 -------- 20
        #                             ^ 
        #         """

        #         if next_group_dt > min_remaining_time - min_dt: 
        #             # cut

        #         else:
        #             # add extra messages, add back popped values to grouped_messages_list
        #             # TODO: this should fix need for recursion

        #     # multiple smallest, get all groups
        #     else:


        #     # TODO: optimize algorithm for stopping
        #     # currently requires recursive function, need to reduce
        #     # try adding all remaining times until it meets up
        #     # or cut list and append back to gront of grouped_messages_list to equalize all start times


        # # check for out of index on next iteration - caused by empty track
        # # use if statement to cut down on time
        # minimum_index_length_of_tracks = min(len(track) for track in messages_list))
        # if minimum_index_length_of_tracks == 0:
        #     grouped_messages_list = [t for t in grouped_messages_list if len(t) != 0]

    # TODO: insert embeddings that count down from 127 to 0 within the piece

    # for i, track in enumerate(inputMidi.tracks):
    #     # add new track for every track
    #     mid.tracks.append(MidiTrack())

    #     notelist = []

    #     for msg in track:
    #         """
    #         What is a channel? vs What is a track?
    #         e.g.:
    #         • Track 1 contains the notes played by right hand with a piano voice on channel 0.
    #         • Track 2 contains the notes played by left hand with the same piano voice on channel 0, too.
    #         • Track 3 contains the bass voice on channel 1.
    #         • Track 4 contains a clarinet voice on channel 2.
    #         • Track 5 contains the drums on channel 9.
    #         """

    #         # print(msg)
    #         # continue
            
    #         # # tempo cannot set channel
    #         # if msg.type != 'set_tempo':
    #         #     msg.channel = i

    #         # 0 - note off; 1 - note on
    #         if msg.type == 'note_off':
    #             notelist.append('0n{}v{}t{}'.format(msg.note, msg.velocity, msg.time))
    #         elif msg.type == 'note_on':
    #             notelist.append('1n{}v{}t{}'.format(msg.note, msg.velocity, msg.time))
          
          
    #         # elif msg.type == 'program_change':
    #         #     # textlist.append('P{}'.format(msg.program))
    #         # elif msg.type == 'set_tempo':
    #         #     # textlist.append('T{}'.format(msg.tempo))
    #         #     msg.tempo = 2000000
    #         # # elif msg.type == 'time_signature':
    #         # #     textlist.append('Sa{}b{}c{}p{}')
    #         # #     midi.tracks[-1].append(msg)break
    #         # else:
    #         #     print(msg.type)

    #         mid.tracks[i].append(msg)

    #     print(' ')

    #     totalNotelist.append(notelist)

    # return totalNotelist


"""Check if all elements in list are equal"""
# http://stackoverflow.com/q/3844948/ - checkEqualIvo
def checkEqual(lst):
    return not lst or lst.count(lst[0]) == len(lst)


# Testing purposes
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', '-f', help='midi filename')
    args = parser.parse_args()

    if args.file:
        print(midiToText(args.file))