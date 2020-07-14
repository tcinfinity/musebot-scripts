vocab = ['[CLS]','[SEP]','[PAD]','[UNK]','start','end','melody']

# accomp0 - accomp19
for i in range(20):
    vocab.append('accomp'+str(i))

# tempo10 - 200
for i in range(10, 201):
    vocab.append('tempo'+str(i))

# v0 - v127
for i in range(128):
    vocab.append('v'+str(i))

# note 1-88
vocab.extend(['A0', 'A#0', 'B-0', 'B0'])

note_letters = ['C','C#','D-','D','D#','E-','E','F-','E#','F','F#','G-','G','G#','A-','A','A#','B-','B','B#','C-'] # len:21
for i in range(1,8): # 12 * 8 = 87 = 88-2
    for j, n in enumerate(note_letters):
        vocab.append(n+str(i))

vocab.append('C8')

# wait (0-5000)
for i in range(5001):
    vocab.append('wait:'+str(i))

# time embeddings
for i in range(128):
    vocab.append('[{}]'.format(i))

with open('training_vocab.txt', 'w') as f:
    f.write('\n'.join(vocab))