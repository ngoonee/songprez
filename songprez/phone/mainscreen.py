#!/usr/bin/env python
import kivy
# kivy.require('1.9.0')
from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen, ScreenManager
from .fontutil import iconfont

Builder.load_string("""
<MainScreen>:
    pbsets: pbsets
    pbpresent: pbpresent
    pbsongs: pbsongs
    pbsearch: pbsearch
    pbscripture: pbscripture
    pbsettings: pbsettings
    GridLayout:
        padding: '10dp'
        spacing: '10dp'
        cols: 2
        Button:
            id: pbsets
            markup: True
            halign: 'center'
            on_press: app.base.to_screen('sets')
            font_size: app.ui_fs_title
        Button:
            id: pbpresent
            markup: True
            halign: 'center'
            on_press: app.base.to_screen('present')
            font_size: app.ui_fs_title
        Button:
            id: pbsongs
            markup: True
            halign: 'center'
            on_press: app.base.to_screen('songs')
            font_size: app.ui_fs_title
        Button:
            id: pbsearch
            markup: True
            halign: 'center'
            on_press: app.base.to_screen('search')
            font_size: app.ui_fs_title
        Button:
            id: pbscripture
            markup: True
            halign: 'center'
            on_press: app.base.to_screen('scripture')
            font_size: app.ui_fs_title
        Button:
            id: pbsettings
            markup: True
            halign: 'center'
            on_press: app.base.to_screen('settings')
            font_size: app.ui_fs_title
""")


"""
Icons we'll need
square-inc-cash (donate) f5b9
menu (menu) f44e
library (sets) f423
presentation-play (present) f518
file-document (songs) f30e
sword (scripture) f5d3
settings (settings) f582
magnify (search) f43b
pencil (edit) f4da
content-save (save) f289
music-note-off (chordoff) f47b
delete (delete) f2b5
close-circle (cancel) f250
plus (new) f504
playlist-plus (listadd) f501
playlist-remove (listremove) f502
content-copy (copy) f285
at (saveas) f15c
alphabetical (language) f5a9
format-indent-increase (showset) f36b
arrow-up-bold (listmoveup) f157
arrow-down-bold (listmovedown) f145
book (bibleversion) f1b0
"""

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        Clock.schedule_once(self._finish_init)

    def _finish_init(self, dt):
        self.pbsets.text = iconfont('sets', '92sp') + '\nSets'
        self.pbpresent.text = iconfont('present', '92sp') + '\nPresent'
        self.pbsongs.text = iconfont('songs', '92sp') + '\nSongs'
        self.pbsearch.text = iconfont('search', '92sp') + '\nSearch'
        self.pbscripture.text = iconfont('scripture', '92sp') + '\nScripture'
        self.pbsettings.text = iconfont('settings', '92sp') + '\nSettings'
