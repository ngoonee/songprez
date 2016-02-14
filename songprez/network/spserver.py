#!/usr/bin/env python
from twisted.internet import protocol
from twisted.protocols import amp
import json
from .messages import *
from ..control.spset import SPSet
from ..control.spsong import SPSong


class SPServerProtocol(amp.AMP):
    def __init__(self, factory):
        self.factory = factory
        self.control = factory.control

    def connectionMade(self):
        self.factory.peers.add(self)
        self.control._connection_made()

    def connectionLost(self, reason):
        self.factory.peers.remove(self)

    @GetItem.responder
    def GetItem(self, itemtype, relpath):
        retval = self.control._get_item(itemtype, relpath)
        return {'jsonitem': json.dumps(retval.__dict__)}

    @GetSet.responder
    def GetSet(self, relpath):
        retval = self.control._get_set(relpath)
        return {'jsonset': json.dumps(retval.__dict__)}

    @Search.responder
    def Search(self, term):
        self.control._search(term)
        return {}

    @GetBooks.responder
    def GetBooks(self, version):
        retval = self.control._get_books(version)
        return {'booklist': retval}

    @GetChapters.responder
    def GetChapters(self, version, book):
        retval = self.control._get_chapters(version, book)
        return {'chapterlist': retval}

    @GetVerses.responder
    def GetVerses(self, version, book, chapter):
        verselist, verses = self.control._get_verses(version, book, chapter)
        return {'verselist': verselist, 'verses': verses }

    @ChangeEditItem.responder
    def ChangeEditItem(self, itemtype, relpath):
        self.control._change_edit_item(itemtype, relpath)
        return {}

    @SaveEditItem.responder
    def SaveEditItem(self, itemtype, jsonitem, relpath):
        if itemtype == 'song':
            item = SPSong()
        else:  # Not implemented yet
            return {}
        item.__dict__ = json.loads(jsonitem)
        self.control._save_edit_item(itemtype, item, relpath)
        return {}

    @NewEditItem.responder
    def NewEditItem(self, itemtype, relpath):
        self.control._new_edit_item(itemtype, relpath)
        return {}

    @DeleteEditItem.responder
    def DeleteEditItem(self, itemtype, relpath):
        self.control._delete_edit_item(itemtype, relpath)
        return {}

    @ChangeEditSet.responder
    def ChangeEditSet(self, relpath):
        self.control._change_edit_set(relpath)
        return {}

    @SaveEditSet.responder
    def SaveEditSet(self, jsonset, relpath):
        item = SPSet()
        item.__dict__ = json.loads(jsonset)
        self.control._save_edit_set(item, relpath)
        return {}

    @NewEditSet.responder
    def NewEditSet(self, relpath):
        self.control._new_edit_set(relpath)
        return {}

    @DeleteEditSet.responder
    def DeleteEditSet(self, relpath):
        self.control._delete_edit_set(relpath)
        return {}

    @Resolution.responder
    def Resolution(self, width, height):
        self.control._resolution(width, height)
        return {}

    @ChangeShowSet.responder
    def ChangeShowSet(self, relpath):
        self.control._change_show_set(relpath)
        return {}

    @AddShowItem.responder
    def AddShowItem(self, itemtype, relpath, position):
        self.control._add_show_item(itemtype, relpath, position)
        return {}

    @RemoveShowItem.responder
    def RemoveShowItem(self, position):
        self.control._remove_show_item(position)
        return {}

    @UpdateShowPosition.responder
    def UpdateShowPosition(self, item, slide):
        self.control._update_show_position(item, slide)
        return {}

    @UpdateShowToggles.responder
    def UpdateShowToggles(self, toggle):
        self.control._update_show_toggles(toggle)
        return {}


class SPServerFactory(protocol.Factory):
    protocol = SPServerProtocol

    def __init__(self, app):
        self.control = app
        self.peers = set()

    def buildProtocol(self, addr):
        print(addr, 'connected')
        return self.protocol(self)

    def _sendPartial(self, message, jsonlist, **kwargs):
        maxlength = 64000
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

    def sendAll(self, message, **kwargs):
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
