#!/usr/bin/env python
from twisted.internet import reactor, protocol
from twisted.internet import defer
from twisted.protocols import amp
import json
from .messages import *
from ..control.spsong import SPSong
from ..control.spset import SPSet


class SPClientProtocol(amp.AMP):
    def connectionMade(self):
        self.factory.resetDelay()
        self.factory.client.on_connection(self)

    def printerr(self, error):
        from pprint import pprint
        pprint(error)
        return

    def sendMessage(self, message, term=None, item=None, set=None, itemtype=None,
                    relpath=None, callback=None):
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
        d.addErrback(self.printerr)
        if callback:
            def json_to_obj(AMPresponse):
                s = SPSong() if itemtype else SPSet()
                name = 'jsonitem' if itemtype else 'jsonset'
                s.__dict__ = json.loads(AMPresponse[name])
                return s
            d.addCallbacks(json_to_obj, self.printerr)
            d.addCallbacks(callback, self.printerr)

    @Running.responder
    def running(self):
        self.factory.client._running()
        return {}

    @SetList.responder
    def setList(self, curpage, totalpage, jsonlist):
        if curpage == 0:
            self._partSetList = []
        listofset = [json.loads(d) for d in jsonlist]
        self._partSetList.extend(listofset)
        if curpage == totalpage-1:
            self.factory.client._set_list(self._partSetList)
        return {}

    @SongList.responder
    def songList(self, curpage, totalpage, jsonlist):
        if curpage == 0:
            self._partSongList = []
        listofsong = [json.loads(d) for d in jsonlist]
        self._partSongList.extend(listofsong)
        if curpage == totalpage-1:
            self.factory.client._song_list(self._partSongList)
        return {}

    @SearchList.responder
    def searchList(self, curpage, totalpage, jsonlist):
        if curpage == 0:
            self._partSearchList = []
        listofsearch = [json.loads(d) for d in jsonlist]
        self._partSearchList.extend(listofsearch)
        if curpage == totalpage-1:
            self.factory.client._search_list(self._partSearchList)
        return {}

    @EditItem.responder
    def editItem(self, itemtype, jsonitem):
        if itemtype == 'song':
            item = SPSong()
        else:  # Unimplemented itemtype
            return {}
        item.__dict__ = json.loads(jsonitem)
        self.factory.client._edit_item(itemtype, item)
        return {}

    @EditSet.responder
    def editSet(self, jsonset):
        item = SPSet()
        item.__dict__ = json.loads(jsonset)
        self.factory.client._edit_set(item)
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
