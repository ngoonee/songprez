#!/usr/bin/env python

import os
from threading import Thread
from blinker import signal
from time import sleep
from .spsearch import SPSearch
from .spset import SPSet
from .spsong import SPSong
from .sputil import list_files


class SPControl(Thread):
    '''
    A SongPrez controller stores current state, and any GUIs should be thin
    interfaces to the state shown. Currently there are two states, presenting
    and editing.

    EDITING:-
        Published information:-
            initialized(sender) - Initialization done
            curSet(sender, Set) - Current set
            curSong(sender, Song) - Current Song
            setList(sender, List) - List of sets
            songList(sender, List) - List of songs
            searchList(sender, List) - List of search results
        Subscribed signals:-
            getSongs(sender) - Generate a current list of songs and publish it
            getSets(sender) - Generate a current list of sets and publish it
            changeSong(sender, Path) - Change current song
            saveSong(sender, Path, Song) - Save current song (replace with
                                           sent information)
            changeSet(sender, Path, <Song>) - Change current set
            saveSet(sender, Path, Set) - Save current set (replace with sent
                                         information)
            getSong(sender, Path) - Return song from given path
            getSet(sender, Path) - Return set from given path
            newSong(sender, Path) - Creates a new song (blank) in the given
                                    path (also changes current song)
            newSet(sender, Path) - Creates a new set (blank) in the given
                                   path (also changes current set)
            deleteSong(sender, Path) - Deletes the song in the given path
            deleteSet(sender, Path) - Deletes the set in the given path
            addSong(sender) - Add current song to current set
            removeSong(sender) - Remove current song from current set
            upSong(sender) - Move current song higher in current set
            downSong(sender) - Move current song lower in current set
            search(sender, SearchTerm) - Run a search and publish the results
            publishAll(sender) - Publish all information (cached) currently
                                 held, this is a sort of 'refresh' order

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
    def __init__(self, indexPath, dirPath, **kwargs):
        super(SPControl, self).__init__(**kwargs)
        self._songPath = os.path.normpath(os.path.join(dirPath, 'Songs'))
        self._setPath = os.path.normpath(os.path.join(dirPath, 'Sets'))
        if not os.path.exists(self._songPath):
            raise IOError('dirPath does not contain a Songs folder at ' +
                          self._songPath)
        if not os.path.exists(self._setPath):
            raise IOError('dirPath does not contain a Sets folder at ' +
                          self._setPath)
        if not os.path.exists(indexPath):
            raise IOError('indexPath does not exist at ' + indexPath)
        self._searchObj = SPSearch(indexPath, self._songPath)
        self._sets = None
        self._songs = None
        self._songList = None
        self._setList = None
        self._curSong = None
        self._curSet = None
        self._searchTerm = ''
        self._searchList = None
        self._quit = False

    def run(self):
        self._update_songs()
        self._update_sets()
        signal('getSongs').connect(self._get_songs)
        signal('changeSong').connect(self._change_song)
        signal('saveSong').connect(self._save_song)
        signal('getSong').connect(self._get_song)
        signal('getSets').connect(self._get_sets)
        signal('changeSet').connect(self._change_set)
        signal('saveSet').connect(self._save_set)
        signal('getSet').connect(self._get_set)
        signal('newSong').connect(self._new_song)
        signal('newSet').connect(self._new_set)
        signal('deleteSong').connect(self._delete_song)
        signal('deleteSet').connect(self._delete_set)
        signal('addSong').connect(self._add_song)
        signal('removeSong').connect(self._remove_song)
        signal('upSong').connect(self._up_song)
        signal('downSong').connect(self._down_song)
        signal('search').connect(self._search)
        signal('publishAll').connect(self._publish_all)
        signal('initialized').send(self)
        while True:
            if self._quit:
                break
            if self._searchTerm:
                self._searchList = self._searchObj.search(self._searchTerm)
                self._searchTerm = ''
                signal('searchList').send(self, List=self._searchList)
            sleep(0.1)

    def quit(self):
        self._quit = True

    ### Methods handling songList. _songs holds the list, _songList holds the
    ### return object. Should only be accessed by _get_songs()
    def _update_songs(self):
        '''
        Update the stored list of songs from file. Also updates the search
        index so that its in sync
        '''
        # Use a generator first, then check for None return-type (xml parsing
        # error
        songs = (SPSong.read_from_file(f) for f in list_files(self._songPath))
        self._songs = [s for s in songs if s is not None]
        self._get_songs(self)
        self._searchObj.update_index()

    def _get_songs(self, sender):
        self._songList = [(s.filepath, s.title) for s in self._songs]
        signal('songList').send(self, List=self._songList)

    ### Methods handling setList. _songs holds the list, _setList holds the
    ### return object. Should only be accessed by _get_sets()
    def _update_sets(self):
        # Use a generator first, then check for None return-type (xml parsing
        # error
        sets = (SPSet.read_from_file(f)
                for f in list_files(self._setPath, sortbytime=True,
                                    reverse=True, recursive=True))
        self._sets = [s for s in sets if s is not None]
        self._get_sets(self)

    def _get_sets(self, sender):
        self._setList = [(s.filepath, s.name) for s in self._sets]
        signal('setList').send(self, List=self._setList)

    ### Methods handling curSong.
    def _change_song(self, sender, **kwargs):
        filepath = kwargs.get('Path')
        if filepath:
            if not os.path.isabs(filepath):
                filepath = os.path.join(self._songPath, filepath)
            self._curSong = SPSong.read_from_file(filepath)
            signal('curSong').send(self, Song=self._curSong)

    def _save_song(self, sender, **kwargs):
        songObject = kwargs.get('Song')
        if not isinstance(songObject, SPSong):
            songObject = self._curSong
            if not songObject:
                # No valid object found either in signal or curSong
                return
        filepath = kwargs.get('Path')
        if not filepath:
            filepath = songObject.filepath
        if not os.path.isabs(filepath):
            filepath = os.path.join(self._songPath, filepath)
        if filepath:
            songObject.write_to_file(filepath)
            self._change_song(self, Path=filepath)
        self._update_songs()

    ### Methods handling curSet.
    def _change_set(self, sender, **kwargs):
        filepath = kwargs.get('Path')
        if not os.path.isabs(filepath):
            filepath = os.path.join(self._setPath, filepath)
        songObject = kwargs.get('Song')
        if filepath:
            self._curSet = SPSet.read_from_file(filepath)
            signal('curSet').send(self, Set=self._curSet)
            if songObject is not None:
                self._change_song(self, Path=songObject.filepath)

    def _save_set(self, sender, **kwargs):
        setObject = kwargs.get('Set')
        if not isinstance(setObject, SPSet):
            setObject = self._curSet
            if not setObject:
                # No valid object found either in signal or curSet
                return
        filepath = kwargs.get('Path')
        if not filepath:
            filepath = setObject.filepath
        if filepath:
            if not os.path.isabs(filepath):
                filepath = os.path.join(self._setPath, filepath)
            setObject.write_to_file(filepath)
            self._change_set(sender, Path=filepath)

    def _add_song(self, sender):
        songObject = self._curSong
        if isinstance(songObject, SPSong) and isinstance(self._curSet, SPSet):
            self._curSet.add_song(songObject)
            signal('curSet').send(self, Set=self._curSet)

    def _remove_song(self, sender):
        songObject = self._curSong
        if isinstance(songObject, SPSong) and isinstance(self._curSet, SPSet):
            self._curSet.remove_song(songObject)
            signal('curSet').send(self, Set=self._curSet)

    def _up_song(self, sender):
        songObject = self._curSong
        if isinstance(songObject, SPSong) and isinstance(self._curSet, SPSet):
            self._curSet.move_song_up(songObject)
            signal('curSet').send(self, Set=self._curSet)

    def _down_song(self, sender):
        songObject = self._curSong
        if isinstance(songObject, SPSong) and isinstance(self._curSet, SPSet):
            self._curSet.move_song_down(songObject)
            signal('curSet').send(self, Set=self._curSet)

    ### Methods handling search results.
    def _search(self, sender, **kwargs):
        self._searchTerm = kwargs.get('SearchTerm', '')

    ### Methods handling general requests
    def _get_set(self, sender, **kwargs):
        filepath = kwargs.get('Path')
        if not os.path.isabs(filepath):
            filepath = os.path.join(self._setPath, filepath)
        return SPSet.read_from_file(filepath)

    def _get_song(self, sender, **kwargs):
        filepath = kwargs.get('Path')
        if not os.path.isabs(filepath):
            filepath = os.path.join(self._songPath, filepath)
        return self._searchObj.get_song_from_cache(path)

    def _new_song(self, sender, **kwargs):
        filepath = kwargs.get('Path')
        songObject = SPSong()
        songObject.title = filepath
        songObject.filepath = filepath
        filepath = os.path.abspath(os.path.join(self._songPath, filepath))
        songObject.write_to_file(filepath)
        self._update_songs()
        self._change_song(None, Path=filepath)

    def _new_set(self, sender, **kwargs):
        filepath = kwargs.get('Path')
        setObject = SPSet()
        setObject.name = filepath
        filepath = os.path.abspath(os.path.join(self._setPath, filepath))
        setObject.filepath = filepath
        setObject.write_to_file(filepath)
        self._update_sets()
        self._change_set(None, Path=filepath)

    def _delete_song(self, sender, **kwargs):
        filepath = kwargs.get('Path')
        if not os.path.isabs(filepath):
            filepath = os.path.join(self._songPath, filepath)
        if os.path.exists(filepath):
            os.remove(filepath)
        self._update_songs()

    def _delete_set(self, sender, **kwargs):
        filepath = kwargs.get('Path')
        if not os.path.isabs(filepath):
            filepath = os.path.join(self._setPath, filepath)
        if os.path.exists(filepath):
            os.remove(filepath)
        self._update_sets()

    def _publish_all(self, sender):
        signal('curSet').send(self, Set=self._curSet)
        signal('curSong').send(self, Song=self._curSong)
        signal('resultSet').send(self, Set=self._resultSet)
        signal('resultSong').send(self, Song=self._resultSong)
        signal('setList').send(self, List=self._setList)
        signal('songList').send(self, List=self._songList)
        signal('searchList').send(self, List=self._searchList)
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
