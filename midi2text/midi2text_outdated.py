import mido
midifile = mido.MidiFile('fw_rain.mid')

midi = mido.MidiFile()

textlist = []

def texttomsg(msg):
    for i in range(len(msg)):
        if not msg[i].isdigit():
            msg = msg[:i] + '#' + msg[i + 1:]
    
    numlist =  [int(x) for x in msg[1::].split('#')]

    return mido.Message('note_on', note=numlist[0], velocity=numlist[1], time=numlist[2])

midistring = 'n91v112t25 n91v0t455 n89v112t25 n89v0t455 n86v112t25 n86v0t227 n87v112t13 n87v0t911 n60v112t13 n59v112t0 n60v0t227 n58v112t13 n58v0t227 n55v112t13 n55v0t227 n67v112t13 n67v0t227 n65v126t13 n65v0t227 n67v126t13 n67v0t227 n74v126t13 n74v0t455 n75v126t25 n75v0t455 n72v126t25 n72v0t911 n60v126t37 n59v126t0 n60v0t455 n67v127t25 n67v0t227 n79v126t13 n79v0t683 n77v127t25 n79v0t911 n63v126t25 n67v0t227 n75v126t13 n75v0t227 n70v126t13 n74v126t0 n67v126t0 n75v126t0 n74v0t911 n70v126t25 n74v126t0 n67v0t227 n75v126t13 n75v0t227 n79v126t13 n79v0t683 n82v126t25 n82v0t227 n82v126t13 n82v0t227 n82v126t13 n82v0t227 n82v126t13 n82v0t227 n80v126t13 n80v0t227 n79v126t13 n79v0t911 n77v126t25 n75v126t0 n79v126t0 n79v0t911 n75v126t25 n75v0t227 n72v126t13 n74v126t0 n72v0t911 n72v126t25 n74v126t0 n60v126t0 n72v0t455 n74v0t0 n60v0t2279 n74v0t0 n62v126t73 n62v0t227 n63v126t13 n63v0t227 n67v126t13 n67v0t227 n65v126t13 n65v0t227 n67v126t13 n67v0t227 n74v126t13 n74v0t455 n75v126t25 n75v0t227 n70v126t13 n74v126t0 n82v126t0 n70v0t68v0 n70v126t25 n74v126t0 n82v0t227 n74v126t13 n74v0t1539 n75v126t0 n82v126t0 n75v0t0 n70v126t25 n82v0t227 n82v126t13 n82v0t683 n80v126t25 n80v0t227 n79v126t13 n79v0t683 n77v126t25 n75v126t0 n79v126t0 n77v0t911 n75v0t0 n79v0t0 n70v126t2425 n82v126t0 n70v0t455 n82v0t0 n63v126t25 n75v126t0 n63v0t455 n75v0t0 n67v126t25 n79v126t0 n67v0t455 n79v0t0 n70v126t2425 n82v126t0 n70v0t455 n82v0t0 n63v126t25 n75v126t0 n63v0t455 n75v0t0 n67v126t25 n79v126t0 n67v0t455 n79v0t0 n87v126t2425 n87v0t455 n94v126t25 n94v0t455 n84v126t25 n84v0t455 n82v126t25 n82v0t455 n82v126t25 n82v0t227 n80v126t13 n80v0t227 n67v126t13 n67v0t227 n67v126t13 n67v0t227 n65v126t13 n65v0t227 n67v126t13 n67v0t227 n65v126t13 n67v0t227 n67v126t13 n67v0t227'


mid = mido.MidiFile()
track = mido.MidiTrack()
mid.tracks.append(track)

midilist = midistring.split(' ')

for i in range(len(midilist)):
        midilist[i] = texttomsg(midilist[i])
        print(midilist[i])

for i in midilist:
    mid.tracks[0].append(i)

mid.save('helpme.mid')

# for i, track in enumerate(midifile.tracks):
#     midi.tracks.append(mido.MidiTrack())
#     for msg in track:
#         if msg.type == 'program_change' and msg.channel != 10:
#             msg.program=50
#         if msg.type == 'note_on':
#             msg.channel = i
#             textlist.append('n{}v{}t{}'.format(msg.note, msg.velocity, msg.time))
#             # print('Channel {}: n{}v{}t{}'.format(msg.channel, msg.note, msg.velocity, msg.time)) 
#         print(msg)
#         midi.tracks[i].append(msg)

# output_file = open('textmidi.txt','w')
# output_file.write(' '.join(textlist))
# output_file.close()

# midi.save('output.mid')

# port = mido.open_output()

# outputfile = mido.MidiFile('output.mid')

# for msg in outputfile.play():
#     port.send(msg)

