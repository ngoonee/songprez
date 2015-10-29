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
<Widget>: # Used instead of Label because TextInput inherits from this
    font_name: 'songprez/fonts/NotoSansCJK-Regular.ttc'
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
