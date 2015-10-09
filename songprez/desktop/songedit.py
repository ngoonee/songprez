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
from .label import MinimalLabel

Builder.load_string("""
<SongEdit>:
    title: title
    author: author
    aka: aka
    key_line: key_line
    presentation: presentation
    copyright: copyright
    ccli: ccli
    key: key
    tempo: tempo
    capo: capo
    time_sig: time_sig
    theme: theme
    hymn_number: hymn_number
    user1: user1
    user2: user2
    user3: user3
    lyrics: lyrics
    scroll: scroll
    orientation: 'vertical'
    padding: 0
    spacing: app.rowspace
    size_hint_x: None
    width: app.colwidth*7 + app.colspace*6
    GridLayout:
        cols: 4
        orientation: 'horizontal'
        size_hint_y: None
        height: 2*title.height + app.rowspace
        spacing: [app.colspace, app.rowspace]
        MinimalLabel:
            text: 'Title:'
        SingleLineTextInput:
            id: title
        MinimalLabel:
            text: ' Author:'
        SingleLineTextInput:
            id: author
        # Next line
        MinimalLabel:
            text: 'AKA:'
        SingleLineTextInput:
            id: aka
        MinimalLabel:
            text: 'Key Line:'
        SingleLineTextInput:
            id: key_line
    ScrollView:
        bar_width: 20
        scroll_type: ['bars', 'content']
        effect_cls: 'ScrollEffect'
        GridLayout:
            cols: 1
            id: scroll
            size_hint_y: None
            spacing: app.rowspace
            height: lyrics.height + presentation.height + copyright.height\
                    + key.height + theme.height + user1.height + user2.height\
                    + user3.height + 7*app.rowspace
            RegisteredTextInput:
                font_name: 'songprez/fonts/NSimSun.ttf'
                size_hint_y: None
                height: self.minimum_height
                id: lyrics
            BoxLayout:
                orientation: 'horizontal'
                size_hint_y: None
                spacing: app.colspace
                height: presentation.height
                MinimalLabel:
                    text: 'Presentation Order:'
                SingleLineTextInput:
                    size_hint_x: 3
                    id: presentation
                MinimalLabel:
                    text: ' Hymn Number:'
                SingleLineTextInput:
                    size_hint_x: 1
                    id: hymn_number
            BoxLayout:
                orientation: 'horizontal'
                size_hint_y: None
                spacing: app.colspace
                height: copyright.height
                MinimalLabel:
                    text: 'Copyright:'
                SingleLineTextInput:
                    id: copyright
                MinimalLabel:
                    text: ' CCLI:'
                SingleLineTextInput:
                    id: ccli
            BoxLayout:
                orientation: 'horizontal'
                size_hint_y: None
                spacing: app.colspace
                height: key.height
                MinimalLabel:
                    text: 'Key:'
                SingleLineTextInput:
                    id: key
                MinimalLabel:
                    text: ' Capo:'
                SingleLineTextInput:
                    id: capo
                MinimalLabel:
                    text: ' Tempo:'
                SingleLineTextInput:
                    id: tempo
                MinimalLabel:
                    text: ' Time Sig:'
                SingleLineTextInput:
                    id: time_sig
            BoxLayout:
                orientation: 'horizontal'
                size_hint_y: None
                spacing: app.colspace
                height: theme.height
                MinimalLabel:
                    text: 'Theme:'
                SingleLineTextInput:
                    id: theme
            BoxLayout:
                orientation: 'horizontal'
                size_hint_y: None
                spacing: app.colspace
                height: user1.height
                MinimalLabel:
                    text: 'User 1:'
                RegisteredTextInput:
                    id: user1
            BoxLayout:
                orientation: 'horizontal'
                size_hint_y: None
                spacing: app.colspace
                height: user2.height
                MinimalLabel:
                    text: 'User 2:'
                RegisteredTextInput:
                    id: user2
            BoxLayout:
                orientation: 'horizontal'
                size_hint_y: None
                spacing: app.colspace
                height: user3.height
                MinimalLabel:
                    text: 'User 3:'
                RegisteredTextInput:
                    id: user3
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
        self.title.text = songObject.title
        self.author.text = songObject.author
        self.aka.text = songObject.aka
        self.key_line.text = songObject.key_line
        self.presentation.text = songObject.presentation
        self.copyright.text = songObject.copyright
        self.ccli.text = songObject.ccli
        self.key.text = songObject.key
        # How to deal with capo?
        self.tempo.text = songObject.tempo
        self.time_sig.text = songObject.time_sig
        self.theme.text = songObject.theme
        self.hymn_number.text = songObject.hymn_number
        self.user1.text = songObject.user1
        self.user2.text = songObject.user2
        self.user3.text = songObject.user3
        self.lyrics.text = songObject.lyrics

    def _song_from_textinput(self):
        songObject = deepcopy(self._songInit)
        songObject.title = self.title.text
        songObject.author = self.author.text
        songObject.aka = self.aka.text
        songObject.key_line = self.key_line.text
        songObject.presentation = self.presentation.text
        songObject.copyright = self.copyright.text
        songObject.ccli = self.ccli.text
        songObject.key = self.key.text
        # How to deal with capo?
        songObject.tempo = self.tempo.text
        songObject.time_sig = self.time_sig.text
        songObject.theme = self.theme.text
        songObject.hymn_number = self.hymn_number.text
        songObject.user1 = self.user1.text
        songObject.user2 = self.user2.text
        songObject.user3 = self.user3.text
        songObject.lyrics = self.lyrics.text
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
