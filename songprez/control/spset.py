#!/usr/bin/env python

import os
import xmltodict
from collections import OrderedDict
from copy import deepcopy
from .spsong import SPSong


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

    @classmethod
    def read_from_file(cls, filepath):
        '''
        Loads an XML file at filepath to create a Set object.
        '''
        with open(filepath) as f:
            obj = xmltodict.parse(f.read())
            setobj = obj['set']
        # Find the base OpenSong directory by walking up the path to find the
        # parent of 'Sets'
        basedir, filename = os.path.split(filepath)
        while filename != 'Sets':
            basedir, filename = os.path.split(basedir)
            if filename == '':
                raise IOError("%s is not in a proper directory structure"
                              % filepath)
        retval = cls()
        retval.filepath = filepath
        retval.name = setobj['@name']
        items = setobj['slide_groups']['slide_group']
        items = items if type(items) is list else [items]
        # Workaround for the fact that single-entry Sets get parsed
        # differently by xmltodict
        for item in items:
            if item['@type'] == 'song':
                songPath = (basedir + os.path.sep + 'Songs' + os.path.sep +
                            item['@path'] + os.path.sep + item['@name'])
                songPath = os.path.normpath(songPath)
                item['song'] = SPSong.read_from_file(songPath.__str__())
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
        with open(filepath, 'w') as f:
            f.write(xmltodict.unparse(obj, pretty=True))

    def _find_name_path(self, filepath):
        if not filepath:
            return '', ''
        basedir, name = os.path.split(filepath)
        path = ''
        basedir, filename = os.path.split(basedir)
        while filename != 'Songs':
            path = filename + os.path.sep + path
            basedir, filename = os.path.split(basedir)
        return name, path

    def add_song(self, songObj):
        '''
        Add a Song to this set.
        '''
        name, path = self._find_name_path(songObj.filepath)
        item = OrderedDict([('@name', name), ('@type', 'song'),
                           ('@presentation', ''), ('@path', path),
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
        if i:
            self._items.pop(i)

    def move_song_down(self, obj):
        '''
        Move this Song (if it exists) further behind in the set.
        '''
        i = None
        for index, item in enumerate(self._items):
            if item['@type'] == 'song' and item['song'] == obj:
                i = index
        if i and i+1 < len(self._items):
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
