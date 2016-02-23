#!/usr/bin/env python
import kivy
# kivy.require('1.9.1')
from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import Screen
from kivy.metrics import dp
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.animation import Animation
from kivy.properties import ObjectProperty
from functools import partial
from .fontutil import iconfont
from .buttonrow import Buttons
from ..control.spsong import SPSong

Builder.load_string("""
#:set left_width '75sp'

<LeftLabel@Label>:
    size_hint_x: None
    width: left_width
    text_size: self.size
    align: 'left'
    font_size: app.ui_fs_detail

<RightTextInput@TextInput>:
    multiline: False
    size_hint_y: None
    height: self.minimum_height
    font_size: app.ui_fs_detail

<EditSongScreen>:
    title: title
    author: author
    aka: aka
    key_line: key_line
    filepath: filepath
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
    buttons: buttons
    transposeicon: transposeicon
    BoxLayout:
        orientation: 'vertical'
        padding: '5dp'
        spacing: '5dp'
        ScrollView:
            do_scroll_x: False
            canvas.before:
                Color:
                    rgba: (.125, .125, .125, 1)
                RoundedRectangle:
                    size: self.size
                    pos: self.pos
                    radius: dp(10),
            FloatLayout:
                size_hint_y: None
                height: mainsongbox.height
                BoxLayout:
                    id: mainsongbox
                    padding: '10dp'
                    spacing: '5dp'
                    orientation: 'vertical'
                    size_hint_y: None
                    height: top.height + lyrics.height + bottom.height + dp(30)
                    GridLayout:
                        id: top
                        cols: 2
                        spacing: '5dp'
                        size_hint_y: None
                        height: self.minimum_height
                        LeftLabel:
                            text: 'Title'
                        RightTextInput:
                            id: title
                        LeftLabel:
                            text: 'Author'
                        RightTextInput:
                            id: author
                        LeftLabel:
                            text: 'AKA'
                        RightTextInput:
                            id: aka
                        LeftLabel:
                            text: 'Key Line'
                        RightTextInput:
                            id: key_line
                        LeftLabel:
                            text: 'Saved As'
                        RightTextInput:
                            id: filepath
                            height: self.minimum_height
                            readonly: True
                    TextInput:
                        id: lyrics
                        size_hint_y: None
                        height: self.minimum_height
                        font_size: app.ui_fs_detail
                        font_name: 'NotoSansMono'
                    GridLayout:
                        id: bottom
                        cols: 2
                        spacing: '5dp'
                        size_hint_y: None
                        height: self.minimum_height
                        LeftLabel:
                            text: 'Order'
                        RightTextInput:
                            id: presentation
                        LeftLabel:
                            text: 'Hymn #'
                        RightTextInput:
                            id: hymn_number
                        LeftLabel:
                            text: 'Copyright'
                        RightTextInput:
                            id: copyright
                        LeftLabel:
                            text: 'CCLI'
                        RightTextInput:
                            id: ccli
                        LeftLabel:
                            text: 'Key'
                        RightTextInput:
                            id: key
                        LeftLabel:
                            text: 'Capo'
                        RightTextInput:
                            id: capo
                        LeftLabel:
                            text: 'Tempo'
                        RightTextInput:
                            id: tempo
                        LeftLabel:
                            text: 'Time Sig'
                        RightTextInput:
                            id: time_sig
                        LeftLabel:
                            text: 'Theme'
                        RightTextInput:
                            id: theme
                        LeftLabel:
                            text: 'User 1'
                        RightTextInput:
                            id: user1
                        LeftLabel:
                            text: 'User 2'
                        RightTextInput:
                            id: user2
                        LeftLabel:
                            text: 'User 3'
                        RightTextInput:
                            id: user3
                TouchLabel:
                    transposebar: transposebar
                    id: transposeicon
                    root: root
                    pos: lyrics.x + lyrics.width - 1*self.width, lyrics.y + lyrics.height - 1*self.height
                    color: 0, 0, 0
                    size_hint: None, None
                    size: 2*app.buttonsize, 2*app.buttonsize
                    markup: True
                    opacity: 0.4
                BoxLayout:
                    id: transposebar
                    size_hint: None, None
                    size: app.buttonsize, 13*app.buttonsize
                    pos: transposeicon.x - self.width, transposeicon.y - 5.5*app.buttonsize
                    orientation: 'vertical'
                    opacity: 0
        Buttons:
            id: buttons
            button1_action: root.bt_copy
            button2_action: root.bt_saveas
            button3_action: root.bt_save
""")

class TouchLabel(Label):
    def __init__(self, **kwargs):
        super(TouchLabel, self).__init__(**kwargs)
        Clock.schedule_once(self._finish_init)

    def _finish_init(self, dt):
        app = App.get_running_app()
        for i in range(6, -7, -1):
            prefix = '+' if i >0 else ''
            but = Button(text=prefix+str(i),
                         size_hint=(None, None),
                         size=(app.buttonsize, app.buttonsize))
            but.bind(on_press=partial(self._do_transpose, i))
            self.transposebar.add_widget(but)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            if self.transposebar.opacity != 1:
                anim = Animation(opacity=1, d=0.2)
            else:
                anim = Animation(opacity=0, d=0.2)
            anim.start(self.transposebar)
            return True
        if self.transposebar.opacity == 1:
            anim = Animation(opacity=0, d=0.2)
            anim.start(self.transposebar)
        return False

    def _do_transpose(self, i, instance):
        so = SPSong()
        so.lyrics = self.root.lyrics.text
        so.key = self.root.key.text
        so.transpose(i)
        self.root.lyrics.text = so.lyrics
        self.root.key.text = so.key

class EditSongScreen(Screen):
    song = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(EditSongScreen, self).__init__(**kwargs)
        Clock.schedule_once(self._finish_init)

    def _finish_init(self, dt):
        app = App.get_running_app()
        app.base.bind(current_song=self._update_song)
        self.buttons.button1.text = iconfont('copy', app.ui_fs_button) + ' Copy'
        self.buttons.button2.text = iconfont('saveas', app.ui_fs_button) + ' Save As'
        self.buttons.button3.text = iconfont('save', app.ui_fs_button) + ' Save'
        self.transposeicon.text = iconfont('transpose', 2*app.ui_fs_button)

    def _update_song(self, instance, song):
        self.song = song
        self.song_to_UI()

    def song_to_UI(self):
        songObject = self.song
        self.title.text = songObject.title
        self.author.text = songObject.author
        self.aka.text = songObject.aka
        self.key_line.text = songObject.key_line
        self.filepath.text = songObject.filepath
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

    def bt_copy(self):
        pass

    def bt_saveas(self):
        pass

    def bt_save(self):
        pass
