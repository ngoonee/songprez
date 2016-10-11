#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_sputil
----------------------------------

Tests for `sputil` module.
"""

import unittest
import os

from songprez.control import sputil

def test_priority_merge_empty_A():
    A = []
    b = [{'name': '1', 'relpath': '1.txt', 'mtime': 147261}]
    assert sputil.priority_merge(A, b) == b

def test_priority_merge_empty_b():
    b = []
    A = [{'name': '1', 'relpath': '1.txt', 'mtime': 147261}]
    assert sputil.priority_merge(A, b) == []

def test_priority_merge_adding():
    A = [{'name': '1', 'relpath': '1.txt', 'mtime': 147261, 'add': 4},
         {'name': '2', 'relpath': '2.txt', 'mtime': 147261},
         {'name': '3', 'relpath': '3.txt', 'mtime': 147261},
         {'name': '4', 'relpath': '4.txt', 'mtime': 147261},]
    b = [{'name': '1', 'relpath': '1.txt', 'mtime': 147261},
         {'name': '2', 'relpath': '2.txt', 'mtime': 147261},
         {'name': '2.5', 'relpath': '2.5.txt', 'mtime': 147261},
         {'name': '3', 'relpath': '3.txt', 'mtime': 147261},
         {'name': '4', 'relpath': '4.txt', 'mtime': 147261},]
    out = A[:]
    out.insert(2, b[2])
    assert sputil.priority_merge(A, b) == out

def test_priority_merge_removing():
    A = [{'name': '1', 'relpath': '1.txt', 'mtime': 147261, 'add': 4},
         {'name': '2', 'relpath': '2.txt', 'mtime': 147261},
         {'name': '3', 'relpath': '3.txt', 'mtime': 147261},
         {'name': '4', 'relpath': '4.txt', 'mtime': 147261},]
    b = [{'name': '1', 'relpath': '1.txt', 'mtime': 147261},
         {'name': '2', 'relpath': '2.txt', 'mtime': 147261},
         {'name': '4', 'relpath': '4.txt', 'mtime': 147261},]
    out = A[:]
    out.pop(2)
    assert sputil.priority_merge(A, b) == out

def test_priority_merge_replacing():
    A = [{'name': '1', 'relpath': '1.txt', 'mtime': 147261, 'add': 4},
         {'name': '2', 'relpath': '2.txt', 'mtime': 147261},
         {'name': '3', 'relpath': '3.txt', 'mtime': 147261},
         {'name': '4', 'relpath': '4.txt', 'mtime': 147261},]
    b = [{'name': '1', 'relpath': '1.txt', 'mtime': 147263},
         {'name': '2', 'relpath': '2.txt', 'mtime': 147261},
         {'name': '3', 'relpath': '3.txt', 'mtime': 147259},
         {'name': '4', 'relpath': '4.txt', 'mtime': 147261},]
    out = A[:]
    out.pop(0)
    out.insert(0, b[0])
    assert sputil.priority_merge(A, b) == out
