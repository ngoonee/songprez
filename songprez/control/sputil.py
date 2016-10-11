#!/usr/bin/env python

import os
import logging
logger = logging.getLogger(__name__)
from sys import platform

# Attempt using lxml with fallbacks to cElementTree and ElementTree
try:
  from lxml import etree
  logger.info("SPUtil: Using lxml.etree")
except ImportError:
  try:
    # Python 2.5
    import xml.etree.cElementTree as etree
    logger.info("SPUtil: Using cElementTree on Python 2.5+")
  except ImportError:
    try:
      # Python 2.5
      import xml.etree.ElementTree as etree
      logger.info("SPUtil: Using ElementTree on Python 2.5+")
    except ImportError:
      try:
        # normal cElementTree install
        import cElementTree as etree
        logger.info("SPUtil: Using cElementTree")
      except ImportError:
        try:
          # normal ElementTree install
          import elementtree.ElementTree as etree
          logger.info("SPUtil: Using ElementTree")
        except ImportError:
          logger.error("SPUtil: Failed to import ElementTree from any known place")

if platform.startswith('linux') or platform == 'darwin':
    def is_hidden(filepath):
        name = os.path.basename(os.path.abspath(filepath))
        return name.startswith('.')  # or has_hidden_attribute(filepath)
elif platform == 'win32':
    import ctypes
    def is_hidden(filepath):
        try:
            attrs = ctypes.windll.kernel32.GetFileAttributesW(unicode(filepath))
            assert attrs != -1
            result = bool(attrs & 2)
        except (AttributeError, AssertionError):
            result = False
        return result

def make_rel(basepath, filepath):
    if filepath.startswith(basepath):
        return filepath[len(basepath)+1:]
    return filepath

def list_files(dirpath, sortbytime=False, reverse=False, recursive=False, hidden=False, recursed=False):
    '''
    Returns a list of absolute paths to files in dirpath.

    Setting sortbytime=True will sort the results by time. Otherwise sorted by
    alphabetical order.
    
    Setting reverse=True will reverse the sorting (alphabetical or by time)

    Setting hidden=True will include hidden files.

    Setting recursive=True will add all subdirectories.
    Subdirectories in subdirectories will also be included.
    '''
    contents = [os.path.abspath(os.sep.join((dirpath, e)))
                for e in os.listdir(dirpath)]
    if not hidden:
        contents = [e for e in contents if not is_hidden(e)]
    files = [{'relpath': f, 'mtime': os.path.getmtime(f)} for f in contents
             if not os.path.isdir(f) and not is_hidden(f)]
    if sortbytime:
        files.sort(key=lambda x: x['mtime'])
    else:
        files.sort(key=lambda x: x['relpath'])
    if reverse:
        files.reverse()
    if recursive:
        dirs = [e for e in contents if os.path.isdir(e) and not is_hidden(e)]
        dirs.sort()
        if reverse:
            dirs.reverse()
        for d in dirs:
            files.extend(list_files(d, sortbytime, reverse, recursive, hidden,
                                    recursed=True))
    if not recursed:
        files = [{'relpath': make_rel(dirpath, f['relpath']),
                  'mtime': f['mtime']} for f in files]
    return files

def mkdir_if_not_exist(dirpath):
    if not os.path.exists(dirpath):
        os.mkdir(dirpath)

def priority_merge(A, b, keys=['name', 'relpath'], mkey='mtime'):
    '''
    Merges b to A, preserving order. A is the priority list. Matching-ness
    of elements depends on dict keys existing in b (instances in A typically
    have more keys than in b).

    If an element in b already exists in A, the A instance is used.

    If an element in b does not exist in A, it is inserted at the same
    relative position to other elements in A as exists in b (preserve order).

    If an element in b already exists in A, but its mkey is higher than that
    of the instance in A, use the b instance.
    '''
    retval = []
    b_index = 0
    for elemA in A:
        if b_index >= len(b):
            break  # No more items in b
        elemb = b[b_index]
        minA = { k: elemA[k] for k in keys }
        minb = { k: elemb[k] for k in keys }
        if minA == minb:  # Found a match
            if elemA[mkey] >= elemb[mkey]:
                retval.append(elemA)
            else:  # Check mkey to see if take b instead
                retval.append(elemb)
            b_index = b_index + 1
        else:  # No match, check forward by one
            if b_index+1 >= len(b):
                continue
            elembplus = b[b_index+1]
            minb = { k: elembplus[k] for k in keys}
            if minA == minb:
                retval.append(elemb)  # This is a new element
                if elemA[mkey] >= elembplus[mkey]:
                    retval.append(elemA)
                else:
                    retval.append(elembplus)
                b_index = b_index + 2
    if b_index <= len(b):
        retval.extend(b[b_index:])
    return retval
