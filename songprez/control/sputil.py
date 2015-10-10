#!/usr/bin/env python

import os


def is_hidden(filepath):
    name = os.path.basename(os.path.abspath(filepath))
    return name.startswith('.')  # or has_hidden_attribute(filepath)

def list_files(dirpath, sortbytime=False, recursive=False, hidden=False):
    '''
    Returns a list of absolute paths to files in dirpath.

    Setting sortbytime=True will sort the results by time. Otherwise sorted by
    alphabetical order.

    Setting hidden=True will include hidden files.

    Setting recursive=True will add all subdirectories.
    Subdirectories in subdirectories will also be included.
    '''
    retval = []
    for e in os.listdir(dirpath):
        abspath = os.path.abspath(os.sep.join((dirpath, e)))
        showhidden = hidden or not is_hidden(abspath)
        if os.path.isfile(abspath) and showhidden:
            retval.append(abspath)
        if recursive and os.path.isdir(abspath) and showhidden:
            retval.extend(list_files(abspath, recursive=True))
    if sortbytime:
        retval.sort(key=lambda f: os.path.getmtime(os.path.abspath(f)))
        retval.reverse()
    else:
        retval.sort()
    return retval
