import mido

import sys
import os
from os.path import isfile
from warnings import warn

import datetime

import argparse
from tqdm import tqdm

import re

# hard coded stuff
notetonumberacc = {'c#':1,'d-':1,'d#':3,'e-':3,'f#':6,'g-':6,'g#':8,'a-':8,'a#':10,'b-':10, 'c-':-1, 'f-':4, 'b#':12, 'e#':5} 
notetonumbernat = {'c':0,'d':2,'e':4,'f':5,'g':7,'a':9,'b':11,}

# converts from musical notation to midi numbers
def notetonumber(note):

    if '-' in note or '#' in note: # test for accidentals
        # check if octave missing
        if note[2:] == '':
            raise Exception('Missing octave (accidental note): {}'.format(note))

        return notetonumberacc[note[:2:]] + 12*(int(note[2::])+1)

    else: # no accidentals
        # check if octave missing
        if note[1:] == '':
            raise Exception('Missing octave: {}'.format(note))

        return notetonumbernat[note[:1:]] + 12*(int(note[1::])+1)


# main function
def texttotrack(miditext):

    # remove trailing whitespaces
    miditext = miditext.strip()
    print([miditext])


    # remove unwanted whitespaces
    miditext = re.sub(r"\s*:\s*", ":", miditext)
    
    miditext = re.sub(r"\s*#\s*", "#", miditext)
    miditext = re.sub(r"\s*-\s*", "-", miditext)

    # remove time embeddings
    miditext = re.sub(r"\[[^]]*\]", "", miditext)

    midilist = miditext.split()
    partslist = {}

    # cleaning up the string to make a dict
    #midilist = [note.split(':') for note in midilist if (not note.startswith('[')) or note != 'start' or note != 'end'] # remove embeddings as well

    midilist = [note for note in midilist if note != 'start' if note != 'end']

    # getting tempo
    if 'tempo' in midilist[0]:
        tempo = int(midilist.pop(0)[5:])
    else:
        tempo = 120

    midilist = [note.split(':') for note in midilist]


    print(midilist[-1])

    # truncate incomplete ending
    if '' in midilist[-1]:
        res = midilist.pop()
        warn('Ending truncated: {}'.format(res))

    else:
        if 'wait' not in midilist[-1]:
            if len(midilist[-1]) != 3:
                res = midilist.pop()
                warn('Ending truncated: {}'.format(res))

            else:
                # check valid note
                try: 
                    notetonumber(midilist[-1][2])
                except Exception as e:
                    print(e)
                    res = midilist.pop()
                    warn('Ending truncated: {}'.format(res))
                

        else:
            if len(midilist[-1]) != 2:
                res = midilist.pop()
                warn('Ending truncated: {}'.format(res))

    



    for note in midilist:
        if note[0] not in partslist and note[0] != 'wait':
            partslist[note[0]] = []

    for part in partslist:
        for note in midilist:
            if part == note[0]:
                partslist[part].append(':'.join(note[1::]))
            if 'wait' == note[0]:
                partslist[part].append(''.join(note))
    
    # combining waits in a list 
    for part in partslist:  
        copy = [i for i in partslist[part]] 
        count = 0   
        temp = []   
        for i in range(len(copy)):
            current = copy[i+count]
            if not current.startswith('wait'): # not a wait
                temp.append(copy[i+count])
            else: # is a wait
                try:
                    temp.append([int(copy[i+count][4:])])
                    for j in copy[i+count+1:]:
                        if j.startswith('wait'):
                            #print(j)
                            temp[-1].append(int(j[4:]))
                            count += 1
                        else:
                            break
                except:
                    warn('Invalid wait: {}'.format(copy[i+count]))
            if i+count == len(copy) - 1:
                break
        partslist[part] = temp

    # summing waits
    for part in partslist:
        for i in range(len(partslist[part])):
            if isinstance(partslist[part][i], list):
                partslist[part][i] = sum(partslist[part][i]) # waits are stored as int


    # adding waits to notes as dt
    for part in partslist:
        for i in range(len(partslist[part])):

            if not isinstance(partslist[part][i], int): # not wait i.e. note
                try:
                    previous_index = partslist[part][i-1]
                    if isinstance(previous_index, int): # wait dt
                        partslist[part][i] += ':' + str(previous_index)
                    else:
                        partslist[part][i] += ':0'

                except IndexError: # for first index
                    partslist[part][i] += ':0'
    
    # removing waits
    for part in partslist:
        for note in partslist[part]:
            if isinstance(note, int):
                partslist[part].remove(note)
    
    # clean data: only allow parts named melody or accomp
    invalid_keys = [part for part in partslist if part != 'melody' if 'accomp' not in part]
    for key in invalid_keys:
        res = partslist.pop(key, None)
        warn("Removed invalid part: {}; {}".format(key, res))


    temp_partslist = {}
    # translating to message
    for part in partslist:
        temp_partslist[part] = []
        #print(part)
        for i in range(len(partslist[part])):
            try:
            # if note[0] == '0':
            #     msg_type = 'note_off'
            # else:
            #     msg_type = 'note_on'
            # partslist[part][i] = mido.Message(msg_type, note=notetonumber(note[1]), velocity=int(note[0]), time=int(note[2]))
                note = partslist[part][i][1:].split(':')
                #print(note)
                temp_partslist[part].append(mido.Message('note_on', note=notetonumber(note[1]), velocity=int(note[0]), time=int(note[2])))
            except:
                warn("Invalid note: {}, {}".format(part, i, note))
                   
    

    # append tempo
    for part in temp_partslist:
        temp_partslist[part].insert(0, mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(tempo)))

    return temp_partslist


def dicttomidi(outputdict, name):
    midi = mido.MidiFile()
    for part in outputdict:
        track = mido.MidiTrack()
        midi.tracks.append(track)
        track.append(outputdict[part][0]) # tempo
        track.append(mido.Message(type='program_change', program=0))

        for message in outputdict[part][1:]:
            track.append(message)
    midi.save(name)



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', '-f', help='text file')
    parser.add_argument('--text', '-t', help='text string to convert')
    parser.add_argument('--output', '-o', help='name of output file')
    args = parser.parse_args()

    if args.file and args.text:
        raise Exception("Conflict Error: Both --file and --text specified\nPlease only use one option at a time.")


    elif args.text:
        # check if midi file with same name has already exists
        if args.output:
            if not args.output.endswith('.mid'):
                output = '{}.mid'.format(args.output)
                warn('Added ".mid" to ending of args.output: {}'.format(args.output))
            else:
                output = args.output
        
        else:
            # default
            timestamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
            output = 'output-{}.mid'.format(timestamp)
        
        # check if file exists with same output name specified to prevent overwrite
        if isfile(output):
            raise FileExistsError('File already exists with name: {}'.format(output))

        
        # generate midi file
        try:
            dicttomidi(texttotrack(args.text), output)
        
        except:
            print('args.text error: ', sys.exc_info()[0])
            raise


    elif args.file:
        
        # check if args.file is valid
        try:
            f = open(args.file, 'r')
        except FileNotFoundError:
            print('File not found: {}'.format(args.file))
            raise
        

        # validate folder creation to store midi files
        if args.output:
            # create folder with name from args.output
            new_folder_name = args.output

        else:
            # create folder with same name as args.file
            base_input_file = os.path.basename(args.file)
            new_folder_name = os.path.splitext(base_input_file)[0]


        # check if folder with same name already exists
        try:
            os.makedirs(new_folder_name)    
        except FileExistsError:
            # add timestamp at the back to make unique folder name
            timestamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
            corrected_folder_name = '{}-{}'.format(new_folder_name, timestamp)
            warn('Directory "{}" already exists; saving as "{}" instead'.format(new_folder_name, corrected_folder_name))
            os.makedirs(corrected_folder_name)
            new_folder_name = corrected_folder_name


        # generate midi files inside folder
        # each line containing text to generate a midi file
        input_text_list = [line for line in f.read().split('\n') if line != '']
        f.close()
        
        # generate midi files in folder
        for i, text in enumerate(tqdm(input_text_list)):
            # e.g. [args.file]/0.mid
            output = '{}/{}.mid'.format(new_folder_name, i)
            dicttomidi(texttotrack(text), output)


    else:
        raise Exception('Please specify a --file or --text.')


    # print(texttotrack(sample_text))
    # output = open('midioutput.txt','w')
    # output.write(str(texttotrack(sample_text)))