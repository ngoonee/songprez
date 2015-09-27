#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_spsong
----------------------------------

Tests for `spsong` module.
"""

import unittest
import os

from songprez import spsong
from songprez.spsong import SPSong

def test_song_read_write(tmpdir):
    p = tmpdir.mkdir('songtest')
    s = SPSong()
    for item in spsong._xmlkeys:
        setattr(s, item, "test")
    s.write_to_file(p.join('test').__str__())
    s2 = SPSong.read_from_file(p.join('test').__str__())
    for item in spsong._xmlkeys:
        assert getattr(s, item) == getattr(s2, item)

class TestSongObject(unittest.TestCase):
    '''
    Uses unsupported creation logic to simplify testing. The resulting
    object WILL break if used externally
    '''
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_str_repr(self):
        s = SPSong()
        assert s.__repr__() == "<Song Object - Title: New Song>"

    def test_chord_removal(self):
        s = SPSong()
        l = []
        l.append("[V]")
        l.append(".C D/F#     F G")
        l.append(" First line of   song")
        l.append(".E G# Bbo")
        l.append(" Secon_d l__ine")
        l.append("")
        l.append("")
        l.append("[C]")
        l.append(".G F Eb Am")
        l.append(" The  chorus starts!  ")
        l.append("; A comment line is here")
        l.append(".F F     C/E D/F#")
        l.append(" End of our  s__ong")
        l.append('')
        s.lyrics = "\n".join(l)
        l2 = []
        l2.append("[V]")
        l2.append("First line of song")
        l2.append("Second line")
        l2.append("")
        l2.append("[C]")
        l2.append("The chorus starts!")
        l2.append("End of our song")
        assert s.words == "\n".join(l2)

    def test_transpose(self):
        s = SPSong()
        l = []
        l.append(".        Esus4 E   D#o G#7(#5) C#m7")
        l.append(" You are ho____ly, ho__________ly")
        l.append(".F#m7           E         Dmaj7 A/B")
        l.append(" Lord, there is none like You")
        l.append(".        Esus4 E   D#o G#7(#5) C#m7")
        l.append(" You are ho____ly, ho__________ly")
        l.append(".F#m7     A/B  E    A/B")
        l.append(" Glory to You alone")
        s.lyrics = "\n".join(l)
        s.transpose(4)
        l = []
        l.append(".        Absus4 Ab  Go C7(#5) Fm7")
        l.append(" You are ho_____ly, ho________ly")
        l.append(".Bbm7           Ab        Gbmaj7 Db/Eb")
        l.append(" Lord, there is none like You")
        l.append(".        Absus4 Ab  Go C7(#5) Fm7")
        l.append(" You are ho_____ly, ho________ly")
        l.append(".Bbm7     Db/Eb Ab    Db/Eb")
        l.append(" Glory to You a_lone")
        assert s.lyrics == "\n".join(l)

    def test_transpose_spacing(self):
        s = SPSong()
        l = []
        l.append(".               D   A G          D  A G")
        l.append(" It's all about You,   All about You")
        l.append(".               Bm  A/F# G/E A D  G/A")
        l.append(" It's all about You,         Jesus")
        s.lyrics = "\n".join(l)
        s.transpose(-4)
        l = []
        l.append(".               Bb  F Eb         Bb  F Eb")
        l.append(" It's all about You,   All about You")
        l.append(".               Gm  F/D Eb/C F Bb  Eb/F")
        l.append(" It's all about You,         Jesus")
        assert s.lyrics == "\n".join(l)
        s = SPSong()
        l = []
        l.append(".  C    F   C    Am Dm G   C")
        l.append(" O God, our help in a__ges past")
        l.append(".    Am   Em  Am    D  G")
        l.append(" Our hope for years to come")
        s.lyrics = "\n".join(l)
        s.transpose(-2)
        l = []
        l.append(".  Bb   Eb  Bb   Gm Cm F   Bb")
        l.append(" O God, our help in a__ges past")
        l.append(".    Gm   Dm  Gm    C  F")
        l.append(" Our hope for years to come")
        assert s.lyrics == "\n".join(l)
        s = SPSong()
        l = []
        l.append(".Ebmaj7 Bb/D Ebmaj7 Bb/D Ebmaj7 Gm Fm")
        l.append(" Ma_____ker  of     the  u______ni_verse")
        l.append(".Ebmaj7 Bb/D Ebmaj7 Bb/D Ebmaj7 Gm  Fm")
        l.append(" Come   to   us,    by   Vir____gin birth")
        l.append(".Bb Bb2/D Bb   Eb2     Gm   Ebmaj7  Fsus F")
        l.append(" Je_______sus, Lord of all (Lord of all)")
        s.lyrics = "\n".join(l)
        s.transpose(1)
        l = []
        l.append(".Emaj7 B/D# Emaj7 B/D# Emaj7 G#m F#m")
        l.append(" Ma____ker  of    the  u_____ni__verse")
        l.append(".Emaj7 B/D# Emaj7 B/D# Emaj7 G#m F#m")
        l.append(" Come  to   us,   by   Vir___gin birth")
        l.append(".B B2/D# B    E2      G#m  Emaj7   F#sus F#")
        l.append(" Je______sus, Lord of all (Lord of all)")
        assert s.lyrics == "\n".join(l)
        s = SPSong()
        l = []
        l.append(".Ebmaj7 Bb/D Ebmaj7 Bb/D Ebmaj7 Gm Fm")
        l.append(" Ma_____ker  of     the  u______ni_verse")
        l.append(".Ebmaj7 Bb/D Ebmaj7 Bb/D Ebmaj7 Gm  Fm")
        l.append(" Come   to   us,    by   Vir____gin birth")
        l.append(".Bb Bb2/D Bb   Eb2     Gm   Ebmaj7  Fsus F")
        s.lyrics = "\n".join(l)
        s.transpose(1)
        l = []
        l.append(".Emaj7 B/D# Emaj7 B/D# Emaj7 G#m F#m")
        l.append(" Ma____ker  of    the  u_____ni__verse")
        l.append(".Emaj7 B/D# Emaj7 B/D# Emaj7 G#m F#m")
        l.append(" Come  to   us,   by   Vir___gin birth")
        l.append(".B B2/D# B   E2     G#m   Emaj7  F#sus F#")
        assert s.lyrics == "\n".join(l)
        s = SPSong()
        l = []
        l.append(".F A/Bb C")
        l.append('')
        s.lyrics = "\n".join(l)
        s.transpose(-1)
        l = []
        l.append(".E G#/A B")
        l.append('')
        assert s.lyrics == "\n".join(l)

    def test_split_lyric(self):
        s = SPSong()
        lyric = " abcdefghijklmnopqrstuvwxyz"
        chord = ["333", "1", "4444", "22", "333", ""]
        splitlyric = s._split_lyric_line(lyric, chord)
        assert splitlyric == ['abc', 'd', 'efgh', 'ij', 'klm', 'nopqrstuvwxyz']
        lyric = " abcdefghijklmnopqrstuvwxyz"
        chord = ['     ', 'C#', ' ', 'Gbsus4/C', '    ', 'F', '  ', 'C/Eb', '']
        splitlyric = s._split_lyric_line(lyric, chord)
        assert splitlyric == ['abcde', 'fg', 'h', 'ijklmnop', 'qrst', 'u', 'vw', 'xyz']
        lyric = " ||"
        chord = ["Doesn't really matter"]
        splitlyric = s._split_lyric_line(lyric, chord)
        assert splitlyric == None

if __name__ == '__main__':
    unittest.main()
