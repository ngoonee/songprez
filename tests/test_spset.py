#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_spset
----------------------------------

Tests for `spset` module
"""

import os
import unittest

from songprez import spset
from songprez import spsong

'''
def test_set_read_write(tmpdir):
    p = tmpdir.mkdir('settest')
    se = SPSet()
    s = SPSong()
    for item in spsong._xmlkeys:
        setattr(s, item, "test")
    s.write_to_file(p.join('test').__str__())
    s2 = SPSong.read_from_file(p.join('test').__str__())
    for item in spsong._xmlkeys:
        assert getattr(s, item) == getattr(s2, item)
        '''

class TestSPSet(unittest.TestCase):

    def setUp(self):
        self.baseDir = os.path.join(os.path.curdir, 'tests', 'dirStructureTest')
        self.set1 = spset.SPSet.read_from_file(os.path.join(self.baseDir,
                                               'Sets', 'SingleElementSet'))
        self.set2 = spset.SPSet.read_from_file(os.path.join(self.baseDir,
                                               'Sets', 'MultiElement Set'))

    def test_listing_song(self):
        assert len(self.set1.list_songs()) == 1
        assert len(self.set2.list_songs()) == 3

    def test_adding_song(self):
        so = spsong.SPSong()
        self.set1.add_song(so)
        self.set2.add_song(so)
        self.set2.add_song(so)
        assert len(self.set1.list_songs()) == 2
        assert len(self.set2.list_songs()) == 5

    def test_removing_song(self):
        so = self.set2.list_songs()[1]
        self.set2.remove_song(so)
        assert len(self.set2.list_songs()) == 2
        self.set2.remove_song(so)
        assert len(self.set2.list_songs()) == 2

    def test_moving_song(self):
        so = self.set2.list_songs()[-1]
        self.set2.move_song_down(so)
        for item in spsong._xmlkeys:
            assert getattr(self.set2.list_songs()[-1], item) == getattr(so, item)
        self.set2.move_song_up(so)
        for item in spsong._xmlkeys:
            assert getattr(self.set2.list_songs()[-2], item) == getattr(so, item)
        self.set2.move_song_down(so)
        for item in spsong._xmlkeys:
            assert getattr(self.set2.list_songs()[-1], item) == getattr(so, item)

    def test_writing(self):
        baseDir = self.baseDir
        set2out = os.path.join(baseDir, 'Sets', 'SingleOutput')
        self.set2.write_to_file(set2out)
        set2copy = spset.SPSet.read_from_file(set2out)
        for index in range(3):
            orisong = self.set2.list_songs()[index]
            copysong = set2copy.list_songs()[index]
            for item in spsong._xmlkeys:
                assert getattr(orisong, item) == getattr(copysong, item)

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
