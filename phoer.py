from scipy import vstack, zeros
import numpy as np
from scipy.io import wavfile
import os

from intervaltree import Interval, IntervalTree


class PhoSong:
    def __init__(self, timewarp=1, ctone=146.8):
        self.tracks = {}
        self.timewarp = timewarp
        self.waitMaxLen = 10000
        self.ctone = ctone
        self.halftone = (2**(1/12))
        self.ownTrackOffset = 100
        self.ownTrackCounter = 0
        pass


    def addNote(self, note, beg, end, prefTrack):
        """Adds note to the preffered Mono track. If the track is full, creates new track."""
        if prefTrack not in self.tracks:
            self.createTrack(prefTrack)

        noteRep = self.note2freq(note)

        if self.fitsIn(beg, end, prefTrack):
            self.tracks[prefTrack][beg:end] = noteRep
            return

        for trackNum in range(self.ownTrackOffset, self.ownTrackOffset+self.ownTrackCounter):
            if self.fitsIn(beg, end, trackNum):
                self.tracks[trackNum][beg:end] = noteRep
                return

        newTrackNum = self.createTrack()
        self.tracks[newTrackNum][beg:end] = noteRep
        return


    def note2freq(self, note):
        """converts note number to frequency"""
        delta = note - 60
        return int(self.ctone * self.halftone ** delta)

    def fitsIn(self, beg, end, track):
        if track not in self.tracks:
            return False

        return not bool(self.tracks[track][beg:end])

    def createTrack(self, trackName=None):
        if trackName is None:
            trackName = self.ownTrackOffset + self.ownTrackCounter
            self.ownTrackCounter += 1

        self.tracks[trackName] = IntervalTree()
        return trackName

    def dumpPhos(self, DIR_NAME):
        """Creates the .pho files necessary for mbrola"""
        TIMEWARP = self.timewarp
        MAX_WAIT_LEN = self.waitMaxLen
        for track in self.tracks.keys():
            VOCAL = "a:"
            phoText = ""

            lastTime = 0
            for intItem in sorted(self.tracks[track]):
                beg, end, freq = intItem
                beg = int(beg*TIMEWARP)
                end = int(end*TIMEWARP)

                while lastTime < beg:
                    d = beg - lastTime
                    if d > MAX_WAIT_LEN:
                        phoText += "_ " + str(MAX_WAIT_LEN) + "\n"
                        lastTime += MAX_WAIT_LEN
                    else:
                        phoText += "_ " + str(beg - lastTime) + "\n"
                        lastTime += beg - lastTime

                lastTime = end

                phoText += VOCAL + " " + str(end - beg)
                phoText += " 0 " + str(freq)
                phoText += " 100 " + str(freq) + "\n"

            phoFName = DIR_NAME + "/track" + str(track) + ".pho"
            with open(phoFName, "w") as f:
                f.write(phoText)

    def makeWav(self, DIR_NAME, filename):
        """Converts the tracks to wav using mbrola"""
        self.dumpPhos(DIR_NAME)

        # print(self.tracks)

        melodys = []
        sizes = []
        for track in self.tracks.keys():
            print("Mbroling track", track)
            phoFName = DIR_NAME + "/track" + str(track) + ".pho"
            command = "./"+DIR_NAME+"/translate.sh " + phoFName
            cmdOut = os.popen(command).read()
            if cmdOut != "":
                print(cmdOut)

            wavFName = DIR_NAME + "/track" + str(track) + ".wav"
            rate, a = wavfile.read(wavFName)
            melodys.append(a)
            sizes.append(a.size)

        comSize = max(sizes)
        melodys = [np.append(x, zeros((comSize - x.size, 1), dtype=x.dtype)) for x in melodys]

        outWav = vstack(melodys)
        outFileName = filename + ".wav"
        wavfile.write(outFileName, rate, outWav.transpose())
