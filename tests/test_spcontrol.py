#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_spcontrol
----------------------------------

Tests for `spcontrol` module.
"""

import unittest
import pytest
import os
from time import sleep

from songprez.control import spcontrol


class TestControl(unittest.TestCase):
    '''
    Uses unsupported creation logic to simplify testing. The resulting
    object WILL break if used externally
    '''
    @pytest.fixture(autouse=True)
    def initdir(self, tmpdir):
        self.baseDir = os.path.join(os.path.curdir, 'tests', 'dirStructureTest')
        self.tempDir = tmpdir.mkdir('searchindex').__str__()

    def setUp(self):
        self.control = spcontrol.SPControl(self.tempDir, self.baseDir)
        self.control.daemon = True
        pass

    def tearDown(self):
        pass

    def test_tmpdir_creation(self):
        assert os.path.isdir(self.tempDir)

    def test_simple_run(self):
        self.control._quit = True
        self.control.run()
        assert True

if __name__ == '__main__':
    unittest.main()
