#!/usr/bin/env python

import xmltodict
import os
from pprint import pprint


def _is_hidden(filepath):
    name = os.path.basename(os.path.abspath(filepath))
    return name.startswith('.')  # or has_hidden_attribute(filepath)


def list_files(dirpath, recursive=False, hidden=False):
    '''
    Returns a list of absolute paths to files in dirpath.

    Setting hidden=True will include hidden files.

    Setting recursive=True will add all subdirectories.
    Subdirectories in subdirectories will also be included.
    '''
    retval = []
    for e in os.listdir(dirpath):
        abspath = os.sep.join((dirpath, e))
        showhidden = hidden or not _is_hidden(abspath)
        if os.path.isfile(abspath) and showhidden:
            retval.append(abspath)
        if recursive and os.path.isdir(abspath) and showhidden:
            retval.extend(list_files(abspath, recursive=True))
    return retval


def _load_xml(filepath):
    '''
    Loads an xml file into a python dict.
    '''
    with open(filepath) as f:
        obj = xmltodict.parse(f.read())
    return obj


def load_set(filepath):
    '''
    Loads an OpenSong set (xml file containing a list of songs).
    
    Currently a stub to xmltodict pending future datatype decision.
    '''
    return _load_xml(filepath)


def load_song(filepath):
    '''
    Loads an OpenSong song (xml file containing a song)
    
    Currently a stub to xmltodict pending future datatype decision.
    '''
    return _load_xml(filepath)


def _write_xml(filepath, obj):
    '''
    Writes a python dict into an xml file.
    '''
    with open(filepath, 'w') as f:
        f.write(xmltodict.unparse(obj, pretty=True))


def write_set(filepath, obj):
    '''
    Writes an OpenSong set (xml file conataining a list of songs).

    Currently a stub to xmltodict pending future datatype decision.
    '''
    _write_xml(filepath, obj)


def write_song(filepath, obj):
    '''
    Writes an OpenSong song (xml file conataining song).

    Currently a stub to xmltodict pending future datatype decision.
    '''
    _write_xml(filepath, obj)
