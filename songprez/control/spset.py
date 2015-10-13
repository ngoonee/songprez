#!/usr/bin/env python

import os
import xmltodict
from xml.parsers.expat import ExpatError
from collections import OrderedDict
from copy import deepcopy
from .spsong import SPSong

FileNotFoundError = getattr(__builtins__,'FileNotFoundError', IOError)

class SPSet(object):
    def __init__(self, **kwargs):
        self.filepath = ''
        self.name = "Unnamed Set"
        self._items = []

    def __repr__(self):
        printout = ["<Set Object - Name: " + self.name + ". Contents are:-"]
        for i in self._items:
            printout.append(i['@type'].title() + ': ' + i['@name'])
        printout[-1] += ">"
        return "\n".join(printout)

    def __eq__(self, other):
        '''
        This ignores value of 'name', which is probably the behaviour we want.
        Compares items rather than just songs, so that I don't have to scratch
        my head later on trying to figure out why scripture/presentations etc
        don't compare well. Probably should have more fine-grained, but that's
        just TODO I guess.
        '''
        for (me, you) in zip(self._items, other._items):
            if me != you:
                return False
        return True

    def __ne__(self, other):
        return not(self.__eq__(other))

    @classmethod
    def read_from_file(cls, filepath):
        '''
        Loads an XML file at filepath to create a Set object. Returns None if
        filepath is not a valid XML.
        '''
        with open(filepath, 'rb') as f:
            data = f.read()
            try:
                obj = xmltodict.parse(data)
            except ExpatError:
                return
            setobj = obj['set']
        # Find the base OpenSong directory by walking up the path to find the
        # parent of 'Sets'
        basedir, filename = os.path.split(filepath)
        relpath = ''
        while filename != 'Sets':
            if relpath:
                relpath = os.path.join(filename, relpath)
            else:
                relpath = filename
            basedir, filename = os.path.split(basedir)
            if filename == '':
                raise IOError("%s is not in a proper directory structure"
                              % filepath)
        retval = cls()
        retval.filepath = relpath
        retval.name = setobj['@name']
        try:
            items = setobj['slide_groups']['slide_group']
        except TypeError:
            return retval
        items = items if type(items) is list else [items]
        # Workaround for the fact that single-entry Sets get parsed
        # differently by xmltodict
        for item in items:
            if item['@type'] == 'song':
                songPath = (basedir + os.path.sep + 'Songs' + os.path.sep +
                            item['@path'] + os.path.sep + item['@name'])
                songPath = os.path.normpath(songPath)
                try:
                    item['song'] = SPSong.read_from_file(songPath)
                except FileNotFoundError:
                    item['song'] = SPSong()
                    SPSong.title = 'File was not found'
                    SPSong.filepath = songPath
                retval._items.append(item)
            elif item['@type'] == 'scripture':
                retval._items.append(item)
            elif item['@type'] == 'image':
                retval._items.append(item)
            elif item['@type'] == 'custom':
                retval._items.append(item)
        return retval

    def write_to_file(self, filepath):
        '''
        Write this Set object to an XML file at filepath.
        '''
        _items = []
        for item in self._items:
            it = deepcopy(item)
            if it['@type'] == 'song':
                it.pop('song')
            _items.append(it)
        setobj = OrderedDict()
        setobj['@name'] = self.name
        setobj['slide_groups'] = OrderedDict()
        setobj['slide_groups']['slide_group'] = _items
        obj = OrderedDict()
        obj['set'] = setobj
        try:
            with open(filepath, 'w', encoding='UTF-8') as f:
                f.write(xmltodict.unparse(obj, pretty=True))
        except TypeError:
            # 'encoding' is not a valid keyword argument in python2
            with open(filepath, 'wb') as f:
                f.write(xmltodict.unparse(obj, pretty=True))

    def add_song(self, songObj):
        '''
        Add a Song to this set.
        '''
        filepath = songObj.filepath
        basedir, name = os.path.split(filepath)
        item = OrderedDict([('@name', name), ('@type', 'song'),
                           ('@presentation', ''), ('@path', filepath),
                           ('song', songObj)])
        self._items.append(item)

    def remove_song(self, obj):
        '''
        Remove this Song (if it exists) from this set.
        '''
        i = None
        for index, item in enumerate(self._items):
            if (item['@type'] == 'song' and
                    item['song'].filepath == obj.filepath):
                i = index
        if i != None:
            self._items.pop(i)

    def move_song_down(self, obj):
        '''
        Move this Song (if it exists) further behind in the set.
        '''
        i = None
        for index, item in enumerate(self._items):
            if item['@type'] == 'song' and item['song'] == obj:
                i = index
        if i is not None and i+1 < len(self._items):
            self._items[i], self._items[i+1] = self._items[i+1], self._items[i]

    def move_song_up(self, obj):
        '''
        Move this Song (if it exists) further behind in the set.
        '''
        i = None
        for index, item in enumerate(self._items):
            if item['@type'] == 'song' and item['song'] == obj:
                i = index
        if i and i > 0:
            self._items[i], self._items[i-1] = self._items[i-1], self._items[i]

    def list_songs(self):
        return [s['song'] for s in self._items if s['@type'] == 'song']
