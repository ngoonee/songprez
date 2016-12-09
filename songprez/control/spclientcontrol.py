#!/usr/bin/env python
from twisted.internet import reactor, defer
from twisted.internet.endpoints import clientFromString
import json
import logging
from blinker import signal
logger = logging.getLogger(__name__)
from ..network.spclient import SPClientFactory
from ..network.messages import *
from .spsong import SPSong
from .spset import SPSet


class SPClientControl(object):
    def __init__(self, **kwargs):
        super(SPClientControl, self).__init__(**kwargs)
        self.connection = None
        self.setList = []
        self.songList = []
        self.scriptureList = []
        self.curSet = None
        self.curItem = None
        self.ownSet = None
        self.ownItem = None
        endpoint = clientFromString(reactor, 'tcp:localhost:1916')
        d = endpoint.connect(SPClientFactory(self))
        def interact():
            import IPython
            IPython.embed()
        if __name__ == '__main__':
            reactor.callInThread(interact)

    def on_connection(self, connection):
        logger.info('SPClientControl: Successfully connected to %s',
                   str(connection.transport.realAddress))
        self.connection = connection

    def _printerr(self, error):
        logger.error('SPClientControl: error %s', error)
        return

    def running(self):
        pass

    ### Respond to server announcements

    def set_list(self, listofset):
        self.setList = listofset
        signal('setList').send()

    def song_list(self, listofsong):
        self.songList = listofsong
        signal('songList').send()

    def scripture_list(self, listofscripture):
        self.scriptureList = listofscripture
        signal('scriptureList').send()

    def current_set(self, set):
        self.curSet = set
        signal('curSet').send()

    def current_item(self, item):
        self.curItem = item
        signal('curItem').send()

    def current_position(self, item, slide):
        pass

    def current_toggles(self, toggle):
        pass

    ### Methods for requesting data from server

    @defer.inlineCallbacks
    def get_item(self, itemtype, relpath):
        def json_to_item(response, itemtype):
            if itemtype == 'song':
                s = SPSong()
                s.__dict__ = json.loads(response['jsonitem'])
                return s
            return response
        d = self.connection.callRemote(GetItem, itemtype=itemtype,
                                       relpath=relpath)
        d.addCallbacks(json_to_item, self._printerr,
                       callbackKeywords={'itemtype': itemtype})
        retval = yield d
        defer.returnValue(retval)

    @defer.inlineCallbacks
    def get_set(self, relpath):
        def json_to_set(response):
            if response.has_key('jsonset'):
                s = SPSet()
                s.__dict__ = json.loads(response['jsonset'])
                return s
            return response
        d = self.connection.callRemote(GetSet, relpath=relpath)
        d.addCallbacks(json_to_set, self._printerr)
        retval = yield d
        defer.returnValue(retval)

    @defer.inlineCallbacks
    def search(self, term):
        d = self.connection.callRemote(Search, term=term)
        d.addCallbacks(lambda x: [json.loads(e) for e in x['jsonlist']],
                       self._printerr)
        retval = yield d
        defer.returnValue(retval)

    @defer.inlineCallbacks
    def get_books(self, version):
        d = self.connection.callRemote(GetBooks, version=version)
        d.addCallbacks(lambda x: [e for e in x['booklist']], self._printerr)
        retval = yield d
        defer.returnValue(retval)

    @defer.inlineCallbacks
    def get_chapters(self, version, book):
        d = self.connection.callRemote(GetChapters, version=version, book=book)
        d.addCallbacks(lambda x: [e for e in x['chapterlist']], self._printerr)
        retval = yield d
        defer.returnValue(retval)

    @defer.inlineCallbacks
    def get_verses(self, version, book, chapter):
        d = self.connection.callRemote(GetVerses, version=version, book=book,
                                       chapter=chapter)
        d.addCallbacks(lambda x: [v for v in x['verses']], self._printerr)
        retval = yield d
        defer.returnValue(retval)

    ### Methods for controlling server

    def change_current_set(self, set):
        jsonset = json.dumps(set.__dict__)
        d = self.connection.callRemote(ChangeCurrentSet, jsonset=jsonset)
        d.addErrback(self._printerr)

    def save_set(self, set, relpath):
        jsonset = json.dumps(set.__dict__)
        d = self.connection.callRemote(SaveSet, jsonset=jsonset, relpath=relpath)
        d.addErrback(self._printerr)

    def delete_set(self, relpath):
        d = self.connection.callRemote(DeleteSet, relpath=relpath)
        d.addErrback(self._printerr)

    def add_item_to_current_set(self, itemtype, relpath, position=-1):
        d = self.connection.callRemote(AddItemToSet, itemtype=itemtype,
                                           relpath=relpath, position=position)
        d.addErrback(self._printerr)

    def remove_item_from_current_set(self, relpath, position):
        d = self.connection.callRemote(RemoveItemFromSet, relpath=relpath,
                                           position=position)
        d.addErrback(self._printerr)

    def change_current_item(self, item):
        if isinstance(item, SPSong):
            jsonsong = json.dumps(item.__dict__)
            d = self.connection.callRemote(ChangeCurrentItem, itemtype='song',
                                           jsonsong=jsonsong)
            d.addErrback(self._printerr)

    def save_item(self, item, relpath):
        if isinstance(item, SPSong):
            jsonitem = json.dumps(item.__dict__)
            d = self.connection.callRemote(SaveItem, itemtype='song',
                                           jsonitem=jsonitem, relpath=relpath)
            d.addErrback(self._printerr)

    def delete_item(self, itemtype, relpath):
        d = self.connection.callRemote(DeleteItem, itemtype=itemtype,
                                       relpath=relpath)
        d.addErrback(self._printerr)

    def change_current_position(self, index, linestart, lineend):
        d = self.connection.callRemote(ChangeCurrentPosition, index=index,
                                       linestart=linestart, lineend=lineend)
        d.addErrback(self._printerr)

    def change_current_toggles(self, toggle):
        d = self.connection.callRemote(ChangeCurrentToggles, toggle=toggle)
        d.addErrback(self._printerr)

    ### Methods for manipulating own (editing) set and items

    @defer.inlineCallbacks
    def change_own_set(self, relpath):
        if relpath:
            d = self.get_set(relpath)
            self.ownSet = yield d
        else:
            self.ownSet = SPSet()
        signal('ownSet').send()

    @defer.inlineCallbacks
    def add_item_to_own_set(self, itemtype, relpath, position=-1):
        if not self.ownSet:
            return
        if itemtype == 'song':
            d = self.get_item(itemtype, relpath)
            song = yield d
            self.ownSet.add_item(item=song, itemtype='song', index=position)
            signal('ownSet').send()

    def remove_item_from_own_set(self, relpath, position):
        if not self.ownSet:
            return
        self.ownSet.remove_item(relpath=relpath, index=position)
        signal('ownSet').send()

    @defer.inlineCallbacks
    def change_own_item(self, itemtype, relpath):
        if itemtype == 'song':
            if relpath:
                d = self.get_item(itemtype, relpath)
                self.ownItem = yield d
            else:
                self.ownItem = SPSong()
            signal('ownItem').send()


if __name__ == "__main__":
    client = SPClientControl()
    reactor.run()
