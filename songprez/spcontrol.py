#/usr/bin/env python

import os
from .spsearch import SPSearch
from .spset import SPSet
from .spsong import SPSong
from .sputil import list_files


class SPControl(object):
    def __init__(self, indexPath, dirPath):
        self._songPath = os.path.join(dirPath, 'Songs')
        self._setPath = os.path.join(dirPath, 'Sets')
        if not os.path.exists(self._songPath):
            raise IOError('dirPath does not contain a Songs folder at '
                          + self._songPath)
        if not os.path.exists(self._setPath):
            raise IOError('dirPath does not contain a Sets folder at '
                          + self._setPath)
        self._search = SPSearch(indexPath, self._songPath)

    def search(self, term):
        return self._search.search(term)

    def get_sets(self):
        return list_files(self._setPath)

    def get_set(self, path):
        return SPSet.read_from_file(path)

    def get_songs(self):
        return list_files(self._songPath)

    def get_song(self, path):
        return SPSong.read_from_file(path)
"search"
"browse_previous"
"browse_next"
"browse_add"
"edit_new"
"edit_copy"
"edit_rename"
"edit_delete"
"edit_undo"
"edit_save"
"edit_save"
"list_newset"
"list_saveset"
"list_renameset"
"list_deleteset"
"list_up"
"list_up"
"list_down"
"list_addsong"
"list_deletesong"
"search_previous"
"search_next"
"search_add"
"transpose_apply"
"transpose_sharpflat"
