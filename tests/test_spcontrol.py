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
    @pytest.fixture(autouse=True)
    def initdir(self, tmpdir):
        self.baseDir = os.path.join(os.path.curdir, 'tests', 'dirStructureTest')
        self.tempDir = tmpdir.mkdir('searchindex').__str__()

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_tmpdir_creation(self):
        assert os.path.isdir(self.tempDir)

    def test_simple_run(self):
        assert True

if __name__ == '__main__':
    unittest.main()
