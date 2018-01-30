import sys, os

from phoer import PhoSong

TIMEWARP = 0.5
MAX_WAIT_LEN = 10000
DIR_NAME = "text2pho"


if len(sys.argv) < 2:
    print("No File!")
    quit()
FILENAME = sys.argv[1]

# converts midi file to text note representation
command = "./"+DIR_NAME+"/midi2notes " + FILENAME
miditext = os.popen(command).read()
notes = miditext.split("\n")
tracks = set([])

# checks for tracks in the midi file
for note in notes:
    words = note.split()

    if len(words) < 5:
        continue

    track = int(words[4])
    if track not in tracks:
        tracks.add(track)

print("Found", tracks, "MIDI tracks")

# puts notes to the PhoSong
song = PhoSong(TIMEWARP)
for track in tracks:
    VOCAL = "a:"
    phoText = ""

    lastTime = 0
    for note in notes:
        words = note.split()

        if len(words) < 5:
            continue

        if (int(words[4]) == track):
            beg = int(words[1])
            end = int(words[2])
            tone = int(words[3])

            if end - beg == 0:
                continue

            song.addNote(tone, beg, end, track)

# checks the number of mono tracks
tracks = set(song.tracks.keys())
print("Converted to", tracks, "mono tracks")

# creates wav file
outFileName = ".".join(FILENAME.split(".")[:-1])
song.makeWav(DIR_NAME, outFileName)
