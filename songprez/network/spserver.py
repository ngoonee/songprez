#!/usr/bin/env python
from twisted.internet import protocol
from twisted.protocols import amp
import json
import logging
logger = logging.getLogger(__name__)
from .messages import *
from ..control.spset import SPSet
from ..control.spsong import SPSong


class SPServerProtocol(amp.AMP):
    def __init__(self, factory):
        self.factory = factory
        self.control = factory.control

    def connectionMade(self):
        print(self.transport.client)
        logger.info('SPServer: Host: "%s" %s --- Client: %s connected',
                    self.transport.hostname, self.transport.repstr,
                    self.transport.client)
        self.factory.peers.add(self)
        self.control._connection_made()

    def connectionLost(self, reason):
        logger.info('SPServer: Host: "%s" %s --- Client: %s lost connection',
                    self.transport.hostname, self.transport.repstr,
                    self.transport.client)
        self.factory.peers.remove(self)

    @GetItem.responder
    def GetItem(self, itemtype, relpath):
        retval = self.control.get_item(itemtype, relpath)
        return {'jsonitem': json.dumps(retval.__dict__)}

    @GetSet.responder
    def GetSet(self, relpath):
        retval = self.control.get_set(relpath)
        return {'jsonset': json.dumps(retval.__dict__)}

    @Search.responder
    def Search(self, term):
        retval = self.control.search(term)
        jsonlist = [json.dumps({'name': s.title, 'relpath': s.filepath}) for s in retval]
        return {'jsonlist': jsonlist}

    @GetBooks.responder
    def GetBooks(self, version):
        retval = self.control.get_books(version)
        return {'booklist': retval}

    @GetChapters.responder
    def GetChapters(self, version, book):
        retval = self.control.get_chapters(version, book)
        return {'chapterlist': retval}

    @GetVerses.responder
    def GetVerses(self, version, book, chapter):
        verselist, verses = self.control.get_verses(version, book, chapter)
        return {'verselist': verselist, 'verses': verses }

    @ChangeCurrentSet.responder
    def ChangeCurrentSet(self, jsonset):
        set = SPSet()
        set.__dict__ = json.loads(jsonset)
        self.control.change_current_set(set)
        return {}

    @SaveSet.responder
    def SaveSet(self, jsonset, relpath):
        item = SPSet()
        item.__dict__ = json.loads(jsonset)
        self.control.save_set(item, relpath)
        return {}

    @DeleteSet.responder
    def DeleteSet(self, relpath):
        self.control.delete_set(relpath)
        return {}

    @AddItemToSet.responder
    def AddItemToSet(self, itemtype, relpath, position):
        self.control.add_item_to_set(itemtype, relpath, position)
        return {}

    @RemoveItemFromSet.responder
    def RemoveItemFromSet(self, relpath, position):
        self.control.remove_item_from_set(relpath, position)
        return {}

    @ChangeCurrentItem.responder
    def ChangeCurrentItem(self, itemtype, jsonsong):
        song = SPSong()
        song.__dict__ = json.loads(jsonsong)
        self.control.change_current_item(itemtype, song)
        return {}

    @SaveItem.responder
    def SaveItem(self, itemtype, jsonitem, relpath):
        if itemtype == 'song':
            item = SPSong()
        else:  # Not implemented yet
            return {}
        item.__dict__ = json.loads(jsonitem)
        self.control.save_item(itemtype, item, relpath)
        return {}

    @DeleteItem.responder
    def DeleteItem(self, itemtype, relpath):
        self.control.delete_item(itemtype, relpath)
        return {}

    @ChangeCurrentPosition.responder
    def ChangeCurrentPosition(self, item, slide):
        self.control.change_current_position(item, slide)
        return {}

    @ChangeCurrentToggles.responder
    def ChangeCurrentToggles(self, toggle):
        self.control.change_current_toggles(toggle)
        return {}


class SPServerFactory(protocol.Factory):
    protocol = SPServerProtocol

    def __init__(self, app):
        self.control = app
        self.peers = set()

    def buildProtocol(self, addr):
        return self.protocol(self)

    def _printerr(self, error):
        logger.error('SPClientControl: error %s', error)
        return

    def _sendPartial(self, message, jsonlist, **kwargs):
        maxlength = 63000
        splitjson = [[]]
        length = 0
        for i, elem in enumerate(jsonlist):
            if length + len(elem) < maxlength:
                splitjson[-1].append(elem)
                length += len(elem)
            else:
                splitjson.append([elem,])
                length = len(elem)
        for p in self.peers:
            for i, lis in enumerate(splitjson):
                kwargs['jsonlist'] = lis
                d = p.callRemote(message, curpage=i,
                                 totalpage=len(splitjson), **kwargs)
                d.addErrback(self._printerr)

    def sendAll(self, message, **kwargs):
        logger.debug(u'SPServer: sending message %s to all', message)
        if kwargs.get('list', None) != None:
            list = kwargs.pop('list')
            jsonlist = [json.dumps(s) for s in list]
            self._sendPartial(message, jsonlist, **kwargs)
        elif kwargs.get('itemlist', None) != None:
            itemlist = kwargs.pop('itemlist')
            jsonlist = [json.dumps(s.__dict__) for s in itemlist]
            self._sendPartial(message, jsonlist, **kwargs)
        else:
            if kwargs.get('item'):
                item = kwargs.pop('item')
                kwargs['jsonitem'] = json.dumps(item.__dict__)
            if kwargs.get('set'):
                set = kwargs.pop('set')
                kwargs['jsonset'] = json.dumps(set.__dict__)
            for p in self.peers:
                d = p.callRemote(message, **kwargs)
                d.addErrback(self._printerr)
