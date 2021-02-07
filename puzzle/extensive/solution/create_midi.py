# file from https://github.com/noopkat/oled-font-5x7/blob/master/oled-font-5x7.js
# hack to make it execable
replace = {
'module.exports': 'font',
'true': 'True',
'//': '#',
'monospace': '"monospace"',
'width': '"width"',
'height': '"height"',
'fontData': '"fontData"',
'lookup': '"lookup"',
}
s = open("oled-font-5x7.js").read()
for i in replace:
    s = s.replace(i, replace[i])
exec(s)

target1 = "The first amazing letter is A"
grid = []
for i in target1:
    ind = font["lookup"].index(i)
    grid += font["fontData"][5*ind:5*ind+5] + [0]
grid = grid[:-1]

target2 = 'The second amazing letter is C'

target3 = 'thethirdamazingletterish'
instruments = []
for i in target3:
    instrument = ord(i) - ord('a')
    assert 0 <= instrument <= 25
    instruments.append(instrument)

# assign channels to used tracks in increasing order
free_channel = 1
channels = {0: 0}
for i in sorted(set(instruments)):
    channels[i+1] = free_channel
    free_channel += 1
    # skip percussion channel
    if free_channel == 9:
        free_channel += 1

note_length = 200
shift_amount = 20 # shift so notes don't end up in the same timestep
events = [] # (absolute time, track, event type, data)
inst_index = 0
for j in range(len(grid)):
    for i in range(7):
        time = j*note_length + i*shift_amount
        if grid[j] & (1 << i):
            events.append([time, instruments[inst_index]+1, 'note_on', 66-i])
            events.append([time+note_length-1, instruments[inst_index]+1, 'note_off', 66-i])
            inst_index = (inst_index+1) % len(instruments)

for i in range(len(target2)):
    events.append([i*1000, 0, 'lyric', target2[i]])

events = sorted(events)

from mido import Message, MetaMessage, MidiFile, MidiTrack

mid = MidiFile(type=1)
tracks = [MidiTrack() for i in range(27)]
for i in range(len(tracks)):
    track = tracks[i]
    mid.tracks.append(track)

for i in sorted(set(instruments)):
    tracks[i+1].append(Message('program_change', program=i, time=0, channel=channels[i+1]))

ts = [0]*27
for event in events:
    dt = event[0] - ts[event[1]]
    ts[event[1]] = event[0]
    track = tracks[event[1]]
    if event[2] == 'note_on':
        track.append(Message('note_on', note=event[3], velocity=127, time=dt, channel=channels[event[1]]))
    elif event[2] == 'note_off':
        track.append(Message('note_off', note=event[3], velocity=127, time=dt, channel=channels[event[1]]))
    elif event[2] == 'lyric':
        track.append(MetaMessage('lyrics', text=event[3], time=dt))
    else:
        1/0

mid.save('puzzle.mid')
