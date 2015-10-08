#!/usr/bin/env python

import xmltodict
from xml.parsers.expat import ExpatError
import os
from warnings import warn
import re
from collections import OrderedDict
from .spchords import SPTranspose

_xmlkeys = ('title', 'author', 'copyright', 'hymn_number', 'presentation',
            'ccli', 'key', 'aka', 'key_line', 'user1', 'user2', 'user3',
            'theme', 'tempo', 'time_sig', 'capo', 'lyrics')
_xmldefaults = ('New Song', '', '', '', '',
                '', '', '', '', '', '', '',
                '', '', '', OrderedDict({'@print': 'false'}), '')


class SPSong(object):
    def __init__(self, **kwargs):
        for key, val in zip(_xmlkeys, _xmldefaults):
            setattr(self, key, val)
        self.filepath = None
        self.mtime = None

    @classmethod
    def read_from_file(cls, filepath):
        '''
        Loads an XML file at filepath to create a Song object. Returns None if
        filepath is not a valid XML.
        '''
        with open(filepath, encoding='UTF-8') as f:
            data = f.read()
            try:
                obj = xmltodict.parse(data)
            except ExpatError:
                return
            songobj = obj['song']
        retval = cls()
        for val in _xmlkeys:
            setattr(retval, val, songobj[val])
        retval.filepath = os.path.abspath(filepath)
        retval.mtime = os.path.getmtime(filepath)
        return retval

    def write_to_file(self, filepath):
        '''
        Write this Song object to an XML file at filepath.
        '''
        songobj = OrderedDict()
        for val in _xmlkeys:
            songobj[val] = getattr(self, val)
        obj = OrderedDict()
        obj['song'] = songobj
        with open(filepath, 'w', encoding='UTF-8') as f:
            f.write(xmltodict.unparse(obj, pretty=True))

    def __repr__(self):
        strrep = "<Song Object - Title: %s" % (self.title)
        if self.author not in (None, ''):
            strrep += ", Author: " + self.author
        strrep += ">"
        return strrep

    @property
    def lyrics(self):
        return "\n".join(self._lyrics)

    @lyrics.setter
    def lyrics(self, val):
        self._lyrics = val.split("\n")

    @property
    def words(self):
        '''
        Returns the words (sans non-lyrical lines) to this song.

        Specifically, removes all lines which:-
        a) Start with '.'
        b) Contains '|' (page split lines)

        Also remove comments, extra whitespace, and the '_' character properly
        '''
        split = self._lyrics
        removed = [line for line in split
                   if len(line) is 0 or
                   (line[0] is not "." and "|" not in line)]
        ret = []
        previousblank = True
        for l in removed:
            l = l.replace("_", "")  # Remove expanders
            l = l.strip()  # Remove whitespace at each end
            while "  " in l:  # Remove all doubled-whitespace characters
                l = l.replace("  ", " ")
            # Remove lines which are only comments
            if ";" in l and l[0] == ";":
                previousblank = True
            l = l.split(';', 1)[0]  # Remove comments
            # Only append blank lines if previous line not blank
            if not previousblank or l != "":
                ret.append(l)
            if len(ret):
                # Check if previous line is blank
                previousblank = ret[-1] == ""
        if len(ret):
            while ret[-1] == "":  # Remove any trailing blank lines
                ret.pop()

        return "\n".join(ret)

    def _split_lyric_line(self, lyricLine, chordLine):
        '''
        Take two matching lyric/chord lines and split up the lyric line
        according to the spacing of the list in chordLine. Returns the
        lyric line as a properly spaced list which matches the spacings
        in chordLine
        '''
        # Check if previous line (lines are currently reversed so
        # that would be the line under this chord line) is a lyric
        # line. It must not be zero length, must have a space
        # space as first character and not have | as second character
        prevLineIsLyric = (len(lyricLine) > 0 and lyricLine[0] == ' ' and
                           lyricLine[1] != '|')
        if prevLineIsLyric:
            splitLyric = []
            index = 1
            for item in chordLine:
                if item != '':
                    splitLyric.append(lyricLine
                                      [index:index+len(item)])
                else:
                    splitLyric.append(lyricLine[index:])
                index += len(item)
            while splitLyric[-1] == '':
                splitLyric.pop()
        else:
            splitLyric = None
        # At this point, splitLyric is either None (no matching lyric
        # line) or contains a list of lyrical elements exactly
        # corresponding to the list in chordLine
        return splitLyric

    def _transpose(self, lyrics, interval, gap=None):
        '''
        Implementation of actual transpose. When run without gap set, will
        simply find default gaps based on existing chords. When run with gap
        set, will try to enforce that particular tone gap. Lyric alignment
        with chords not yet implemented. Will only take place if gap is set.
        '''
        # 'Decouple' lyrics from the input list. Otherwise it does a shallow
        # copy (by ref) and all our edits will be saved on to the input list,
        # which is not the behaviour we want
        lyrics = list(lyrics)
        # Reversing must be done twice so as not to change actual order of
        # lyrics. Purpose is to allow for loop to cross lyric line before
        # reaching the chord line which matches that lyric line. This means
        # we can safely edit the matching lyric line as the loop as passed it
        lyrics.reverse()
        toneGaps = []
        for i, line in enumerate(lyrics):
            if line != "" and line[0] == ".":
                splitLine = re.split('(\S+)', line[1:])
                # If chord-line does not start with space, the above generates
                # a blank initial element. Remove that
                if splitLine[0] == '':
                    splitLine.pop(0)
                if i is not 0:
                    splitLyric = self._split_lyric_line(lyrics[i-1], splitLine)
                else:
                    splitLyric = None
                for n, note in enumerate(splitLine):
                    if not note.isspace() and note != '':
                        t = SPTranspose()
                        newNote = t.transpose_unit(note, interval, gap)
                        curgap = t.get_tone_gap(note, newNote)
                        toneGaps.append(curgap)
                        splitLine[n] = newNote
                        delta = len(newNote) - len(note)
                        if splitLyric is None:
                            continue
                        # Chord is now longer by delta, also check if there's
                        # a next chord, otherwise nothing needs doing
                        if delta > 0 and n+2 < len(splitLyric):
                            # If the next spacing is long enough, just
                            # reduce it sufficiently
                            if len(splitLine[n+1]) > delta:
                                newlen = len(splitLine[n+1]) - delta
                                splitLine[n+1] = ' ' * newlen
                                delta = 0
                            # If it isn't, but is longer than 1 space,
                            # reduce it to 1 space and update delta
                            elif len(splitLine[n+1]) > 1:
                                delta = len(splitLine[n+1]) - 1
                                splitLine[n+1] = ' '
                            finalchar = splitLyric[n+1][-1]
                            firstchar = splitLyric[n+2][0]
                            # Space in front or behind means we can just
                            # add spaces
                            if finalchar.isspace() or firstchar.isspace():
                                splitLyric[n+1] += ' ' * delta
                            # If both are not spaces, then we have to add
                            # an underscore
                            else:
                                splitLyric[n+1] += '_' * delta
                        # Chord is now shorter by negative delta, also check
                        # whether there's a next chord
                        elif delta < 0 and n+2 < len(splitLyric):
                            # Combine to find the total word before the next
                            # chord comes along, to be compared with firstchar
                            word2 = splitLyric[n] + splitLyric[n+1]
                            firstchar = splitLyric[n+2][0]
                            delta = -delta  # invert delta for easier counting
                            while delta > 0:
                                if firstchar.isspace():
                                    if word2[-1].isspace() or word2[-1] == '_':
                                        word2 = word2[:-1]
                                        delta -= 1
                                        continue
                                else:
                                    if word2[-1] == '_':
                                        word2 = word2[:-1]
                                        delta -= 1
                                        continue
                                    elif (word2[-1].isspace() and
                                          word2[-2].isspace()):
                                        word2 = word2[:-1]
                                        delta -= 1
                                        continue
                                # No more opportunity for reducing word, so
                                # have to add spaces to the space after the
                                # chord
                                splitLine[n+1] += ' ' * delta
                                delta = 0
                            # Insert word2 back into splitLyric
                            splitLyric[n+1] = ''
                            splitLyric[n] = word2
                # Recombine splitLine and splitLyric (if needed)
                lyrics[i] = "." + "".join(splitLine)
                if splitLyric:
                    lyrics[i-1] = " " + "".join(splitLyric)
        # Reverse again after modifications done
        lyrics.reverse()
        return (lyrics, toneGaps)

    def transpose(self, interval):
        '''
        Transposes all chords in this song by interval, where interval is an
        integer between -6 and +6 and denotes the number of semi-tones to
        modify all chords by.

        Lyric lines directly below a modified chord line may have spacing
        modified or underscore characters added such that chords are properly
        placed above the matching lyrical lines.
        '''
        # Use the _transpose helper function as multiple runs are needed to
        # guarantee identical tone-gap across the song
        lyrics, toneGaps = self._transpose(self._lyrics, interval)
        if toneGaps.count(toneGaps[0]) != len(toneGaps):
            toneGaps.sort()
            gap = toneGaps[(len(toneGaps)-1)//2]
            gapstore = toneGaps[0] if toneGaps[0] != gap else toneGaps[-1]
            lyrics, toneGaps = self._transpose(self._lyrics, interval, gap)
        if toneGaps.count(toneGaps[0]) != len(toneGaps):
            gap = gapstore
            lyrics, toneGaps = self._transpose(self._lyrics, interval, gap)
        if toneGaps.count(toneGaps[0]) != len(toneGaps):
            warn("Transposition was unable to maintain a suitable tone gap " +
                 "for " + self.__repr__)
        self._lyrics = lyrics
