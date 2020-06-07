track2 = 'accomp0:v72:D3 wait:96 wait:96 accomp0:v0:D3 accomp0:v72:D3 wait:192 accomp0:v0:D3'

track2 = track2.split(' ')

print(track2)

# ill do the while one

temp = []
track = [i for i in track2] # copy for immutability
while len(track) > 0:
    current = track.pop(0)
    if current.startswith('accomp0'):
        temp.append(current)
    else:
        temp.append([current])
        for x in track:
            if x.startswith('wait'):
                new = track.pop(0)
                temp[-1].append(new)
            else:
                break


print(temp)


track = [i for i in track2]
count = 0
temp = []
for i in range(len(track)):
    current = track[i+count]
    if current.startswith('accomp0'):
        temp.append(track[i+count])
    else: # startswith wait
        temp.append([track[i+count]]) #note the array
        for x in track[i+count+1:]:
            if x.startswith('wait'):
                temp[-1].append(x)
                count += 1
            else:
                break
    if i+count == len(track) - 1:
        break
        

print(temp)
# I HATE THIS METHOD ^