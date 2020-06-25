import mido

import sys
import os
from os.path import isfile
from warnings import warn

import datetime

import argparse
from tqdm import tqdm

# hard coded stuff
notetonumberacc = {'C#':1,'D-':1,'D#':3,'E-':3,'F#':6,'G-':6,'G#':8,'A-':8,'A#':10,'B-':10, 'C-':-1, 'F-':4, 'B#':12, 'E#':5} 
notetonumbernat = {'C':0,'D':2,'E':4,'F':5,'G':7,'A':9,'B':11,}

# sample
# sample_text = 'start tempo120 melody:v72:G4 accomp0:v72:D3 accomp1:v72:G3 wait:96 melody:v0:G4 melody:v72:A4 wait:96 melody:v0:A4 melody:v72:B4 accomp0:v0:D3 accomp0:v72:D3 accomp1:v0:G3 accomp1:v72:B3 wait:192 melody:v0:B4 accomp0:v0:D3 accomp1:v0:B3 end'

# converts from musical notation to midi numbers
def notetonumber(note):

    if '-' in note or '#' in note: # test for accidentals
        # check if octave missing
        if note[2:] == '':
            print(note)

        return notetonumberacc[note[:2:]] + 12*(int(note[2::])+1)

    else: # no accidentals
        # check if octave missing
        if note[1:] == '':
            print(note)

        return notetonumbernat[note[:1:]] + 12*(int(note[1::])+1)


# main function
def texttotrack(miditext):
    midilist = miditext.split()
    partslist = {}

    # cleaning up the string to make a dict
    midilist = [note.split(':') for note in midilist if not note.startswith('[')] # remove embeddings as well

    # getting tempo
    if 'tempo' in midilist[0][0]:
        tempo = int(midilist.pop(0)[0][5:])
    else:
        tempo = 120

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
                temp.append([int(copy[i+count][4::])])
                for j in copy[i+count+1:]:
                    if j.startswith('wait'):
                        temp[-1].append(int(j[4::]))
                        count += 1
                    else:
                        break
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
    
    # translating to message
    for part in partslist:
        print(part)
        for i in range(len(partslist[part])):
            note = partslist[part][i][1:].split(':')
            print(i, note)
            # if note[0] == '0':
            #     msg_type = 'note_off'
            # else:
            #     msg_type = 'note_on'
            # partslist[part][i] = mido.Message(msg_type, note=notetonumber(note[1]), velocity=int(note[0]), time=int(note[2]))
            partslist[part][i] = mido.Message('note_on', note=notetonumber(note[1]), velocity=int(note[0]), time=int(note[2]))            


    # append tempo
    for part in partslist:
        partslist[part].insert(0, mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(tempo)))

    return partslist


def dicttomidi(outputdict, name):
    midi = mido.MidiFile()
    for part in outputdict:
        track = mido.MidiTrack()
        midi.tracks.append(track)
        track.append(mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(120)))
        track.append(mido.Message(type='program_change', program=0))
        
        for message in outputdict[part]:
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
        input_text_list = f.read().split('/n')
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