#/usr/bin/env python

import os
from blinker import signal
from .spsearch import SPSearch
from .spset import SPSet
from .spsong import SPSong
from .sputil import list_files


class SPControl(object):
    '''
    A SongPrez controller stores current state, and any GUIs should be thin
    interfaces to the state shown. Currently there are two states, presenting
    and editing.

    EDITING:-
        Internal state variables:-
            Current set
            Current song
        Published information:-
            Current set
            Current Song
        Subscribed signals:-
            Change current set
            Save current set (replace with sent information)
            Change current song
            Save current song (replace with sent information)
            Add current song to current set
            Remove current song from current set
        Functions:-
            get_sets - returns list of sets
            get_songs - returns list of songs
            search(term) - returns list of songs matching search term

    PRESENTING:-
        Published information:-
            Current set
            Current song
            Position in current song
            Current status of screen toggles (blank/black/freeze etc)
        Subscribed signals:-
            Next slide
            Next song
            Previous slide
            Previous song
            Goto in song (V1, C, B etc)
            Toggle blank/black/freeze etc
            Change to set
            Add this song
            Overlay this alert
    '''
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
        self.songList = None
        self.setList = None
        self.curSong = None
        self.curSet = None
        self._update_songs()
        self._update_sets()
        signal('changeSet').connect(self._change_set)
        signal('saveSet').connect(self._save_set)
        signal('changeSong').connect(self._change_song)
        signal('saveSong').connect(self._save_song)
        signal('addSong').connect(self._add_song)
        signal('removeSong').connect(self._remove_song)

    @property
    def songList(self):
        return self._songs

    @songList.setter
    def songList(self, list_of_songs):
        self._songs = list_of_songs
        signal('songList').send(self._songs)

    def _update_songs(self):
        self.songList = [SPSong.read_from_file(f)
                         for f in list_files(self._songPath)]

    @property
    def setList(self):
        return self._sets

    @setList.setter
    def setList(self, list_of_sets):
        self._sets = list_of_sets
        signal('setList').send(self._sets)

    def _update_sets(self):
        self.setList = [SPSet.read_from_file(f)
                        for f in list_files(self._setPath)]

    @property
    def curSong(self):
        return self._cursong

    @curSong.setter
    def curSong(self, songObject):
        self._cursong = songObject
        signal('curSong').send(self._cursong)

    def _change_song(self, filepath):
        if filepath:
            self.curSong = SPSong.read_from_file(filepath)

    def _save_song(self, songObject, filepath):
        if not isinstance(songObject, SPSong):
            return
        if not filepath:
            filepath = songObject.filepath
        songObject.write_to_file(filepath)
        # Not sure if this is a good idea, would there be race bugs? Just that
        # self.curSong = songObject seems a bit too presumptuous
        self.curSong = SPSong.read_from_file(filepath)

    @property
    def curSet(self):
        return self._curset

    @curSet.setter
    def curSet(self, setObject):
        self._curset = setObject
        signal('curSet').send(self._curset)

    def _change_set(self, filepath):
        if filepath:
            self.curSet = SPSet.read_from_file(filepath)
            self.curSong = self.curSet.list_songs()[0]

    def _save_set(self, setObject, filepath):
        if not isinstance(setObject, SPSet):
            return
        if not filepath:
            filepath = setObject.filepath
        setObject.write_to_file(filepath)
        # Not sure if this is a good idea, would there be race bugs? Just that
        # self.curSet = setObject seems a bit too presumptuous
        self.curSet = SPSet.read_from_file(filepath)

    def _add_song(self, songObject):
        if not isinstance(songObject, SPSong):
            return
        self.curSet.add_song(songObject)

    def _remove_song(self):
        if not isinstance(songObject, SPSong):
            return
        self.curSet.remove_song(songObject)

    def search(self, term):
        return self._search.search(term)

    def get_sets(self):
        return [(s.filepath, s.name) for s in self.setList]

    def get_set(self, path):
        return SPSet.read_from_file(path)

    def get_songs(self):
        return [(s.filepath, s.title) for s in self.songList]

    def get_song(self, path):
        return self._search.get_song_from_cache(path)
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
