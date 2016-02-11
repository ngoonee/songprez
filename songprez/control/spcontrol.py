#!/usr/bin/env python

import os
from twisted.internet import reactor, threads
from twisted.internet.endpoints import serverFromString
from threading import Thread
from time import sleep
from .spsearch import SPSearch
from .spset import SPSet
from .spsong import SPSong
from .spscripture import SPBible
from .sputil import list_files
from ..network.spserver import SPServerFactory
from ..network.messages import *


class SPControl(object):
    '''
    A SongPrez controller stores current state, and any GUIs should be thin
    interfaces to the state shown. All communication with SPControl is to be
    done via Twisted AMP (see network/messages for a list).

    Only one show and one edit session can be going on at the same time. This
    means that clients who want to connect to SPControl for editing will affect
    other clients which are also editing. In practice, editing should be for
    the localhost client only (though 'in-show' editing requires that external
    clients be allowed as well). TODO - perhaps a priority mechanism/lock?

    Implementation details:-
    All paths are relative, should relook this when cross-platform with windows,
    see how filesep affects things
    SPSongs and SPSets are converted to json using their __dict__, this is done
    by SPServer
    Editing is done directly by the client, SPControl will only receive 'save'
    commands (or not). This means things like moving items around and then
    addition/removal of items are the responsibility of clients.

    BIG TODO - Show is not properly implemented. Client would have to decide
    the split of each item in a set (since only client would have the correct
    screen dimensions), this should be represented to SPControl somehow so
    can be passed on to other clients. Again the issue of 'priority mechanism'
    becomes possible. Alternatively have another item type called SPSlides?
    '''
    def __init__(self, indexPath, dirPath, **kwargs):
        super(SPControl, self).__init__(**kwargs)
        self._songPath = os.path.normpath(os.path.join(dirPath, 'Songs'))
        self._setPath = os.path.normpath(os.path.join(dirPath, 'Sets'))
        self._scripturePath = os.path.normpath(os.path.join(dirPath, 'Scripture'))
        if not os.path.exists(self._songPath):
            raise IOError('dirPath does not contain a Songs folder at ' +
                          self._songPath)
        if not os.path.exists(self._setPath):
            raise IOError('dirPath does not contain a Sets folder at ' +
                          self._setPath)
        if not os.path.exists(self._scripturePath):
            raise IOError('dirPath does not contain a Scripture folder at ' +
                          self._scripturePath)
        if not os.path.exists(indexPath):
            raise IOError('indexPath does not exist at ' + indexPath)
        self._searchObj = SPSearch(indexPath, self._songPath)
        self._sets = None
        self._songs = None
        self._songList = None
        self._setList = None
        self._editSong = None
        self._editSet = None
        self._searchList = None
        self._searchTerm = u''
        self._running = False
        self._showSet = None
        self._showItems = None
        self._showSlides = None
        self._scriptureList = None
        self._scripture = None
        server = serverFromString(reactor, 'tcp:1916')
        d = server.listen(SPServerFactory(self))
        def save_factory(response):
            self.sendAll = response.factory.sendAll
        d.addCallback(save_factory)
        reactor.callInThread(self._start)

    def _start(self):
        self._update_songs()
        self._update_sets()
        self._running = True
        self.sendAll(Running)
        self._update_scripture()

    def _connection_made(self):
        if self._running:
            self._get_songs()
            self._get_sets()
            self._get_scripture()
            self.sendAll(Running)

    def quit(self):
        try:
            reactor.stop()
        except:
            pass  # Does it really matter if there's an error here?

    def _update_songs(self):
        '''
        Update the stored list of songs from file. Also updates the search
        index so that its in sync
        '''
        # Use a generator first, then check for None return-type (xml parsing
        # error
        songs = (SPSong.read_from_file(f) for f in list_files(self._songPath))
        self._songs = [s for s in songs if s is not None]
        self._get_songs()
        self._searchObj.update_index()
        if self._searchTerm:
            reactor.callInThread(self._threadedsearch)

    def _get_songs(self):
        #self._songList = [{'filepath': s.filepath, 'name': s.title,
                           #'itemtype': 'song'} for s in self._songs]
        self.sendAll(SongList, itemlist=self._songs)

    def _update_sets(self):
        # Use a generator first, then check for None return-type (xml parsing
        # error
        sets = (SPSet.read_from_file(f)
                for f in list_files(self._setPath, sortbytime=True,
                                    reverse=True, recursive=False))
        self._sets = [s for s in sets if s is not None]
        self._get_sets()

    def _get_sets(self):
        #self._setList = [{'filepath': s.filepath, 'name': s.name} for s in self._sets]
        self.sendAll(SetList, itemlist=self._sets)

    def _update_scripture(self):
        self._scriptureList = ({'filepath': os.path.split(f)[1],
                                'name': os.path.split(f)[1]}
                               for f in list_files(self._scripturePath))
        self._get_scripture()

    def _get_scripture(self):
        self.sendAll(ScriptureList, list=self._scriptureList)

    def _get_item(self, itemtype, relpath):
        if itemtype == 'song':
            obj = self._searchObj.get_song_from_cache(relpath)
            return obj
        else:
            return

    def _get_set(self, relpath):
        if not os.path.isabs(relpath):
            relpath = os.path.join(self._setPath, relpath)
        return SPSet.read_from_file(relpath)

    def _threadedsearch(self):
        term = self._searchTerm
        self._searchList = self._searchObj.search(term)
        self.sendAll(SearchList, itemlist=self._searchList)

    def _search(self, searchTerm):
        self._searchTerm = searchTerm
        reactor.callInThread(self._threadedsearch)

    def _get_books(self, version):
        if self._scripture and self._scripture.name == version:
            pass
        else:
            filepath = os.path.join(self._scripturePath, version)
            self._scripture = SPBible.read_from_file(filepath)
        return self._scripture._booklist

    def _get_chapters(self, version, book):
        if self._scripture and self._scripture.name == version:
            pass
        else:
            filepath = os.path.join(self._scripturePath, version)
            self._scripture = SPBible.read_from_file(filepath)
        return self._scripture._chapdict[book]

    def _get_verses(self, version, book, chapter):
        if self._scripture and self._scripture.name == version:
            pass
        else:
            filepath = os.path.join(self._scripturePath, version)
            self._scripture = SPBible.read_from_file(filepath)
        verselist = self._scripture._chapdict[book][chapter]
        verses = self._scripture.full_chapter(book, chapter)
        return verselist, verses

    def _change_edit_item(self, itemtype, relpath):
        if itemtype == 'song':
            if not os.path.isabs(relpath):
                relpath = os.path.join(self._songPath, relpath)
            self._editSong = SPSong.read_from_file(relpath)
            self.sendAll(EditItem, itemtype='song', item=self._editSong)
        elif itemtype == 'scripture':
            import time
            print(time.time())
            if not os.path.isabs(relpath):
                relpath = os.path.join(self._scripturePath, relpath)
            if self._scripture and self._scripture.name == os.path.split(relpath)[-1]:
                pass  # Already been loaded
            else:
                self._scripture = SPBible.read_from_file(relpath)
            import time
            print(time.time())
            sendval = self._scripture.skeleton()
            self.sendAll(EditItem, itemtype='scripture', item=sendval)
            print('selecting scripture at %s' % relpath)

    def _save_edit_item(self, itemtype, item, relpath):
        if itemtype == 'song':
            songObject = item
            if not isinstance(songObject, SPSong):
                songObject = self._editSong
                if not songObject:
                    return
            filepath = relpath
            if not filepath:
                filepath = songObject.filepath
            if not os.path.isabs(filepath):
                filepath = os.path.join(self._songPath, filepath)
            if filepath:
                songObject.write_to_file(filepath)
                self._change_edit_item('song', filepath)
            self._update_songs()

    def _new_edit_item(self, itemtype, relpath):
        if itemtype == 'song':
            filepath = relpath
            songObject = SPSong()
            songObject.title = relpath
            songObject.filepath = relpath
            filepath = os.path.abspath(os.path.join(self._songPath, filepath))
            songObject.write_to_file(filepath)
            self._update_songs()
            self._change_edit_item('song', filepath)

    def _delete_edit_item(self, itemtype, relpath):
        if itemtype == 'song':
            filepath = relpath
            if not os.path.isabs(filepath):
                filepath = os.path.join(self._songPath, filepath)
            if os.path.exists(filepath):
                os.remove(filepath)
            self._update_songs()

    def _change_edit_set(self, relpath):
        if not os.path.isabs(relpath):
            relpath = os.path.join(self._setPath, relpath)
        if relpath:
            self._editSet = SPSet.read_from_file(relpath)
            self.sendAll(EditSet, set=self._editSet)

    def _save_edit_set(self, item, relpath):
        if not isinstance(item, SPSet):
            item = self._editSet
            if not item:
                return
        if not relpath:
            relpath = item.filepath
        if relpath:
            if not os.path.isabs(relpath):
                relpath = os.path.join(self._setPath, relpath)
            item.write_to_file(relpath)
            self._update_sets()
            self._change_edit_set(relpath=relpath)

    def _new_edit_set(self, relpath):
        setObject = SPSet()
        setObject.name = relpath
        relpath = os.path.abspath(os.path.join(self._setPath, relpath))
        setObject.filepath = relpath
        setObject.write_to_file(relpath)
        self._update_sets()
        self._change_edit_set(relpath=relpath)

    def _delete_edit_set(self, relpath):
        if not os.path.isabs(relpath):
            relpath = os.path.join(self._setPath, relpath)
        if os.path.exists(relpath):
            os.remove(relpath)
        self._update_sets()

    def _resolution(self, width, height):
        pass

    def _change_show_set(self, relpath):
        self._showSet = SPSet.read_from_file(os.path.join(self._setPath, relpath))
        self.sendAll(ShowSet, set=self._showSet)
        pass

    def _add_show_item(self, itemtype, relpath, position):
        pass

    def _remove_show_item(self, position):
        pass

    def _update_show_position(self, item, slide):
        pass

    def _update_show_toggles(self, toggle):
        pass
