#!/usr/bin/env python
import kivy
# kivy.require('1.9.0')
from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen, ScreenManager

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
        Button:
            id: pbpresent
            markup: True
            halign: 'center'
            on_press: app.base.to_screen('present')
        Button:
            id: pbsongs
            markup: True
            halign: 'center'
            on_press: app.base.to_screen('songs')
        Button:
            id: pbsearch
            markup: True
            halign: 'center'
            on_press: app.base.to_screen('search')
        Button:
            id: pbscripture
            markup: True
            halign: 'center'
            on_press: app.base.to_screen('scripture')
        Button:
            id: pbsettings
            markup: True
            halign: 'center'
            on_press: app.base.to_screen('settings')
""")


"""
Icons we'll need
square-inc-cash (Donate) f5b9
menu (Menu) f44e
library (Sets) f423
presentation-play (present) f518
file-document (songs) f30e
sword (scripture) f5d3
settings (settings) f582
magnify (search) f43b
pencil (edit) f4da
content-save (save) f289
music-note-off (chords off) f47b
delete (trashcan) f2b5
close-circle (cancel) f250
plus (add new) f504
playlist-plus (add to list) f501
playlist-remove (remove from list) f502
content-copy (copy) f285
at (save as) f15c
alphabetical (language) f5a9
format-indent-increase (show set) f36b
arrow-up-bold (move item up the list) f157
arrow-down-bold (move item down the list) f145
book (bible version) f1b0
"""

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        Clock.schedule_once(self._finish_init)

    def _finish_init(self, dt):
        self.pbsets.text = u'''[font=MaterialDesignIcons][size=92dp]\uf423
                               [/size][/font]\nSets'''
        self.pbpresent.text = u'''[font=MaterialDesignIcons][size=92dp]\uf518
                               [/size][/font]\nPresent'''
        self.pbsongs.text = u'''[font=MaterialDesignIcons][size=92dp]\uf30e
                               [/size][/font]\nSongs'''
        self.pbsearch.text = u'''[font=MaterialDesignIcons][size=92dp]\uf43b
                               [/size][/font]\nSearch'''
        self.pbscripture.text = u'''[font=MaterialDesignIcons][size=92dp]\uf5d3
                               [/size][/font]\nScripture'''
        self.pbsettings.text = u'''[font=MaterialDesignIcons][size=92dp]\uf582
                               [/size][/font]\nSettings'''
