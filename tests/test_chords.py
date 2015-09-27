#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_chords
----------------------------------

Tests for `chords` module.
"""

import unittest

from songprez import spchords


class TestTranspose(unittest.TestCase):
    '''
    Uses unsupported creation logic to simplify testing. The resulting
    object WILL break if used externally
    '''
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_transpose_note(self):
        t = spchords.SPTranspose()
        assert t._transpose_note('F#', 4) == 'Bb'
        assert t._transpose_note('D#', -2) == 'C#'
        assert t._transpose_note('E', 6) == 'Bb'
        assert t._transpose_note('Ab', 5) == 'C#'
        assert t._transpose_note('Cb', -5) == 'F#'

    def test_transpose_unit(self):
        t = spchords.SPTranspose()
        assert t.transpose_unit('D', 4) == 'F#'
        assert t.transpose_unit('C#m', 1) == 'Dm'
        assert t.transpose_unit('Fm7', 6) == 'Bm7'
        assert t.transpose_unit('F#maj7', -4) == 'Dmaj7'
        assert t.transpose_unit('B7', 2) == 'C#7'
        assert t.transpose_unit('A#sus4', 6) == 'Esus4'
        assert t.transpose_unit('Dsus', 1) == 'Ebsus'
        assert t.transpose_unit('G#aug', 6) == 'Daug'
        assert t.transpose_unit('A+', -5) == 'E+'
        assert t.transpose_unit('D#o', 1) == 'Eo'
        assert t.transpose_unit('Edim', -4) == 'Cdim'
        assert t.transpose_unit('C2', -4) == 'G#2'
        assert t.transpose_unit('G9', 4) == 'B9'
        assert t.transpose_unit('Db6', -1) == 'C6'
        assert t.transpose_unit('B#add2', -2) == 'Bbadd2'
        assert t.transpose_unit('(Cb)', 6) == '(F)'
        assert t.transpose_unit('A/F#', -5) == 'E/C#'
        assert t.transpose_unit('(Fbdim/C)', -2) == '(Ddim/A#)'
        assert t.transpose_unit('Gbsus4/Db', -3) == 'Ebsus4/Bb'
        assert t.transpose_unit('Ebmaj7', -2) == 'C#maj7'
        assert t.transpose_unit('E#add9', -1) == 'Eadd9'
        assert t.transpose_unit('(Bbmaj7/E)', 6) == '(Emaj7/A#)'
        assert t.transpose_unit('(G#7(#6))', 3) == '(B7(#6))'
        assert t.transpose_unit('(Emaj7(#2)/G#)', -1) == '(Ebmaj7(#2)/G)'
        assert t.transpose_unit('A/B', 1) == 'Bb/C'
        assert t.transpose_unit('B/F',-1) == 'Bb/Fb'
        assert t.transpose_unit('A/B#', 2) == 'Cb/D'
        assert t.transpose_unit('B/G',-1) == 'Bb/Gb'
        assert t.transpose_unit('AWord',2) == 'AWord'
        assert t.transpose_unit('notAChord',4) == 'notAChord'
        assert t.transpose_unit('A/B/C',3) == 'A/B/C'

    def test_get_tone_gap(self):
        t = spchords.SPTranspose()
        assert t.get_tone_gap('C#m','Dm') == 1
        assert t.get_tone_gap('F#maj7','Dmaj7') == 5
        assert t.get_tone_gap('B7','C#7') == 1
        assert t.get_tone_gap('A#sus4','Esus4') == 4
        assert t.get_tone_gap('Dsus','D#sus') == 0
        assert t.get_tone_gap('A+','E+') == 4
        assert t.get_tone_gap('D#o','Eo') == 1
        assert t.get_tone_gap('Edim','Cdim') == 5
        assert t.get_tone_gap('C2','G#2') == 4
        assert t.get_tone_gap('G9','B9') == 2
        assert t.get_tone_gap('Db6','C6') == 6
        assert t.get_tone_gap('B#add2','A#add2') == 6
        assert t.get_tone_gap('(Cb)','(F)') == 3
        assert t.get_tone_gap('A/F#','E/C#') == 4
        assert t.get_tone_gap('(Fbdim/C)','(Ddim/A#)') == 5
        assert t.get_tone_gap('Gbsus4/Db','D#sus4/A#') == 4
        assert t.get_tone_gap('Ebmaj7','C#maj7') == 5
        assert t.get_tone_gap('E#add9','Eadd9') == 0
        assert t.get_tone_gap('(Bbmaj7/E)','(Emaj7/A#)') == 3
        assert t.get_tone_gap('NotAChord','C#') == None


if __name__ == '__main__':
    unittest.main()
