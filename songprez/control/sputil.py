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

def list_files(dirpath, sortbytime=False, reverse=False, recursive=False, hidden=False):
    '''
    Returns a list of absolute paths to files in dirpath.

    Setting sortbytime=True will sort the results by time. Otherwise sorted by
    alphabetical order.
    
    Setting reverse=True will reverse the sorting (alphabetical or by time)

    Setting hidden=True will include hidden files.

    Setting recursive=True will add all subdirectories.
    Subdirectories in subdirectories will also be included.
    '''
    retval = []
    dirs = []
    for e in os.listdir(dirpath):
        abspath = os.path.abspath(os.sep.join((dirpath, e)))
        showhidden = hidden or not is_hidden(abspath)
        if os.path.isfile(abspath) and showhidden:
            retval.append(abspath)
        if recursive and os.path.isdir(abspath) and showhidden:
            dirs.append(abspath)
    if sortbytime:
        retval.sort(key=lambda f: os.path.getmtime(os.path.abspath(f)))
    else:
        retval.sort()
    dirs.sort()
    if reverse:
        retval.reverse()
        dirs.reverse()
    for d in dirs:
        retval.extend(list_files(d, sortbytime, reverse, recursive, hidden))
    return retval
