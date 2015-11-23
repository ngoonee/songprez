#!/usr/bin/env python
from twisted.internet import protocol
from twisted.protocols import amp
import json
import blinker
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
    def getItem(self, itemtype, relpath):
        retval = self.control._get_item(itemtype, relpath)
        if not retval:
            return {}
        return {'jsonitem': json.dumps(retval.__dict__)}

    @GetSet.responder
    def getSet(self, relpath):
        retval = self.control._get_set(relpath)
        if not retval:
            return {}
        return {'jsonset': json.dumps(retval.__dict__)}

    @Search.responder
    def search(self, term):
        retval = self.control._search(term)
        return {}

    @ChangeEditItem.responder
    def changeEditItem(self, itemtype, relpath):
        retval = self.control._change_edit_item(itemtype, relpath)
        return {}

    @SaveEditItem.responder
    def saveEditItem(self, itemtype, jsonitem, relpath):
        item = SPSong()
        item.__dict__ = json.loads(jsonitem)
        retval = self.control._save_edit_item(itemtype, item, relpath)
        return {}

    @NewEditItem.responder
    def newEditItem(self, itemtype, relpath):
        retval = self.control._new_edit_item(itemtype, relpath)
        return {}

    @DeleteEditItem.responder
    def deleteEditItem(self, itemtype, relpath):
        retval = self.control._delete_edit_item(itemtype, relpath)
        return {}

    @ChangeEditSet.responder
    def changeEditSet(self, relpath):
        retval = self.control._change_edit_set(relpath)
        return {}

    @SaveEditSet.responder
    def saveEditSet(self, jsonset, relpath):
        item = SPSet()
        item.__dict__ = json.loads(jsonset)
        retval = self.control._save_edit_set(item, relpath)
        return {}

    @NewEditSet.responder
    def newEditSet(self, relpath):
        retval = self.control._new_edit_set(relpath)
        return {}

    @DeleteEditSet.responder
    def deleteEditSet(self, relpath):
        retval = self.control._delete_edit_set(relpath)
        return {}


class SPServerFactory(protocol.Factory):
    protocol = SPServerProtocol

    def __init__(self, app):
        self.control = app
        self.peers = set()

    def buildProtocol(self, addr):
        print(addr, 'connected')
        return self.protocol(self)

    def printerr(self, error):
        from pprint import pprint
        pprint(error)
        return

    def sendAll(self, message, **kwargs):
        if kwargs.get('list'):
            list = kwargs.pop('list')
            jsonlist = [json.dumps(s) for s in list]
            maxitems = 300
            splitjson = [jsonlist[i:i+maxitems]
                         for i in range(0, len(jsonlist), maxitems)]
            for p in self.peers:
                for i, lis in enumerate(splitjson):
                    kwargs['jsonlist'] = lis
                    d = p.callRemote(message, curpage=i,
                                     totalpage=len(splitjson), **kwargs)
        else:
            if kwargs.get('item'):
                item = kwargs.pop('item')
                kwargs['jsonitem'] = json.dumps(item.__dict__)
            if kwargs.get('set'):
                set = kwargs.pop('set')
                kwargs['jsonset'] = json.dumps(set.__dict__)
            for p in self.peers:
                d = p.callRemote(message, **kwargs)
                d.addErrback(self.printerr)
