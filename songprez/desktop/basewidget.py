#!/usr/bin/env python
import kivy
# kivy.require('1.9.1')
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.app import App
from kivy.properties import BooleanProperty
from kivy.uix.screenmanager import ScreenManager
from .editscreen import EditScreen
from .showscreen import ShowScreen

Builder.load_string("""
#:import FallOutTransition kivy.uix.screenmanager.FallOutTransition
#:import NoTransition kivy.uix.screenmanager.NoTransition
#:import SwapTransition kivy.uix.screenmanager.SwapTransition
<Widget>:
    # Use same font throughout. Needed because SlideElement is a BoxLayout and
    # needs to have a font_name.
    font_name: 'songprez/fonts/NotoSansCJK-Regular.ttc'
    font_size: 15
    # Sometime between revision 700 (g048821a) and 828 (g132be35) this was made
    # to work. Before that we needed to apply font_size separately to label and
    # TextInput.
<BaseWidget>:
    editor: editscreen.editor
    songedit: editscreen.songedit
    scriptureedit: editscreen.scriptureedit
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
    EditScreen:
        name: 'EditScreen'
        id: editscreen
    ShowScreen:
        name: 'ShowScreen'
        id: showscreen
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
        self.contentlist.panel._song_list(listofsong)

    def _set_list(self, listofset):
        self.contentlist.panel._set_list(listofset)

    def _search_list(self, listofsearch):
        self.contentlist.panel._search_list(listofsearch)

    def _scripture_list(self, listofscripture):
        self.contentlist.panel._scripture_list(listofscripture)

    def _edit_item(self, itemtype, item):
        if itemtype == 'song':
            self.editor.current = 'SongEdit'
            self.songedit._edit_song(item)
        elif itemtype == 'scripture':
            self.editor.current = 'ScriptureEdit'
        self.currentset._edit_item(itemtype, item)

    def _edit_set(self, item):
        self.currentset._edit_set(item)
