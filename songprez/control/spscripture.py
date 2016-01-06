#!/usr/bin/env python

import xmltodict
import os
import sys
if sys.version_info[0] < 3:
    from codecs import open  # 'UTF-8 aware open'
from collections import OrderedDict

class SPBible(object):
    def __init__(self, **kwargs):
        self._bible = None
        self._booklist = None
        self._chapdict = None
        self.name = u''

    def skeleton(self):
        retval = SPBible()
        retval.name = self.name
        retval._booklist = self._booklist
        retval._chapdict = self._chapdict
        return retval

    @classmethod
    def read_from_file(cls, filepath):
        try:
            filepath = unicode(filepath)
        except NameError:
            pass
        with open(filepath, 'r', encoding='UTF-8') as f:
            firstline = f.readline()
            index = firstline.find('encoding')
            encoding = firstline[index:].split('"')[1]
        if not encoding:
            encoding = 'UTF-8'
        obj = None
        with open(filepath, 'r', encoding=encoding) as f:
            data = f.read()
            # Most of the time taken by xmltodict, would lkml save time?
            obj = xmltodict.parse(data)
        retval = cls()
        retval._bible = obj
        retval.name = os.path.split(filepath)[-1]
        if obj:
            retval._index()
            return retval
        else:
            return None

    def _index(self):
        bible = self._bible
        booklist = [b['@n'] for b in bible['bible']['b']]
        chapdict = OrderedDict()
        for b, book in enumerate(booklist):
            chapdict[book] = OrderedDict()
            bookcontent = bible['bible']['b'][b]['c']
            if type(bookcontent) == OrderedDict:
                # Workaround for single-chapter books, make them lists as well
                bible['bible']['b'][b]['c'] = [bible['bible']['b'][b]['c']]
                bookcontent = bible['bible']['b'][b]['c']
            chaplist = [c['@n'] for c in bookcontent]
            for c, chap in enumerate(chaplist):
                chapcontent = bookcontent[c]['v']
                chapdict[book][chap] = [v['@n'] if not v.has_key('@t')
                                        else v['@n'] + '-' + v['@t']
                                        for v in chapcontent]
        self._booklist = booklist
        self._chapdict = chapdict

    def full_chapter(self, book, chapter):
        '''
        '''
        bible, booklist, chapdict = self._bible, self._booklist, self._chapdict
        b = booklist.index(book)
        c = chapdict[book].keys().index(str(chapter))
        return [(i, v['#text']) for i, v in
                zip(chapdict[book][chapter],
                    bible['bible']['b'][b]['c'][c]['v'])]

    def split_slides(self):
        pass
