#!/usr/bin/env python

import os
import logging
logger = logging.getLogger(__name__)

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

def is_hidden(filepath):
    name = os.path.basename(os.path.abspath(filepath))
    return name.startswith('.')  # or has_hidden_attribute(filepath)

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
