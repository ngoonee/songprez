#!/usr/bin/env python
import kivy
# kivy.require('1.9.0')
from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from blinker import signal
from .textinput import SingleLineTextInput, RegisteredTextInput

Builder.load_string("""
<SongEdit>:
    songname: songname
    songauthor: songauthor
    songlyrics: songlyrics
    orientation: 'vertical'
    spacing: app.rowspace
    BoxLayout:
        orientation: 'horizontal'
        size_hint_y: None
        height: songname.height
        spacing: app.colspace
        SingleLineTextInput:
            id: songname
        SingleLineTextInput:
            id: songauthor
    ScrollView:
        RegisteredTextInput:
            font_name: 'songprez/fonts/NSimSun.ttf'
            size_hint_y: None
            height: self.minimum_height
            id: songlyrics

""")


class SongEdit(BoxLayout):
    def __init__(self, **kwargs):
        super(SongEdit, self).__init__(**kwargs)
        signal('curSong').connect(self._update_song)

    def _update_song(self, sender, **kwargs):
        songObject = kwargs.get('Song')
        print(songObject)
        self.songname.text = songObject.title
        if songObject.author:
            self.songauthor.text = songObject.author
        else:
            self.songauthor.text = ''
        self.songlyrics.text = songObject.lyrics
