vocab = {'[CLS':0,'[SEP]':1,'PAD':2,'[UNK]':3,'start':4,'end':5,'melody':6}

# accomp0 - accomp19
accomps = {}
for i in range(20):
    accomps['accomp'+str(i)] = 7+i

vocab.update(accomps)

# tempo10 - 200
tempos = {}
for i in range(10, 201):
    tempos['tempo'+str(i)] = 7+20 + (i-10)
vocab.update(tempos)

# v0 - v127
vels = {}
for i in range(128):
    vels['v'+str(i)] = 7+20+191+i
vocab.update(vels)

# note 1-88
notes = {'A0':7+20+191+128, 'A#0':7+20+191+128+1, 'B-0':7+20+191+128+2, 'B0':7+20+191+128+3}
note_letters = ['C','C#','D-','D','D#','E-','E','F-','E#','F','F#','G-','G','G#','A-','A','A#','B-','B','B#','C-'] # len:21
for i in range(1,8): # 12 * 8 = 87 = 88-2
    for j, n in enumerate(note_letters):
        notes[n+str(i)] = 7+20+191+128+3 + (i-1)*21 + j

notes['C8'] = 7+20+191+128+3+21*8
vocab.update(notes)

# wait (0-5000)
waits = {}
for i in range(5001):
    waits['wait:'+str(i)] = 7+20+191+128+3+21*8+1 + i
vocab.update(waits)

# time embeddings
time_embeds = {}
for i in range(128):
    time_embeds['[{}]'.format(i)] = 7+20+191+128+3+21*8+1+5001 + i
vocab.update(time_embeds)

import json
with open('vocab.json', 'w') as f:
    json.dump(vocab, f)