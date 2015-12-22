#!/usr/bin/env python
from twisted.internet import reactor, protocol
from twisted.internet import defer
from twisted.protocols import amp
import json
from .messages import *
from ..control.spsong import SPSong
from ..control.spset import SPSet


class SPClientProtocol(amp.AMP):
    '''
    Implicitly defines the API of a SongPrez client.

    The required methods are:-
        on_connection()
        _running()
        _set_list(setList)
        _song_list(songList)
        _search_list(searchList)

    The optional methods are:-
        _edit_item(SPSong)
        _edit_set(SPSet)
        _show_slides(slideList)
        _show_items(itemList)
        _show_set(SPSet)
        _show_position(item, slide)
        _show_toggles(toggles)
    '''
    def connectionMade(self):
        self.factory.resetDelay()
        self.factory.client.on_connection(self)

    def printerr(self, error):
        from pprint import pprint
        pprint(error)
        return

    def sendMessage(self, message, term=None, item=None, set=None, itemtype=None,
                    relpath=None, callback=None, callbackKeywords={}):
        kwargs = {}
        if term:
            kwargs['term'] = term
        if relpath:
            kwargs['relpath'] = relpath
        if item:
            jsonitem = json.dumps(item.__dict__)
            kwargs['jsonitem'] = jsonitem
        if set:
            jsonset = json.dumps(set.__dict__)
            kwargs['jsonset'] = jsonset
        if itemtype:
            kwargs['itemtype'] = itemtype
        d = self.callRemote(message, **kwargs)
        if not d:
            return
        d.addErrback(self.printerr)
        if callback:
            def json_to_obj(AMPresponse):
                s, name = {None: (SPSet(), 'jsonset'),
                           'song': (SPSong(), 'jsonitem'),
                           'scripture': (None, 'jsonitem')}[itemtype]
                            # Does not work yet, need SPScripture?
                s.__dict__ = json.loads(AMPresponse[name])
                return s
            d.addCallbacks(json_to_obj, self.printerr)
            d.addCallbacks(callback, self.printerr, callbackKeywords=callbackKeywords)

    @Running.responder
    def Running(self):
        print('received running')
        self.factory.client._running()
        return {}

    @SetList.responder
    def SetList(self, curpage, totalpage, jsonlist):
        if curpage == 0:
            self._partSetList = []
        listofset = [json.loads(d) for d in jsonlist]
        self._partSetList.extend(listofset)
        if curpage == totalpage-1:
            self.factory.client._set_list(self._partSetList)
        return {}

    @SongList.responder
    def SongList(self, curpage, totalpage, jsonlist):
        if curpage == 0:
            self._partSongList = []
        listofsong = [json.loads(d) for d in jsonlist]
        self._partSongList.extend(listofsong)
        if curpage == totalpage-1:
            self.factory.client._song_list(self._partSongList)
        return {}

    @SearchList.responder
    def SearchList(self, curpage, totalpage, jsonlist):
        if curpage == 0:
            self._partSearchList = []
        listofsearch = [json.loads(d) for d in jsonlist]
        self._partSearchList.extend(listofsearch)
        if curpage == totalpage-1:
            self.factory.client._search_list(self._partSearchList)
        return {}

    @EditItem.responder
    def EditItem(self, itemtype, jsonitem):
        if '_edit_item' not in dir(self.factory.client):
            return {}  # Optional method, return if not found
        if itemtype == 'song':
            item = SPSong()
        else:  # Unimplemented itemtype
            return {}
        item.__dict__ = json.loads(jsonitem)
        self.factory.client._edit_item(itemtype, item)
        return {}

    @EditSet.responder
    def EditSet(self, jsonset):
        if '_edit_set' not in dir(self.factory.client):
            return {}  # Optional method, return if not found
        item = SPSet()
        item.__dict__ = json.loads(jsonset)
        self.factory.client._edit_set(item)
        return {}

    @ShowSlides.responder
    def ShowSlides(self, curpage, totalpage, jsonlist):
        if '_show_slides' not in dir(self.factory.client):
            return {}  # Optional method, return if not found
        if curpage == 0:
            self._partShowSlideList = []
        showslidelist = [json.loads(d) for d in jsonlist]
        self._partShowSlideList.extend(showslidelist)
        if curpage == totalpage-1:
            self.factory.client._show_slides(self._partShowSlideList)
        return {}

    @ShowItems.responder
    def ShowItems(self, curpage, totalpage, jsonlist):
        if '_show_items' not in dir(self.factory.client):
            return {}  # Optional method, return if not found
        if curpage == 0:
            self._partShowItemList = []
        showitemlist = [json.loads(d) for d in jsonlist]
        self._partShowItemList.extend(showitemlist)
        if curpage == totalpage-1:
            self.factory.client._show_items(self._partShowItemList)
        return {}

    @ShowSet.responder
    def ShowSet(self, jsonset):
        if '_show_set' not in dir(self.factory.client):
            return {}  # Optional method, return if not found
        s = SPSet()
        s.__dict__ = json.loads(jsonset)
        self.factory.client._show_set(s)
        return {}

    @ShowPosition.responder
    def ShowPosition(self, item, slide):
        if '_show_position' not in dir(self.factory.client):
            return {}  # Optional method, return if not found
        self.factory.client._show_position(item, slide)
        return {}

    @ShowToggles.responder
    def ShowToggles(self, toggle):
        if '_show_toggles' not in dir(self.factory.client):
            return {}  # Optional method, return if not found
        self.factory.client._show_toggles(toggles)
        return {}


class SPClientFactory(protocol.ReconnectingClientFactory):
    protocol = SPClientProtocol

    def __init__(self, app):
        self.client = app

    def clientConnectionLost(self, connector, reason):
        # Code to handle lost connection (if needed in future)
        protocol.ReconnectingClientFactory.clientConnectionLost(self, connector, reason)

    def clientConnectionFailed(self, conn, reason):
        print("connection failed")
