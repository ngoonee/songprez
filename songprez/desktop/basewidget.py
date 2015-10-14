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
        Button:
            text: "Nice intro logo?"
    Screen:
        name: 'EditScreen'
        EditScreen:
            id: editscreen
""")


class BaseWidget(ScreenManager):
    inhibit = BooleanProperty(False)

    def __init__(self, **kwargs):
        super(BaseWidget, self).__init__(**kwargs)
        self._keyboard = Window.request_keyboard(None, self, 'text')
        self._keyboard.bind(on_key_down=self._on_keyboard_down)

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        print(keycode, text, modifiers)
        if self.inhibit:
            return True
        # Handle shortcut keys
        if modifiers == ['alt']:
            if keycode[1] == 's':
                self.contentlist.searchheader.trigger_action()
            elif keycode[1] == 'e':
                self.contentlist.setheader.trigger_action()
            elif keycode[1] == 'o':
                self.contentlist.songheader.trigger_action()
            elif keycode[1] == 'a':
                self.songedit.addtoset.trigger_action()
            elif keycode[1] == 'r':
                self.songedit.removefromset.trigger_action()
            elif keycode[1] == 't':
                self.songedit.transposespinner.trigger_action()
            elif keycode[1] == 'g':
                app = App.get_running_app()
                app.open_settings()
        if keycode[1] == 'escape':
            return True
        return False
