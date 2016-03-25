#!/usr/bin/env python

import os
import sys
if sys.version_info[0] < 3:
    from codecs import open  # 'UTF-8 aware open'
from xml.parsers.expat import ExpatError
from collections import OrderedDict
from copy import deepcopy
import time
from .spsong import SPSong
from .sputil import etree

FileNotFoundError = getattr(__builtins__,'FileNotFoundError', IOError)

class SPSet(object):
    totaltime = 0  # Time taken for entire reading process

    def __init__(self, **kwargs):
        self.filepath = ''
        self.name = "Unnamed Set"
        self._items = []

    def __repr__(self):
        printout = ["<Set Object - Name: " + self.name + ". Contents are:-"]
        for i in self._items:
            printout.append(i['type'].title() + ': ' + i['name'])
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
        if len(self._items) != len(other._items):
            # Different lengths means different sets, obviously
            return False
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
        filepath is not a valid Unicode XML.
        '''
        starttime = time.time()
        try:
            filepath = unicode(filepath)
        except NameError:
            pass
        retval = cls()
        try:
            root = etree.parse(filepath).getroot()
        except etree.ParseError:
            return
        retval.name = root.attrib.get('name')
        items = root.getchildren()[0]
        for item in items:
            if item.attrib['type'] == 'song':
                retval._items.append(dict(item.attrib))
            elif item.attrib['type'] == 'scripture':
                elem = dict(item.attrib)
                for child in item:
                    if child.tag == 'slides':
                        slides = []
                        for s in child:
                            slides.append(s[0].text)
                        elem['slides'] = slides
                    else:
                        elem[child.tag] = child.text
                retval._items.append(elem)
            elif item.attrib['type'] == 'image':
                pass
            elif item.attrib['type'] == 'custom':
                pass
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
        retval.filepath = relpath
        cls.totaltime += time.time() - starttime
        return retval

    def write_to_file(self, filepath):
        '''
        Write this Set object to an XML file at filepath.
        '''
        root = etree.Element('set', attrib={'name': self.name})
        tree = etree.ElementTree(root)
        slide_groups = etree.SubElement(root, 'slide_groups')
        for item in self._items:
            if item['type'] == 'song':
                attrib = {a: item[a] for a in ['name', 'path',
                                               'presentation', 'type']}
                slide_group = etree.Element('slide_group', attrib=attrib)
                slide_groups.append(slide_group)
            elif item['type'] == 'scripture':
                slide_group = etree.Element('slide_group')
                # Handle the title of the set
                title = etree.Element('title')
                title.text = item['title']
                slide_group.append(title)
                # Handle the slides element of the set
                slides = etree.Element('slides')
                for s in item['slides']:
                    slide = etree.Element('slide')
                    body = etree.Element('body')
                    body.text = s
                    slide.append(body)
                    slides.append(slide)
                slide_group.append(slides)
                # Handle the subtitle of the set
                subtitle = etree.Element('subtitle')
                subtitle.text = item['subtitle']
                slide_group.append(subtitle)
                # Handle the notes of the set
                notes = etree.Element('notes')
                notes.text = item['notes']
                slide_group.append(notes)
                # Handle the remaining (all assumed to be attributes)
                keys = [k for k in item.keys() if k not in
                            ['title', 'slides', 'subtitle', 'notes']]
                for s in keys:
                    slide_group.attrib[s] = item[s]
                slide_groups.append(slide_group)
            elif item.attrib['type'] == 'image':
                pass
            elif item.attrib['type'] == 'custom':
                pass
        tree.write(filepath, encoding='UTF-8', pretty_print=True, xml_declaration=True)

    def add_song(self, songObj, index=-1):
        '''
        Add a Song to this set. Default adds to end.
        '''
        filepath = songObj.filepath
        basedir, name = os.path.split(filepath)
        item = {'name': name, 'type': 'song',
                'presentation': songObj.presentation,
                'path': basedir}
        if index == -1:
            self._items.append(item)
        else:
            self._items.insert(index, item)

    def remove_song(self, obj):
        '''
        Remove this Song (if it exists) from this set.
        '''
        i = None
        for index, item in enumerate(self._items):
            itempath = os.path.join(item['path'], item['name'])
            if (item['type'] == 'song' and itempath == obj.filepath):
                i = index
        if i != None:
            self._items.pop(i)

    def list_songs(self):
        retval = []
        for s in self._items:
            if s['type'] == 'song':
                retval.append({'name': s['name'],
                               'itemtype': s['type'],
                               'presentation': s['presentation'],
                               'filepath': os.path.join(s['path'],
                                                        s['name'])})
            '''
            if s['@type'] == 'song':
                retval.append({'name': s['@name'],
                               'itemtype': s['@type'],
                               'presentation': s['@presentation'],
                               'filepath': os.path.join(s['@path'],
                                           s['@name'])})
            elif s['@type'] == 'scripture':
                retval.append({'name': s['@name'],
                               'itemtype': s['@type'],
                               'print': s['@print'],
                               'seconds': s.get('@seconds'),
                               'loop': s.get('@loop'),
                               'transition': s.get('@transition')})
            else:
                retval.append({'name': s['@name'],
                               'itemtype': s['@type']})
            '''
        return retval

    def from_song_list(self, songList):
        self._items = []
        for s in songList:
            if s['itemtype'] == 'song':
                self._items.append({'name': s['name'],
                                    'type': s['itemtype'],
                                    'presentation': s['presentation'],
                                    'path': os.path.dirname(s['filepath'])})
            '''
            if s['itemtype'] == 'song':
                self._items.append({'@name': s['name'],
                                    '@type': s['itemtype'],
                                    '@presentation': s['presentation'],
                                    '@path': os.path.dirname(s['filepath'])})
            elif s['itemtype'] == 'scripture':
                self._items.append({'@name': s['name'],
                                    '@type': s['itemtype'],
                                    '@print': s['print'],
                                    '@seconds': s['seconds'],
                                    '@loop': s['loop'],
                                    '@transition': s['transition']})
            else:
                self._items.append({'@name': s['name'],
                                    '@type': s['itemtype']})
                                    '''
