#!/usr/bin/env python
import kivy
# kivy.require('1.9.0')
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from blinker import signal
from .button import FocusButton, NormalSizeFocusButton
from .itemlist import ItemList
from .setlist import SetList
from .contentlist import ContentList

Builder.load_string("""
#:import blinker blinker
<BaseWidget>:
    orientation: 'horizontal'
    colwidth: self.width//13
    colspace: self.width//140
    rowheight: self.colwidth//3
    rowspace: self.colspace//2
    padding: (self.width - self.colwidth*12 - self.colspace*11)//2
    spacing: self.colspace
    curset: curset
    songlist: contentlist.songlist
    setlist: contentlist.setlist
    searchlist: contentlist.searchlist
    BoxLayout:
        orientation: 'vertical'
        padding: 0
        spacing: root.rowspace*3
        size_hint_x: None
        width: root.colwidth*3 + root.colspace*2
        ContentList:
            id: contentlist
            size_hint_y: 4
        SetList:
            id: curset
            size_hint_y: 3
    BoxLayout:
        orientation: 'vertical'
        padding: 0
        spacing: root.rowspace
        size_hint_x: None
        width: root.colwidth*7 + root.colspace*6
        Button:
        BoxLayout:
            orientation: 'horizontal'
            size_hint_y: None
            height: root.rowheight
            padding: 0
            spacing: root.colspace
            NormalSizeFocusButton:
                text: 'Add to Set'
                on_release: blinker.signal('getSets').send(None)
            NormalSizeFocusButton:
                text: 'Remove from Set'
                on_release: blinker.signal('getSongs').send(None)
            Widget:
                #size_hint_x: None
                #width: root.colwidth*3 + root.colspace*2
            NormalSizeFocusButton:
                text: 'Save Song As'
                on_release: blinker.signal('search').send(None, SearchTerm='marry')
            NormalSizeFocusButton:
                text: 'Save Song'
                on_release: blinker.signal('publishAll').send(None)
    BoxLayout:
        orientation: 'vertical'
        padding: 0
        spacing: root.rowspace
        size_hint_x: None
        width: root.colwidth*2 + root.colspace*1
        Button:
        BoxLayout:
            orientation: 'horizontal'
            size_hint_y: None
            height: root.rowheight
            spacing: root.colspace
            BoxLayout:
                size_hint_x: None
                width: root.colwidth
            NormalSizeFocusButton:
                text: 'Settings'
        FocusButton:
            size_hint_y: None
            height: root.rowheight*2 + root.rowspace
            text: 'Present'
""")


class BaseWidget(BoxLayout):
    def __init__(self, **kwargs):
        super(BaseWidget, self).__init__(**kwargs)
        signal('curSet').connect(self._monitor_curSet)
        signal('setList').connect(self._monitor_setList)
        signal('songList').connect(self._monitor_songList)
        signal('searchList').connect(self._monitor_searchList)

    def _monitor_curSet(self, sender, **kwargs):
        setObject = kwargs.get('Set')
        self.curset.setcontent.set_data(setObject)

    def _monitor_setList(self, sender, **kwargs):
        setList = kwargs.get('List')
        self.setlist.set_data(setList)

    def _monitor_songList(self, sender, **kwargs):
        songList = kwargs.get('List')
        self.songlist.set_data(songList)

    def _monitor_searchList(self, sender, **kwargs):
        searchList = kwargs.get('List')
        self.searchlist.set_data(searchList)
