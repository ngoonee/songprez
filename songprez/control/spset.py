#!/usr/bin/env python

import os
import sys
if sys.version_info[0] < 3:
    from codecs import open  # 'UTF-8 aware open'
else:
    def unicode(input):  # Hack to allow use of 'unicode' function
        return str(input)  # in python 3
from xml.dom import minidom
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

    def __unicode__(self):
        printout = ["<Set Object - Name: " + self.name + ". Contents are:-"]
        for i in self._items:
            printout.append(i['type'].title() + ': ' + i['name'])
        printout[-1] += ">"
        return "\n".join(printout)

    def __repr__(self):
        try:  # Python3 path
            return str(self.__unicode__())
        except UnicodeError:
            return unicode(self).encode('utf-8')

    def __eq__(self, other):
        '''
        This ignores value of 'name', which is probably the behaviour we want.
        Compares items rather than just songs, so that I don't have to scratch
        my head later on trying to figure out why scripture/presentations etc
        don't compare well. Probably should have more fine-grained, but that's
        just TODO I guess.
        '''
        if other == None:
            return False
        if type(other) != type(self):
            return False
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
            raise LookupError("Unable to parse {}, not valid XML"
                              .format(filepath))
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
        # Set the correct path
        retval.filepath = relpath
        # Set the correct name
        retval.name = root.attrib.get('name')
        try:
            items = root.getchildren()[0]
        except IndexError:
            # No children means no items/songs (empty set)
            return retval
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
        cls.totaltime += time.time() - starttime
        return retval

    def write_to_file(self, filepath):
        '''
        Write this Set object to an XML file at filepath.
        '''
        root = etree.Element('set', {'name': self.name})
        slide_groups = etree.SubElement(root, 'slide_groups')
        for item in self._items:
            if item['type'] == 'song':
                attrib = {a: item[a] for a in ['name', 'path',
                                               'presentation', 'type']}
                slide_group = etree.Element('slide_group', attrib)
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
                    #slide_group.attrib[s] = item[s]
                    slide_group.set(s, item[s])
                slide_groups.append(slide_group)
            elif item['type'] == 'image':
                pass
            elif item['type'] == 'custom':
                pass
        # Prettify it and then write it to file
        dom = minidom.parseString(etree.tostring(root, 'utf-8'))
        xml_string = dom.toprettyxml(indent="  ", encoding="UTF-8")
        with open(filepath, 'w', encoding='utf8') as f:
            f.write(xml_string)

    def add_item(self, item, itemtype, index=-1):
        '''
        Add an item of itemtype to this list. Defaults to adding to end.
        '''
        if itemtype == 'song':
            filepath = item.filepath
            basedir, name = os.path.split(filepath)
            if basedir:
                basedir += "/"
            list_item = {'name': name, 'type': u'song',
                         'presentation': u'',  # Start with no custom order
                         'path': basedir}
        else:
            return
        if index == -1:
            self._items.append(list_item)
        else:
            self._items.insert(index, list_item)

    def remove_item(self, relpath, index):
        '''
        Remove the item at this index.
        '''
        item = self._items[index]
        if item['type'] == 'song':
            if item['path']:
                path = os.path.normpath(item['path']+item['name'])
            else:
                path = item['name']
            if relpath == path:
                self._items.pop(index)

    def list_songs(self):
        retval = []
        for s in self._items:
            if s['type'] == 'song':
                retval.append({'name': s['name'],
                               'itemtype': s['type'],
                               'presentation': s['presentation'],
                               'filepath': os.path.normpath(s['path']+
                                                            s['name'])})
        return retval

    def from_song_list(self, songList):
        self._items = []
        for s in songList:
            if s['itemtype'] == 'song':
                self._items.append({'name': s['name'],
                                    'type': s['itemtype'],
                                    'presentation': s['presentation'],
                                    'path': os.path.dirname(s['filepath'])})
