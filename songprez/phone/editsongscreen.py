#!/usr/bin/env python
import kivy
# kivy.require('1.9.1')
from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import Screen
from kivy.metrics import dp
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.animation import Animation
from kivy.properties import ObjectProperty, StringProperty
from kivymd.label import MDLabel
from kivymd.dialog import MDDialog
from kivymd.button import MDIconButton
from functools import partial
from blinker import signal
from .icontextbutton import TransposeButton
from .saveasdialog import SaveAsDialogContent
from ..control.spsong import SPSong

Builder.load_string("""
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
    capo_print: capo_print
    time_sig: time_sig
    theme: theme
    hymn_number: hymn_number
    user1: user1
    user2: user2
    user3: user3
    lyrics: lyrics
    transposeicon: transposeicon
    sendMessage: app.sendMessage
    BoxLayout:
        orientation: 'vertical'
        ScrollView:
            do_scroll_x: False
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
                    BoxLayout:
                        id: top
                        orientation: 'vertical'
                        cols: 2
                        spacing: dp(10)
                        size_hint_y: None
                        height: self.minimum_height
                        MDTextField:
                            id: title
                            hint_text: 'Title'
                        MDTextField:
                            id: author
                            hint_text: 'Author'
                        MDTextField:
                            id: aka
                            hint_text: 'AKA'
                        MDTextField:
                            id: key_line
                            hint_text: 'Key line'
                        MDTextField:
                            id: filepath
                            hint_text: 'Saved As'
                            height: self.minimum_height
                            readonly: True
                    MDTextField:
                        multiline: True
                        id: lyrics
                        size_hint_y: None
                        height: self.minimum_height if self.minimum_height > transposeicon.height else transposeicon.height
                    BoxLayout:
                        orientation: 'vertical'
                        id: bottom
                        spacing: dp(10)
                        size_hint_y: None
                        height: self.minimum_height
                        MDTextField:
                            id: presentation
                            hint_text: 'Order'
                        MDTextField:
                            id: hymn_number
                            hint_text: 'Hymn number'
                        MDTextField:
                            id: copyright
                            hint_text: 'Copyright'
                        MDTextField:
                            id: ccli
                            hint_text: 'CCLI'
                        MDTextField:
                            id: key
                            hint_text: 'Key'
                        BoxLayout:
                            orientation: 'horizontal'
                            size_hint_y: None
                            height: capo.height
                            MDTextField:
                                id: capo
                                hint_text: 'Capo'
                            Widget:
                                size_hint_x: None
                                width: dp(20)
                            MDLabel:
                                text: 'Print'
                                size_hint_x: None
                                -text_size: (None, capo.height)
                                valign: 'middle'
                                width: self.texture_size[0]
                                font_style: 'Subhead'
                                theme_text_color: 'Hint'
                            CheckBox:
                                id: capo_print
                                size_hint_x: None
                                width: sp(32)
                        MDTextField:
                            id: tempo
                            hint_text: 'Tempo'
                        MDTextField:
                            id: time_sig
                            hint_text: 'Time Signature'
                        MDTextField:
                            id: theme
                            hint_text: 'Theme'
                        MDTextField:
                            id: user1
                            hint_text: 'User 1'
                        MDTextField:
                            id: user2
                            hint_text: 'User 2'
                        MDTextField:
                            id: user3
                            hint_text: 'User 3'
                TouchLabel:
                    transposebar: transposebar
                    id: transposeicon
                    root: root
                    pos: lyrics.x + lyrics.width - self.width, lyrics.y + lyrics.height - self.height
                    icon: 'music-note'
                    opacity: 0.6
                BoxLayout:
                    id: transposebar
                    size_hint: None, None
                    size: dp(24), self.minimum_height
                    spacing: dp(4)
                    pos: transposeicon.x - self.width, transposeicon.y + .5*transposeicon.height - .5*self.height
                    orientation: 'vertical'
                    opacity: 0
                    TransposeButton:
                        text: '+6'
                        on_press: root.do_transpose(6)
                    TransposeButton:
                        text: '+5'
                        on_press: root.do_transpose(5)
                    TransposeButton:
                        text: '+4'
                        on_press: root.do_transpose(4)
                    TransposeButton:
                        text: '+3'
                        on_press: root.do_transpose(3)
                    TransposeButton:
                        text: '+2'
                        on_press: root.do_transpose(2)
                    TransposeButton:
                        text: '+1'
                        on_press: root.do_transpose(1)
                    TransposeButton:
                        text: '0'
                        on_press: root.do_transpose(0)
                    TransposeButton:
                        text: '-1'
                        on_press: root.do_transpose(-1)
                    TransposeButton:
                        text: '-2'
                        on_press: root.do_transpose(-2)
                    TransposeButton:
                        text: '-3'
                        on_press: root.do_transpose(-3)
                    TransposeButton:
                        text: '-4'
                        on_press: root.do_transpose(-4)
                    TransposeButton:
                        text: '-5'
                        on_press: root.do_transpose(-5)
                    TransposeButton:
                        text: '-6'
                        on_press: root.do_transpose(-6)
        AnchorLayout:
            anchor_x: 'right'
            padding: dp(8)
            size_hint_y: None
            height: buttons.height + dp(16)
            BoxLayout:
                id: buttons
                orientation: 'horizontal'
                size_hint: None, None
                width: self.minimum_width
                height: self.minimum_height
                spacing: dp(8)
                IconTextButton:
                    text: "SAVE AS"
                    icon: "at"
                    background_palette: 'Primary'
                    theme_text_color: 'Custom'
                    text_color: self.specific_text_color
                    on_release: root.do_saveas()
                IconTextButton:
                    text: "SAVE"
                    disabled: True if not root.filepath.text else False
                    icon: "content-save"
                    md_bg_color: app.theme_cls.accent_color
                    background_palette: 'Accent'
                    theme_text_color: 'Custom'
                    text_color: self.specific_text_color
                    on_release: root.do_save()
""")

class TouchLabel(MDIconButton):
    def _finish_init(self, dt=None):
        super(TouchLabel, self)._finish_init(dt)
        self.content.font_size = dp(32)

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


class EditSongScreen(Screen):
    song = ObjectProperty(None)
    dialog = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(EditSongScreen, self).__init__(**kwargs)
        Clock.schedule_once(self._finish_init)

    def _finish_init(self, dt):
        app = App.get_running_app()
        signal('ownItem').connect(self._update_song)

    def _update_song(self, sender=None):
        app = App.get_running_app()
        if isinstance(app.client.ownItem, SPSong):
            self.song = app.client.ownItem
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

    def UI_to_song(self):
        songObject = SPSong()
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

    def do_transpose(self, i):
        so = SPSong()
        so.lyrics = self.lyrics.text
        so.key = self.key.text
        so.transpose(i)
        self.lyrics.text = so.lyrics
        self.key.text = so.key

    def dismiss_all(self):
        if self.dialog:
            self.dialog.dismiss()

    def do_saveas(self):
        self.dismiss_all()
        songObject = self.UI_to_song()
        title = "Save song as a different file?"
        message = ("Save the song '{0}' as".
                   format(songObject.title))
        if songObject.filepath:
            suggestpath = songObject.filepath
        else:
            suggestpath = songObject.title
        content = SaveAsDialogContent(message=message,
                                      suggestpath=suggestpath)
        self.dialog = MDDialog(title=title,
                               content=content,
                               size_hint=(.8, .6),
                               auto_dismiss=False)
        self.dialog.add_icontext_button("save", "content-save",
                action=lambda x: self._do_save(songObject,
                    self.dialog.content.filepath.text))
        self.dialog.add_icontext_button("cancel", "close-circle",
                action=lambda x: self.dialog.dismiss())
        self.dialog.open()

    def do_save(self):
        self.dismiss_all()
        songObject = self.UI_to_song()
        if songObject != self.song:
            if songObject.filepath == '':
                return self.do_saveas()
            title = "Save song?"
            message = ("Save the song '{0}' to file named '{1}'?".
                       format(songObject.title, songObject.filepath))
            content = MDLabel(font_style='Body1',
                              theme_text_color='Secondary',
                              text=message,
                              size_hint_y=None,
                              valign='top')
            content.bind(texture_size=content.setter('size'))
            self.dialog = MDDialog(title=title,
                                   content=content,
                                   size_hint=(.8, .6),
                                   auto_dismiss=False)
            self.dialog.add_icontext_button("save", "content-save",
                    action=lambda x: self._do_save(songObject, songObject.filepath))
            self.dialog.add_icontext_button("cancel", "close-circle",
                    action=lambda x: self.dialog.dismiss())
        else:
            title = "Nothing to save"
            message = ("The song '{0}' has not changed.".
                       format(songObject.title))
            content = MDLabel(font_style='Body1',
                              theme_text_color='Secondary',
                              text=message,
                              size_hint_y=None,
                              valign='top')
            content.bind(texture_size=content.setter('size'))
            self.dialog = MDDialog(title=title,
                                   content=content,
                                   size_hint=(.8, .4),
                                   auto_dismiss=True)
        self.dialog.open()

    def _do_save(self, songObject, relpath):
        self.dismiss_all()
        songObject.filepath = relpath
        app = App.get_running_app()
        app.client.save_item(item=songObject, relpath=relpath)
        app.client.change_own_item('song', relpath)

    def safe_to_exit(self, target_screen):
        self.dismiss_all()
        songObject = self.UI_to_song()
        if songObject != self.song:
            title = "Song not yet saved!"
            message = ("Save the song '{0}' to file named '{1}'?".
                       format(songObject.title, songObject.filepath))
            content = MDLabel(font_style='Body1',
                              theme_text_color='Secondary',
                              text=message,
                              size_hint_y=None,
                              valign='top')
            content.bind(texture_size=content.setter('size'))
            self.dialog = MDDialog(title=title,
                                   content=content,
                                   size_hint=(.8, .6),
                                   auto_dismiss=True)
            self.dialog.add_icontext_button("save", "content-save",
                    action=lambda x: self._do_save(songObject, songObject.filepath))
            self.dialog.add_icontext_button("discard", "delete-variant",
                    action=lambda x: self._proceed_to_target(target_screen))
            self.dialog.open()
            return False
        else:
            return True

    def _proceed_to_target(self, target_screen):
        self.dismiss_all()
        app = App.get_running_app()
        app.base.to_screen(target_screen, skip_save_check=True)
        self.song = app.client.ownItem
        self.song_to_UI()
