from music21 import *
import glob
import pickle


# midi = converter.parse('samplemidi.mid')
# midi.translate.instrumentToMidiEvents



score = converter.parse('samplemidi.mid')
components = []
for element in score.recurse():
    components.append(element)
    if 'Stream' in element.classes:
        mf = midi.translate.streamToMidiFile(element)
        print(mf.tracks)
        print(mf.tracks[0].events)
        
    print(element)
    print(element.classes)


# notes = []
# for file in glob.glob("*.mid"):

#     midi = converter.parse(file)
#     print("Parsing %s" % file)
#     notes_to_parse = None
#     try: 
#         s2 = instrument.partitionByInstrument(midi)
#         notes_to_parse = s2.parts[0].recurse() 
#     except: 
#         notes_to_parse = midi.flat.notes
#     for element in notes_to_parse:
#         if isinstance(element, note.Note):
#             notes.append(str(element.pitch))
#         elif isinstance(element, chord.Chord):
#             notes.append('.'.join(str(n) for n in element.normalOrder))

# print(notes)