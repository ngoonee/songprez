#!/usr/bin/env python
from twisted.internet import reactor, protocol
from twisted.internet import defer
from twisted.protocols import amp
import json
import logging
logger = logging.getLogger(__name__)
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
        _scripture_list(scriptureList)

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
        logger.error('SPClient: Client %s generated error %s',
                     self.factory.client, error)
        return

    def sendMessage(self, message, **kwargs):
        # deprecated
        logger.debug(u'SPClient: sending message %s with arguments %s',
                     message, kwargs)
        if kwargs.get('item'):
            jsonitem = json.dumps(kwargs.pop('item').__dict__)
            kwargs['jsonitem'] = jsonitem
        if kwargs.get('set'):
            jsonset = json.dumps(kwargs.pop('set').__dict__)
            kwargs['jsonset'] = jsonset
        callback = kwargs.pop('callback', None)
        callbackKeywords = kwargs.pop('callbackKeywords', None)
        d = self.callRemote(message, **kwargs)
        if not d:
            return
        d.addErrback(self.printerr)
        if callback:
            def json_to_obj(AMPresponse):
                s, name = {None: (SPSet(), 'jsonset'),
                           'song': (SPSong(), 'jsonitem'),
                           'scripture': (None, 'jsonitem')}[kwargs.get('itemtype')]
                            # Does not work yet, need SPScripture?
                s.__dict__ = json.loads(AMPresponse[name])
                return s
            d.addCallbacks(json_to_obj, self.printerr)
            d.addCallbacks(callback, self.printerr, callbackKeywords=callbackKeywords)
        return d

    @Running.responder
    def Running(self):
        logger.info("SPClient: Received 'running' signal")
        self.factory.client.running()
        return {}

    @SetList.responder
    def SetList(self, curpage, totalpage, jsonlist):
        if curpage == 0:
            self._partSetList = []
        self._partSetList.extend([json.loads(d) for d in jsonlist])
        if curpage == totalpage-1:
            self.factory.client.set_list(self._partSetList)
        return {}

    @SongList.responder
    def SongList(self, curpage, totalpage, jsonlist):
        if curpage == 0:
            self._partSongList = []
        self._partSongList.extend([json.loads(d) for d in jsonlist])
        if curpage == totalpage-1:
            self.factory.client.song_list(self._partSongList)
        return {}

    @ScriptureList.responder
    def ScriptureList(self, curpage, totalpage, jsonlist):
        if curpage == 0:
            self._partScriptureList = []
        self._partScriptureList.extend([json.loads(d) for d in jsonlist])
        if curpage == totalpage-1:
            self.factory.client.scripture_list(self._partScriptureList)
        return {}

    @CurrentSet.responder
    def CurrentSet(self, jsonset):
        if 'current_set' not in dir(self.factory.client):
            return {}  # Optional method, return if not found
        s = SPSet()
        s.__dict__ = json.loads(jsonset)
        self.factory.client.current_set(s)
        return {}

    @CurrentItem.responder
    def CurrentItem(self, itemtype, jsonitem):
        if 'current_item' not in dir(self.factory.client):
            return {}  # Optional method, return if not found
        if itemtype == 'song':
            s = SPSong()
            s.__dict__ = json.loads(jsonitem)
            self.factory.client.current_item(s)
        return {}

    @CurrentPosition.responder
    def CurrentPosition(self, item, slide):
        if 'current_position' not in dir(self.factory.client):
            return {}  # Optional method, return if not found
        self.factory.client.current_position(item, slide)
        return {}

    @CurrentToggles.responder
    def CurrentToggles(self, toggle):
        if 'current_toggles' not in dir(self.factory.client):
            return {}  # Optional method, return if not found
        self.factory.client.current_toggles(toggles)
        return {}


class SPClientFactory(protocol.ReconnectingClientFactory):
    protocol = SPClientProtocol

    def __init__(self, app):
        self.client = app

    def clientConnectionLost(self, connector, reason):
        # Code to handle lost connection (if needed in future)
        protocol.ReconnectingClientFactory.clientConnectionLost(self, connector, reason)

    def clientConnectionFailed(self, conn, reason):
        logger.info('SPClient: Connection %s failed because %s', conn, reason)
