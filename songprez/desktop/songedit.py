#!/usr/bin/env python
import kivy
# kivy.require('1.9.0')
from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from blinker import signal
from copy import deepcopy
from .textinput import SingleLineTextInput, RegisteredTextInput
from .filenamedialog import FilenameDialog

Builder.load_string("""
<SongEdit>:
    songname: songname
    songauthor: songauthor
    songlyrics: songlyrics
    orientation: 'vertical'
    padding: 0
    spacing: app.rowspace
    size_hint_x: None
    width: app.colwidth*7 + app.colspace*6
    BoxLayout:
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
    BoxLayout:
        orientation: 'horizontal'
        size_hint_y: None
        height: app.rowheight
        padding: 0
        spacing: app.colspace
        NormalSizeFocusButton:
            text: 'Add to Set'
            on_press: signal('addSong').send(None)
        NormalSizeFocusButton:
            text: 'Remove from Set'
            on_press: signal('removeSong').send(None)
        Widget:
        NormalSizeFocusButton:
            text: 'Save Song As'
            on_press: root._save_as()
        NormalSizeFocusButton:
            text: 'Save Song'
            on_press: root._save()
""")


class SongEdit(BoxLayout):
    def __init__(self, **kwargs):
        super(SongEdit, self).__init__(**kwargs)
        signal('curSong').connect(self._update_song)

    def _update_song(self, sender, **kwargs):
        songObject = kwargs.get('Song')
        self._songInit = songObject
        self.songname.text = songObject.title
        if songObject.author:
            self.songauthor.text = songObject.author
        else:
            self.songauthor.text = ''
        self.songlyrics.text = songObject.lyrics

    def _song_from_textinput(self):
        songObject = deepcopy(self._songInit)
        songObject.title = self.songname.text
        songObject.author = self.songauthor.text
        songObject.lyrics = self.songlyrics.text
        return songObject

    def _save(self):
        songObject = self._song_from_textinput()
        if songObject != self._songInit:
            signal('saveSong').send(self, Song=songObject)

    def _save_as(self):
        songObject = self._song_from_textinput()
        view = FilenameDialog('saveSong', Song=songObject)
        view.textinput.text = songObject.filepath
        view.open()
