#!/usr/bin/env python
import kivy
# kivy.require('1.9.0')
from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from copy import deepcopy
from .textinput import SingleLineTextInput, RegisteredTextInput
from .filenamedialog import FilenameDialog
from .label import MinimalLabel
from ..control.spsong import SPSong
from .spinner import FocusSpinner
from ..network.messages import *

Builder.load_string("""
<SongEdit>:
    title: title
    author: author
    aka: aka
    key_line: key_line
    filepath: filepath
    transposespinner: transposespinner
    presentation: presentation
    copyright: copyright
    ccli: ccli
    key: key
    tempo: tempo
    capo: capo
    capo_print: capo_print
    time_sig: time_sig
    theme: theme
    hymn_number: hymn_number
    user1: user1
    user2: user2
    user3: user3
    lyrics: lyrics
    scroll: scroll
    addtoset: addtoset
    removefromset: removefromset
    sendMessage: app.sendMessage
    BoxLayout:
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
        BoxLayout:
            orientation: 'horizontal'
            size_hint_y: None
            padding_y: app.rowspace
            height: app.rowheight
            MinimalLabel:
                text: 'Song saved as '
                id: filepath_pre
            MinimalLabel:
                size_hint_x: 1
                text_size: self.parent.width - filepath_pre.width - filepath_post.width - 2*app.rowspace, None
                shorten: True
                id: filepath
            BoxLayout:
                id: filepath_post
                orientation: 'horizontal'
                size_hint_x: None
                spacing: app.colspace
                width: transposelabel.width + transposespinner.width + app.colspace
                MinimalLabel:
                    id: transposelabel
                    markup: True
                    text: ' [color=ffff00][b]T[/b][/color]ranspose:'
                FocusSpinner:
                    mimic_size: True
                    id: transposespinner
                    size_hint: None, None
                    size: app.colwidth, app.rowheight
                    values: (str(n) if n<1 else '+' + str(n) for n in range(-6,7))
                    text: '0'
                    on_text: root._transpose(self.text); self.text='0'
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
                    font_name: 'NotoSansMono'
                    line_spacing: -lyrics.font_size/2.4
                    size_hint_y: None
                    # Required, otherwise last line is half cut off
                    height: self.minimum_height - self.line_spacing
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
                        text: ' Print:'
                    CheckBox:
                        id: capo_print
                    MinimalLabel:
                        text: ' Tempo:'
                    SingleLineTextInput:
                        id: tempo
                    MinimalLabel:
                        text: ' Time Sig:'
                    SingleLineTextInput:
                        id: time_sig
                GridLayout:
                    cols: 2
                    size_hint_y: None
                    spacing: app.rowspace
                    height: theme.height + user1.height + user2.height +\
                            user3.height + 3*app.rowspace
                    MinimalLabel:
                        text: 'Theme:'
                    SingleLineTextInput:
                        id: theme
                    MinimalLabel:
                        text: 'User 1:'
                    RegisteredTextInput:
                        id: user1
                        size_hint_y: None
                        height: self.minimum_height
                    MinimalLabel:
                        text: 'User 2:'
                    RegisteredTextInput:
                        id: user2
                        size_hint_y: None
                        height: self.minimum_height
                    MinimalLabel:
                        text: 'User 3:'
                    RegisteredTextInput:
                        id: user3
                        size_hint_y: None
                        height: self.minimum_height
        BoxLayout:
            orientation: 'horizontal'
            size_hint_y: None
            height: app.rowheight
            padding: 0
            spacing: app.colspace
            NormalSizeFocusButton:
                id: addtoset
                markup: True
                text: '[color=ffff00][b]A[/b][/color]dd to Set'
                on_press: root._add_song()
            NormalSizeFocusButton:
                id: removefromset
                markup: True
                text: '[color=ffff00][b]R[/b][/color]emove from Set'
                on_press: root._remove_song()
            Widget:
            NormalSizeFocusButton:
                text: 'Save Song As'
                on_press: root._save_as()
            NormalSizeFocusButton:
                text: 'Save Song'
                on_press: root._save()
""")


class SongEdit(Screen):
    def __init__(self, **kwargs):
        super(SongEdit, self).__init__(**kwargs)

    def _edit_song(self, song):
        self._songInit = song
        self._song_to_textinput(song)

    def _song_to_textinput(self, songObject):
        self.title.text = songObject.title
        self.author.text = songObject.author
        self.aka.text = songObject.aka
        self.key_line.text = songObject.key_line
        self.filepath.text = songObject.filepath
        self.presentation.text = songObject.presentation
        self.copyright.text = songObject.copyright
        self.ccli.text = songObject.ccli
        self.key.text = songObject.key
        self.capo.text = songObject.capo
        self.capo_print.active = songObject.capo_print
        self.tempo.text = songObject.tempo
        self.time_sig.text = songObject.time_sig
        self.theme.text = songObject.theme
        self.hymn_number.text = songObject.hymn_number
        self.user1.text = songObject.user1
        self.user2.text = songObject.user2
        self.user3.text = songObject.user3
        self.lyrics.text = songObject.lyrics

    def _song_from_textinput(self):
        try:
            songObject = deepcopy(self._songInit)
        except AttributeError:
            return None
            # Hit if transpose is run before song is loaded
        songObject.title = self.title.text
        songObject.author = self.author.text
        songObject.aka = self.aka.text
        songObject.key_line = self.key_line.text
        songObject.filepath = self.filepath.text 
        songObject.presentation = self.presentation.text
        songObject.copyright = self.copyright.text
        songObject.ccli = self.ccli.text
        songObject.key = self.key.text
        songObject.capo = self.capo.text
        songObject.capo_print = self.capo_print.active
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
        if songObject and songObject != self._songInit:
            self.sendMessage(SaveEditItem, itemtype='song', item=songObject,
                             relpath=songObject.filepath)

    def _save_as(self):
        songObject = self._song_from_textinput()
        if songObject:
            view = FilenameDialog(SaveEditItem, inittext=songObject.filepath,
                                  itemtype='song', item=songObject)

    def _transpose(self, interval):
        numInterval = int(interval)
        songObject = self._song_from_textinput()
        if songObject and numInterval:
            songObject.transpose(numInterval)
            self._song_to_textinput(songObject)

    def _add_song(self):
        songObject = self._song_from_textinput()
        app = App.get_running_app()
        if songObject and app.base.currentset._set:
            app.base.currentset._set.add_song(songObject)
            app.base.currentset._set_to_list()

    def _remove_song(self):
        songObject = self._song_from_textinput()
        app = App.get_running_app()
        if songObject and app.base.currentset._set:
            app.base.currentset._set.remove_song(songObject)
            app.base.currentset._set_to_list()
