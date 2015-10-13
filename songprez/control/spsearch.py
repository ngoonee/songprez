#!/usr/bin/env python

import os
from whoosh.index import create_in, open_dir, exists_in
from whoosh.qparser import MultifieldParser
from whoosh.fields import Schema, TEXT, ID, STORED
from whoosh.lang import porter2
from whoosh.analysis import RegexTokenizer, LowercaseFilter, StopFilter
from whoosh.analysis import StemFilter
from .spsong import SPSong
from .sputil import list_files

_myFilter = (RegexTokenizer() | LowercaseFilter() | StopFilter() |
             StemFilter(porter2.stem))
_schema = Schema(filepath=ID(unique=True, stored=True),
                 time=STORED,
                 title=TEXT(field_boost=2.0, stored=True),
                 aka=TEXT(field_boost=2.0),
                 key_line=TEXT(field_boost=2.0),
                 lyrics=TEXT(analyzer=_myFilter),
                 song=STORED)
# TODO: What about NGrams?


class SPSearch(object):
    def __init__(self, indexPath, dirPath):
        self._indexpath = indexPath
        self._dirpath = dirPath
        ix = self._obtain_index()
        self._ix = ix

    def update_index(self):
        listed_files = list_files(self._dirpath)
        if not self._ix.storage.index_exists():
            self._ix = self._obtain_index()
        ix = self._ix
        indexedPaths = set()
        with ix.searcher() as searcher:
            writer = ix.writer()
            for fields in searcher.all_stored_fields():
                relPath = fields['filepath']
                indexedPath = os.path.join(self._dirpath, relPath)
                indexedPaths.add(indexedPath)
                if not os.path.exists(indexedPath):
                    # File was deleted
                    writer.delete_by_term('filepath', relPath)
                else:
                    # Check if file has changed since indexing
                    indexedTime = fields['time']
                    mtime = os.path.getmtime(indexedPath)
                    if mtime > indexedTime:
                        # Update the file
                        self._update_doc(writer, indexedPath)
            for f in listed_files:
                if f not in indexedPaths:
                    # New file, not seen before
                    self._update_doc(writer, f)
            writer.commit()

    def _update_doc(self, writer, path):
        obj = SPSong.read_from_file(path)
        if obj:
            writer.update_document(filepath=obj.filepath,
                                   time=obj.mtime,
                                   title=obj.title,
                                   aka=obj.aka,
                                   key_line=obj.key_line,
                                   lyrics=obj.words,
                                   song=obj)

    def search(self, term):
        if not self._ix.storage.index_exists():
            self._ix = self._obtain_index()
            self.update_index()
        ix = self._ix
        with ix.searcher() as searcher:
            parser = MultifieldParser(['title', 'aka', 'key_line', 'lyrics'],
                                      ix.schema)
            query = parser.parse(term)
            results = searcher.search(query, limit=None)
            output = [(r['filepath'], r['title']) for r in results]
        return output

    def _obtain_index(self):
        if not os.path.exists(self._indexpath):
            os.mkdir(self._indexpath)
        if exists_in(self._indexpath):
            index = open_dir(self._indexpath)
        else:
            index = create_in(self._indexpath, _schema)
        return index

    def get_song_from_cache(self, path):
        if not self._ix.storage.index_exists():
            self._ix = self._obtain_index()
            self.update_index()
        ix = self._ix
        return ix.searcher().document(filepath=path)['song']
