#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_spset
----------------------------------

Tests for `spset` module
"""

import os
import unittest

from songprez.control import spset
from songprez.control import spsong

def test_read_non_set(tmpdir):
    p = tmpdir.mkdir('settest')
    testfile = p.join('testfile').__str__()
    with open(testfile, 'w') as f:
        f.write('This is just at text file, not XML')
    assert spset.SPSet.read_from_file(testfile) is None

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
        so = self.set2.list_songs()[1]['filepath']
        so = os.path.join(self.baseDir, 'Songs', so)
        so = spsong.SPSong.read_from_file(so)
        self.set2.remove_song(so)
        assert len(self.set2.list_songs()) == 2
        self.set2.remove_song(so)
        assert len(self.set2.list_songs()) == 2

    def test_writing(self):
        baseDir = self.baseDir
        set2out = os.path.join(baseDir, 'Sets', 'SingleOutput')
        self.set2.write_to_file(set2out)
        set2copy = spset.SPSet.read_from_file(set2out)
        for index in range(3):
            orisong = self.set2.list_songs()[index]
            copysong = set2copy.list_songs()[index]
            assert orisong == copysong
        os.remove(set2out)

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
