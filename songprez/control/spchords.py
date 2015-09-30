#!/usr/bin/env python

import re

# _notes is loosely preferred over _eqvnotes. Some decisions here are quite
# arbitrary (esp G# over Ab) while some are uncontroversial (Bb over A#).
_notes = ('A', 'Bb', 'B', 'C', 'C#', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'G#')
_eqvnotes = ('A', 'A#', 'Cb', 'B#', 'Db', 'D', 'D#', 'Fb', 'E#', 'Gb', 'G',
             'Ab')


class SPTranspose(object):
    def _legal_unit(self, unit):
        '''
        Checks if unit is a string containing a music chord. Returns None
        if it isn't, otherwise it returns a tuple containing the prepending
        text ('(' or ''), the note itself, and the appending text.
        '''
        # First match against an optional initial (, a note, and a following
        # part which will be checked later
        chordRegex = re.match("(\(?)([A-G][#b]?)(.*)", unit)
        if not chordRegex:
            return None
        # Check the latter part, which can only contain some combination of
        # sus, maj, m, aug, dim, add, +, o, #, b and numbers
        check = re.sub('sus|maj|m|aug|dim|add|\+|o|[0-9]|\(|\)|#|b', '',
                       chordRegex.groups()[2])
        if check != '':
            return None
        else:
            return chordRegex.groups()

    def _transpose_note(self, note, interval, gap=None):
        '''
        Given a legal note and an interval, return that note after
        transposition by the given interval. Preferential order of return
        specified according to _notes, with alternatives given in _eqvnotes.
        '''
        try:
            initial = _notes.index(note)
        except ValueError:
            initial = _eqvnotes.index(note)
        final = (initial + interval) % len(_notes)
        candidate = _notes[final]
        if gap is not None and self.get_tone_gap(note, candidate) != gap:
            return _eqvnotes[final]
        else:
            return candidate

    def transpose_unit(self, unit, interval, gap=None):
        '''
        Given a possible chord unit and an interval, return the same chord unit
        after transposition by the given interval, or return the original unit
        if not a legal unit for transposition.
        '''
        if unit.count('/') > 1:
            return unit
        if '/' in unit:
            index = unit.find('/')
            chord = unit[:index]
            bass = unit[index+1:]
            transChord = self.transpose_unit(chord, interval, gap)
            if gap is None:
                gap = self.get_tone_gap(chord, transChord)
            transBass = self.transpose_unit(bass, interval, gap)
            if gap != self.get_tone_gap(bass, transBass):
                gap = self.get_tone_gap(bass, transBass)
                transChord = self.transpose_unit(chord, interval, gap)
            return transChord + '/' + transBass
        else:
            chordGroups = self._legal_unit(unit)
            if chordGroups is None:
                return unit
            else:
                pre, note, post = chordGroups
                trans = self._transpose_note(note, interval, gap)
                return pre + trans + post

    def get_tone_gap(self, initial, transposed):
        '''
        Given two chord units, find the number of tones between them. Returns
        between 0 and 6 inclusive.
        '''
        if '/' in initial:
            index = initial.find('/')
            init = self._legal_unit(initial[:index])
        else:
            init = self._legal_unit(initial)
        if '/' in transposed:
            index = transposed.find('/')
            tran = self._legal_unit(transposed[:index])
        else:
            tran = self._legal_unit(transposed)
        if init is None or tran is None:
            return None
        else:
            # ord converts letters to numbers
            return (ord(tran[1][0]) - ord(init[1][0])) % 7
