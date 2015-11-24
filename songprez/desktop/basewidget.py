#!/usr/bin/env python
import kivy
# kivy.require('1.9.1')
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.app import App
from kivy.properties import BooleanProperty
from kivy.uix.screenmanager import ScreenManager
from .editscreen import EditScreen

Builder.load_string("""
#:import FallOutTransition kivy.uix.screenmanager.FallOutTransition
#:import NoTransition kivy.uix.screenmanager.NoTransition
#:import SwapTransition kivy.uix.screenmanager.SwapTransition
<Widget>:
    # Use same font throughout. Needed because SlideElement is a BoxLayout and
    # needs to have a font_name.
    font_name: 'songprez/fonts/NotoSansCJK-Regular.ttc'
<Label>:
    # If we use Widget instead even layouts get a font_size which wrecks
    # SlideElement
    font_size: 15
<TextInput>: # Inherits from Widget, so doesn't get the above font_size
    font_size: 15
<BaseWidget>:
    songedit: editscreen.songedit
    contentlist: editscreen.contentlist
    currentset: editscreen.currentset
    colwidth: self.width//13
    colspace: self.width//140
    rowheight: self.colwidth//3
    rowheight: self.songedit.title.height
    rowspace: self.colspace//2
    #transition: NoTransition()
    #transition: FallOutTransition()
    transition: SwapTransition()
    Screen:
        name: 'LoadScreen'
        Label:
            font_size: '120sp'
            text_size: self.parent.size
            halign: 'center'
            valign: 'middle'
            text: "Please wait for loading..."
    Screen:
        name: 'EditScreen'
        EditScreen:
            id: editscreen
""")


class BaseWidget(ScreenManager):
    def __init__(self, **kwargs):
        super(BaseWidget, self).__init__(**kwargs)
        self._keyboard = Window.request_keyboard(None, self, 'text')
        self._keyboard.bind(on_key_down=self._on_keyboard_down)

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        if keycode[1] == 'escape':
            return True
        return False

    def on_connection(self, connection):
        print('connected successfully')
        app = App.get_running_app()
        app.sendMessage = connection.sendMessage

    def _running(self):
        app = App.get_running_app()
        app._control_loaded()

    def _song_list(self, listofsong):
        self.contentlist._song_list(listofsong)

    def _set_list(self, listofset):
        self.contentlist._set_list(listofset)

    def _search_list(self, listofsearch):
        self.contentlist._search_list(listofsearch)

    def _edit_item(self, itemtype, item):
        if itemtype == 'song':
            self.songedit._edit_song(item)
        self.currentset._edit_item(itemtype, item)

    def _edit_set(self, item):
        self.currentset._edit_set(item)
