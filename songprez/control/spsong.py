#!/usr/bin/env python

import os
from warnings import warn
import re
import sys
if sys.version_info[0] < 3:
    from codecs import open  # 'UTF-8 aware open'
from collections import OrderedDict
from copy import deepcopy
import time
import logging
logger = logging.getLogger(__name__)
from .spchords import SPTranspose
from .sputil import etree

_xmldefaults = OrderedDict((('title', u'New Song'),
                            ('author', u''),
                            ('copyright', u''),
                            ('hymn_number', u''),
                            ('presentation', u''),
                            ('ccli', u''),
                            ('key', u''),
                            ('aka', u''),
                            ('key_line', u''),
                            ('user1', u''),
                            ('user2', u''),
                            ('user3', u''),
                            ('theme', u''),
                            ('tempo', u''),
                            ('time_sig', u''),
                            ('capo_print', False),
                            ('capo', u''),
                            ('lyrics', u''),
                          ))


class SPSong(object):
    xmlparse = 0  # Time taken to parse the XML (including file read)
    relpathfind = 0  # Time taken to find the base directory
    mtimefind = 0  # Time taken to find mtime of the current file

    def __init__(self, **kwargs):
        self.lyrics = u''
        self.filepath = u''
        self.mtime = None

    @classmethod
    def read_from_file(cls, filepath):
        '''
        Loads an XML file at filepath to create a Song object. Returns None if
        filepath is not a valid Unicode XML.
        '''
        starttime = time.time()
        try:
            filepath = unicode(filepath)
        except NameError:
            pass
        retval = cls()
        try:
            root = etree.parse(filepath).getroot()
        except etree.ParseError:
            return
        for elem in root:
            if elem.text is not None:
                if elem.tag in _xmldefaults.keys():
                    if elem.tag == 'capo_print':
                        continue
                    if elem.tag == 'capo':
                        if elem.attrib.get('print') == 'true':
                            setattr(retval, 'capo_print', True)
                        setattr(retval, 'capo', unicode(elem.text))
                        continue
                    setattr(retval, elem.tag, unicode(elem.text))
        cls.xmlparse += time.time() - starttime
        # Find the base OpenSong directory by walking up the path to find the
        # parent of 'Songs'
        basedir, filename = os.path.split(filepath)
        relpath = ''
        while filename != 'Songs':
            if relpath:
                relpath = os.path.join(filename, relpath)
            else:
                relpath = filename
            basedir, filename = os.path.split(basedir)
            if filename == '':
                raise IOError("%s is not in a proper directory structure"
                              % filepath)
        retval.filepath = relpath
        cls.relpathfind += time.time() - starttime
        retval.mtime = os.path.getmtime(filepath)
        cls.mtimefind += time.time() - starttime
        return retval

    def write_to_file(self, filepath):
        '''
        Write this Song object to an XML file at filepath.
        '''

        root = etree.Element('song')
        for key in _xmldefaults.iterkeys():
            if key == 'capo_print':
                continue
            if key == 'capo':
                elem = etree.SubElement(root, 'capo')
                elem.text = self.capo
                elem.attrib['print'] = u'true' if self.capo_print else u'false'
                continue
            etree.SubElement(root, key).text = getattr(self, key)
        tree = etree.ElementTree(root)
        try:
            tree.write(filepath, pretty_print=True,
                       encoding='utf-8', xml_declaration=True)
        except TypeError:
            tree.write(filepath,
                       encoding='utf-8', xml_declaration=True)

    def __repr__(self):
        strrep = "<Song Object - Title: %s" % (self.title)
        if self.author not in (None, ''):
            strrep += ", Author: " + self.author
        strrep += ">"
        return strrep

    def __eq__(self, other):
        '''
        Compares all relevant properties. filepath and mtime do not matter in
        comparing songs for equivalence.
        '''
        for key in _xmldefaults.iterkeys():
            if getattr(self, key) != getattr(other, key):
                return False
        return True

    def __ne__(self, other):
        return not(self.__eq__(other))

    @property
    def title(self):
        return (self._title if hasattr(self, '_title')
                          else _xmldefaults['title'])

    @title.setter
    def title(self, val):
        self._title = val

    @property
    def author(self):
        return (self._author if hasattr(self, '_author')
                          else _xmldefaults['author'])

    @author.setter
    def author(self, val):
        self._author = val

    @property
    def copyright(self):
        return (self._copyright if hasattr(self, '_copyright')
                          else _xmldefaults['copyright'])

    @copyright.setter
    def copyright(self, val):
        self._copyright = val

    @property
    def hymn_number(self):
        return (self._hymn_number if hasattr(self, '_hymn_number')
                          else _xmldefaults['hymn_number'])

    @hymn_number.setter
    def hymn_number(self, val):
        self._hymn_number = val

    @property
    def presentation(self):
        return (self._presentation if hasattr(self, '_presentation')
                          else _xmldefaults['presentation'])

    @presentation.setter
    def presentation(self, val):
        self._presentation = val

    @property
    def ccli(self):
        return (self._ccli if hasattr(self, '_ccli')
                          else _xmldefaults['ccli'])

    @ccli.setter
    def ccli(self, val):
        self._ccli = val

    @property
    def key(self):
        return (self._key if hasattr(self, '_key')
                          else _xmldefaults['key'])

    @key.setter
    def key(self, val):
        self._key = val

    @property
    def aka(self):
        return (self._aka if hasattr(self, '_aka')
                          else _xmldefaults['aka'])

    @aka.setter
    def aka(self, val):
        self._aka = val

    @property
    def key_line(self):
        return (self._key_line if hasattr(self, '_key_line')
                          else _xmldefaults['key_line'])

    @key_line.setter
    def key_line(self, val):
        self._key_line = val

    @property
    def user1(self):
        return (self._user1 if hasattr(self, '_user1')
                          else _xmldefaults['user1'])

    @user1.setter
    def user1(self, val):
        self._user1 = val

    @property
    def user2(self):
        return (self._user2 if hasattr(self, '_user2')
                          else _xmldefaults['user2'])

    @user2.setter
    def user2(self, val):
        self._user2 = val

    @property
    def user3(self):
        return (self._user3 if hasattr(self, '_user3')
                          else _xmldefaults['user3'])

    @user3.setter
    def user3(self, val):
        self._user3 = val

    @property
    def theme(self):
        return (self._theme if hasattr(self, '_theme')
                          else _xmldefaults['theme'])

    @theme.setter
    def theme(self, val):
        self._theme = val

    @property
    def tempo(self):
        return (self._tempo if hasattr(self, '_tempo')
                          else _xmldefaults['tempo'])

    @tempo.setter
    def tempo(self, val):
        self._tempo = val

    @property
    def time_sig(self):
        return (self._time_sig if hasattr(self, '_time_sig')
                          else _xmldefaults['time_sig'])

    @time_sig.setter
    def time_sig(self, val):
        self._time_sig = val

    @property
    def capo_print(self):
        return (self._capo_print if hasattr(self, '_capo_print')
                          else _xmldefaults['capo_print'])

    @capo_print.setter
    def capo_print(self, val):
        self._capo_print = val

    @property
    def capo(self):
        return (self._capo if hasattr(self, '_capo')
                          else _xmldefaults['capo'])

    @capo.setter
    def capo(self, val):
        self._capo = val

    @property
    def lyrics(self):
        return u"\n".join(self._lyrics)

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
        return self.remove_chords(u"\n".join(self._lyrics))

    def remove_chords(self, text):
        split = text.split("\n")
        removed = [line for line in split
                   if len(line) is 0 or
                   (line[0] != "." and "||" not in line)]
        ret = []
        previousblank = True
        for l in removed:
            l = l.replace("_", "")  # Remove expanders
            l = l.replace("|", "")  # Remove vertical spacers
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
        return u"\n".join(ret)


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
        set, will try to enforce that particular tone gap.
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
        # Enforce 'int' for interval
        interval = int(interval)
        # Use the _transpose helper function as multiple runs are needed to
        # guarantee identical tone-gap across the song
        lyrics, toneGaps = self._transpose(self._lyrics, interval)
        if len(toneGaps) == 0:
            # Nothing to transpose
            return
        if toneGaps.count(toneGaps[0]) != len(toneGaps):
            # First, try the more common gap
            toneGaps.sort()
            gap = toneGaps[(len(toneGaps)-1)//2]
            gapstore = toneGaps[0] if toneGaps[0] != gap else toneGaps[-1]
            lyrics, toneGaps = self._transpose(self._lyrics, interval, gap)
        if toneGaps.count(toneGaps[0]) != len(toneGaps):
            # Next, try the alternative gap
            lyrics, toneGaps = self._transpose(self._lyrics, interval,
                                               gapstore)
        if toneGaps.count(toneGaps[0]) != len(toneGaps):
            # If all else fails, print a warning and use the original gap
            logger.error('SPSong: Transposing %s with interval %d, could not' +
                         ' maintain suitable tone gap', str(self), interval)
            lyrics, _ = self._transpose(self._lyrics, interval, gap)
        t = SPTranspose()
        self.key = t.transpose_unit(self.key, interval, toneGaps[0])
        self._lyrics = lyrics

    def split_slides(self, presentation=None):
        '''
        Splits the lyrics into multiple slides. Optionally re-orders using
        presentation (priority given to presentation input, otherwise use
        instance presentation settings).

        Returns a list of {marker, string, startLine, endLine} objects.
        '''
        # Go through lines, get markers/splits
        # Also keep a record of which object is in which Marker
        limit = len(self._lyrics)
        slides = []
        template = {'marker': u'', 'string': [], 'start': None, 'end': None}
        slides.append(deepcopy(template))
        slides[-1]['start'] = 0
        for i, l in enumerate(self._lyrics):
            if len(l) > 0 and l[0] == "[":  # A marker
                # Mark previous line as end (if exists)
                slides[-1]['end'] = i-1 if i else 0
                # Create new object
                slides.append(deepcopy(template))
                # Set the marker
                marker = re.search(r"\[([A-Za-z0-9 ]+)\]", l)
                marker = marker.group(1) if marker else u''
                slides[-1]['marker'] = marker
                # Mark next line as start (if exists)
                slides[-1]['start'] = i+1 if i+1 < limit else limit-1
            elif l.lstrip()[0:2] == '||':  # Manual slide split
                # Get previous marker (may be blank)
                marker = slides[-1]['marker']
                # Mark previous line as end (if exists)
                slides[-1]['end'] = i-1 if i else 0
                # Create new object with the same marker
                slides.append(deepcopy(template))
                slides[-1]['marker'] = marker
                # Mark next line as start (if exists)
                slides[-1]['start'] = i+1 if i+1 < limit else limit-1
            else:  # Just a normal line, add it
                # Add this line to the current object's string list
                slides[-1]['string'].append(l)
                # Mark this line as end (just in case its the last line, will
                # be overwritten in any case if that's not true
                slides[-1]['end'] = i
        # Remove any objects which have less than one line
        for o in slides[:]:  # Operate on a copy
            if o['end'] - o['start'] < 1:
                slides.remove(o)
        for o in slides:  # Convert to string, strip extra blank lines
            for s in o['string']:  # strip from start
                if s.isspace() or s == u'':
                    o['start'] += 1
                else:
                    break
            for s in reversed(o['string']):  # strip from end
                if s.isspace() or s == u'':
                    o['end'] -= 1
                else:
                    break
            o['string'] = u"\n".join(o['string']).strip("\n")
        # If no presentation, set presentation to be the song's own preset
        # presentation order
        if not presentation:
            presentation = self.presentation
        # If presentation is still not set, just return what we have
        if not presentation:
            return slides
        # At this point, there is a presentation string. Split it into markers
        markers = presentation.split(' ')
        newslides = []
        for m in markers:  # Operate on a copy
            if m:  # Ignore blank markers, indicates extra spaces
                for s in slides:
                    # Iterate through slides, add each object (separately) to
                    # newslides if it matches the current marker
                    if m == s['marker']:
                        newslides.append(s)
        return newslides
