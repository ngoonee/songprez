#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_spset
----------------------------------

Tests for `spset` module
"""

import os
import pytest
import unittest

from songprez.control import spset
from songprez.control import spsong

class TestSPSet(unittest.TestCase):

    @pytest.fixture(autouse=True)
    def mktmpdir(self, tmpdir):
        self.tmpdir = tmpdir

    def setUp(self):
        self.baseDir = os.path.join(os.path.curdir, 'tests', 'dirStructureTest')
        self.set1 = spset.SPSet.read_from_file(os.path.join(self.baseDir,
                                               'Sets', 'SingleElementSet'))
        self.set2 = spset.SPSet.read_from_file(os.path.join(self.baseDir,
                                               'Sets', 'MultiElement Set'))

    def test_read_non_set(self):
        p = self.tmpdir.mkdir('settest')
        testfile = p.join('testfile').__str__()
        with open(testfile, 'w') as f:
            f.write('This is just at text file, not XML')
        with self.assertRaises(LookupError):
            spset.SPSet.read_from_file(testfile)

    def test_listing_song(self):
        assert len(self.set1.list_songs()) == 1
        assert len(self.set2.list_songs()) == 3

    def test_adding_song(self):
        so = spsong.SPSong()
        so.filepath = 'testsong'
        self.set1.add_item(so, 'song')
        self.set2.add_item(so, 'song', 0)
        self.set2.add_item(so, 'song')
        assert len(self.set1.list_songs()) == 2
        assert self.set1.list_songs()[-1]['name'] == 'testsong'
        assert len(self.set2.list_songs()) == 5
        assert self.set2.list_songs()[0]['name'] == 'testsong'

    def test_removing_song(self):
        so = self.set2.list_songs()[1]['filepath']
        so = os.path.join(self.baseDir, 'Songs', so)
        so = spsong.SPSong.read_from_file(so)
        self.set2.remove_item(so.filepath, 1)
        assert len(self.set2.list_songs()) == 2
        self.set2.remove_item('wrongpath', 1)
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
