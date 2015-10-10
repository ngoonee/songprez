#!/usr/bin/env python
import kivy
# kivy.require('1.9.0')
from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from blinker import signal
from .button import FocusButton, NormalSizeFocusButton
from .itemlist import ItemList
from .setlist import SetList
from .contentlist import ContentList
from .songedit import SongEdit

Builder.load_string("""
#:import signal blinker.signal
<BaseWidget>:
    songedit: songedit
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
    SongEdit:
        id: songedit
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
        Clock.schedule_once(self._finish_init)

    def _finish_init(self, dt):
        pass
