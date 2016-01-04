#!/usr/bin/env python
import kivy
# kivy.require('1.9.0')
from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty
from copy import deepcopy
from .textinput import SingleLineTextInput, RegisteredTextInput
from .filenamedialog import FilenameDialog
from .label import MinimalLabel
from ..control.spsong import SPSong
from .spinner import FocusSpinner
from .itemlist import ItemList
from ..network.messages import *

Builder.load_string("""
<ScriptureEdit>:
    booklist: booklist
    chapterlist: chapterlist
    verselist: verselist
    content: content
    sendMessage: app.sendMessage
    BoxLayout:
        orientation: 'vertical'
        BoxLayout:
            orientation: 'horizontal'
            ItemList:
                id: booklist
            ItemList:
                id: chapterlist
            ItemList:
                id: verselist
        RegisteredTextInput:
            id: content
""")


class ScriptureEdit(Screen):
    version = StringProperty(u'')
    book = StringProperty(u'')
    chapter = StringProperty(u'')

    def __init__(self, **kwargs):
        super(ScriptureEdit, self).__init__(**kwargs)
        Clock.schedule_once(self._finish_init)

    def _finish_init(self, dt):
        self.booklist.bind(adapter=self._update_book_adapter)
        self.chapterlist.bind(adapter=self._update_chapter_adapter)

    def _update_book_adapter(self, instance, value):
        instance.adapter.bind(on_selection_change=self._book_selected)

    def _update_chapter_adapter(self, instance, value):
        instance.adapter.bind(on_selection_change=self._chapter_selected)

    def _book_selected(self, adapter):
        def act(AMPresponse):
            chapters = [{'name': c, 'filepath': c}
                        for c in AMPresponse['chapterlist']]
            self.chapterlist.set_data(chapters)
        self.book = adapter.selection[0].filepath
        d = self.sendMessage(GetChapters, version=self.version,
                             book=self.book)
        d.addCallback(act)

    def _chapter_selected(self, adapter):
        def act(AMPresponse):
            versenumbers = [{'name': v, 'filepath': v}
                      for v in AMPresponse['verselist']]
            self.verselist.set_data(versenumbers)
            verses = AMPresponse['verses']
            self.content.text = "\n".join([": ".join(v) for v in verses])
        self.chapter = adapter.selection[0].filepath
        d = self.sendMessage(GetVerses, version=self.version,
                             book=self.book, chapter=self.chapter)
        d.addCallback(act)

    def update_booklist(self, version, booklist):
        self.version = version
        self.booklist.set_data([{'name': n, 'filepath': n} for n in booklist])
