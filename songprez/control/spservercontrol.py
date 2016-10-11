#!/usr/bin/env python

import os
from twisted.internet import reactor, threads
from twisted.internet.endpoints import serverFromString
from threading import Thread
import time
import logging
logger = logging.getLogger(__name__)
from .spsearch import SPSearch
from .spset import SPSet
from .spsong import SPSong
from .spscripture import SPBible
from .sputil import list_files, mkdir_if_not_exist
from ..network.spserver import SPServerFactory
from ..network.messages import *


class SPServerControl(object):
    '''
    A SongPrez controller stores current state, and any GUIs should be thin
    interfaces to the state shown. All communication with SPServerControl is to be
    done via Twisted AMP (see network/messages for a list).

    Only one show and one edit session can be going on at the same time. This
    means that clients who want to connect to SPServerControl for editing will affect
    other clients which are also editing. In practice, editing should be for
    the localhost client only (though 'in-show' editing requires that external
    clients be allowed as well). TODO - perhaps a priority mechanism/lock?

    Implementation details:-
    All paths are relative, should relook this when cross-platform with windows,
    see how filesep affects things
    SPSongs and SPSets are converted to json using their __dict__, this is done
    by SPServer
    Editing is done directly by the client, SPServerControl will only receive 'save'
    commands (or not). This means things like moving items around and then
    addition/removal of items are the responsibility of clients.

    BIG TODO - Show is not properly implemented. Client would have to decide
    the split of each item in a set (since only client would have the correct
    screen dimensions), this should be represented to SPServerControl somehow so
    can be passed on to other clients. Again the issue of 'priority mechanism'
    becomes possible. Alternatively have another item type called SPSlides?
    '''
    def __init__(self, indexPath, dirPath, **kwargs):
        super(SPServerControl, self).__init__(**kwargs)
        if not os.path.exists(dirPath):
            errmsg = ("SPServerControl: SongPrez media folder '%s' doesn't exist".
                      format(dirPath))
            raise IOError(errmsg)
        self._songPath = os.path.normpath(os.path.join(dirPath, 'Songs'))
        self._setPath = os.path.normpath(os.path.join(dirPath, 'Sets'))
        self._scripturePath = os.path.normpath(os.path.join(dirPath, 'Scripture'))
        for p in (self._songPath, self._setPath, self._scripturePath, indexPath):
            mkdir_if_not_exist(p)
        logger.info('SPServerControl: Using %s as directory path and %s as index path',
                    dirPath, indexPath)
        self._searchObj = SPSearch(indexPath, self._songPath)
        self._sets = None
        self.curSet = None
        self._songs = None
        self.curItem = None
        self._running = False
        self._scriptureList = None
        self._scripture = None
        self.sendAll = None
        def save_factory(response):
            self.sendAll = response.factory.sendAll
            reactor.callInThread(self._start)
        def raise_error(failure):
            raise RuntimeError('SPServerControl: Failed to start server')
        server = serverFromString(reactor, 'tcp:1916')
        d = server.listen(SPServerFactory(self))
        d.addCallback(save_factory)
        d.addErrback(raise_error)
        def interact():
            import IPython
            IPython.embed()
        if __name__ == '__main__':
            reactor.callInThread(interact)

    def _start(self):
        self._update_songs()
        self._update_sets()
        self._update_scripture()
        self._running = True
        self.sendAll(Running)

    def _connection_made(self):
        if self._running:
            logger.info('SPServerControl: A new connection was made, sending signals')
            self.send_songs()
            self.send_sets()
            self.send_scripture()
            self.sendAll(Running)

    def _update_songs(self):
        '''
        Update the stored list of songs from file. Also updates the search
        index so that its in sync
        '''
        # Use a generator first, then check for None return-type (xml parsing
        # error
        logger.info('SPServerControl: Reading songs from %s', self._songPath)
        songPath = self._songPath
        listresult = list_files(songPath, recursive=True)
        songs = [{'name': os.path.basename(e['relpath']), 'relpath': e['relpath'],
                  'mtime': e['mtime']} for e in listresult]
        self._songs = songs
        self.send_songs()
        logger.info('SPServerControl: Done reading songs from %s', self._songPath)
        self._searchObj.update_index()
        #if self._searchTerm:
            #reactor.callInThread(self._threadedsearch)

    def send_songs(self):
        self.sendAll(SongList, list=self._songs)

    def _update_sets(self):
        # Use a generator first, then check for None return-type (xml parsing
        # error
        logger.info('SPServerControl: Reading sets from %s', self._setPath)
        setPath = self._setPath
        listresult = list_files(setPath, sortbytime=True, reverse=True)
        sets = [{'name': os.path.basename(e['relpath']), 'relpath': e['relpath'],
                 'mtime': e['mtime']} for e in listresult]
        self._sets = sets
        self.send_sets()
        logger.info('SPServerControl: Done reading sets from %s', self._setPath)

    def send_sets(self):
        self.sendAll(SetList, list=self._sets)

    def _update_scripture(self):
        logger.info('SPServerControl: Reading scripture from %s', self._scripturePath)
        scripturePath = self._scripturePath
        listresult = list_files(scripturePath)
        scriptures = [{'name': os.path.basename(e['relpath']),
                       'relpath': e['relpath']} for e in listresult]
        self._scriptureList = scriptures
        self.send_scripture()
        logger.info('SPServerControl: Done reading scripture from %s', self._scripturePath)

    def send_scripture(self):
        self.sendAll(ScriptureList, list=self._scriptureList)

    def get_item(self, itemtype, relpath):
        if itemtype == 'song':
            obj = self._searchObj.get_song_from_cache(relpath)
            return obj
        else:
            return

    def get_set(self, relpath):
        if not os.path.isabs(relpath):
            relpath = os.path.join(self._setPath, relpath)
        return SPSet.read_from_file(relpath)

    def _threadedsearch(self):
        # Deprecated
        term = self._searchTerm
        starttime = time.time()
        logger.debug('SPServerControl: Searching for %s', term)
        self._searchList = self._searchObj.search(term)
        logger.debug('SPServerControl: Search for %s took %f', term, time.time()-starttime)
        self.sendAll(SearchList, itemlist=self._searchList)

    def search(self, searchTerm):
        return self._searchObj.search(searchTerm)
        # deprecated callInThread
        #self._searchTerm = searchTerm
        #reactor.callInThread(self._threadedsearch)

    def get_books(self, version):
        if self._scripture and self._scripture.name == version:
            pass
        else:
            filepath = os.path.join(self._scripturePath, version)
            self._scripture = SPBible.read_from_file(filepath)
        return self._scripture._booklist

    def get_chapters(self, version, book):
        if self._scripture and self._scripture.name == version:
            pass
        else:
            filepath = os.path.join(self._scripturePath, version)
            self._scripture = SPBible.read_from_file(filepath)
        return self._scripture._chapdict[book]

    def get_verses(self, version, book, chapter):
        if self._scripture and self._scripture.name == version:
            pass
        else:
            filepath = os.path.join(self._scripturePath, version)
            self._scripture = SPBible.read_from_file(filepath)
        verselist = self._scripture._chapdict[book][chapter]
        verses = self._scripture.full_chapter(book, chapter)
        return verselist, verses

    def change_current_set(self, set):
        if isinstance(set, SPSet):
            self.curSet = set
            self.sendAll(CurrentSet, set=self.curSet)

    def save_set(self, item, relpath):
        if not isinstance(item, SPSet):
            item = self.curSet
            if not item:
                return
        if not relpath:
            relpath = item.filepath
        if relpath:
            if not os.path.isabs(relpath):
                relpath = os.path.join(self._setPath, relpath)
            item.write_to_file(relpath)
            self._update_sets()
            self._change_current_set(relpath=relpath)

    def delete_set(self, relpath):
        if not os.path.isabs(relpath):
            relpath = os.path.join(self._setPath, relpath)
        if os.path.exists(relpath):
            os.remove(relpath)
        self._update_sets()

    def add_item_to_set(self, itemtype, relpath, position):
        if not self.curSet:
            return
        if itemtype == 'song':
            if not os.path.isabs(relpath):
                relpath = os.path.join(self._songPath, relpath)
            song = SPSong.read_from_file(relpath)
            self.curSet.add_item(item=song, itemtype='song', index=position)
            self.sendAll(CurrentSet, set=self.curSet)

    def remove_item_from_set(self, relpath, position):
        if not self.curSet:
            return
        self.curSet.remove_item(relpath=relpath, index=position)
        self.sendAll(CurrentSet, set=self.curSet)

    def change_current_item(self, itemtype, item):
        if itemtype == 'song':
            if isinstance(item, SPSong):
                self.curItem = item
                self.sendAll(CurrentItem, itemtype='song', item=self.curItem)
        elif itemtype == 'scripture':
            if not os.path.isabs(relpath):
                relpath = os.path.join(self._scripturePath, relpath)
            if self._scripture and self._scripture.name == os.path.split(relpath)[-1]:
                pass  # Already been loaded
            else:
                self._scripture = SPBible.read_from_file(relpath)
            sendval = self._scripture.skeleton()
            self.sendAll(CurrentItem, itemtype='scripture', item=sendval)

    def save_item(self, itemtype, item, relpath):
        if itemtype == 'song':
            songObject = item
            if not isinstance(songObject, SPSong):
                songObject = self.curItem
                if not songObject:
                    return
            filepath = relpath
            if not filepath:
                filepath = songObject.filepath
            if not os.path.isabs(filepath):
                filepath = os.path.join(self._songPath, filepath)
            if filepath:
                songObject.write_to_file(filepath)
                self.change_current_item('song', filepath)
            self._update_songs()

    def delete_item(self, itemtype, relpath):
        if itemtype == 'song':
            filepath = relpath
            if not os.path.isabs(filepath):
                filepath = os.path.join(self._songPath, filepath)
            if os.path.exists(filepath):
                os.remove(filepath)
            self._update_songs()

    def change_current_position(self, item, slide):
        pass

    def change_current_toggles(self, toggle):
        pass


if __name__ == "__main__":
    server = SPServerControl(u'/home/ngoonee/.config/songprez/index/',
                       u'/home/data/Dropbox/OpenSong/')
    reactor.run()
