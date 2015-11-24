#!/usr/bin/env python
import kivy
# kivy.require('1.9.0')
from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from .button import FocusButton, NormalSizeFocusButton
from .itemlist import ItemList
from .setlist import SetList
from .contentlist import ContentList
from .songedit import SongEdit

Builder.load_string("""
<EditScreen>:
    songedit: songedit
    contentlist: contentlist
    currentset: currentset
    BoxLayout:
        orientation: 'horizontal'
        padding: (self.width - app.colwidth*12 - app.colspace*11)//2
        spacing: app.colspace
        BoxLayout:
            orientation: 'vertical'
            padding: 0
            spacing: app.rowspace*3
            size_hint_x: None
            width: app.colwidth*3 + app.colspace*2
            ContentList:
                id: contentlist
                size_hint_y: 4
            SetList:
                id: currentset
                size_hint_y: 3
        SongEdit:
            id: songedit
        BoxLayout:
            orientation: 'vertical'
            padding: 0
            spacing: app.rowspace
            size_hint_x: None
            width: app.colwidth*2 + app.colspace*1
            Button:
            BoxLayout:
                orientation: 'horizontal'
                size_hint_y: None
                height: app.rowheight
                spacing: app.colspace
                BoxLayout:
                    size_hint_x: None
                    width: app.colwidth
                NormalSizeFocusButton:
                    markup: True
                    text: 'Settin[color=FFFF00][b]g[/b][/color]s'
                    on_press: app.open_settings()
            FocusButton:
                size_hint_y: None
                height: app.rowheight*2 + app.rowspace
                text: 'Present'
""")


class EditScreen(Screen):
    def __init__(self, **kwargs):
        super(EditScreen, self).__init__(**kwargs)
        self._app = App.get_running_app()
        self._keyboard = Window.request_keyboard(None, self, 'text')
        self.bind(parent=self._parent)
        Clock.schedule_once(self._finish_init)

    def _finish_init(self, dt):
        pass

    def _parent(self, instance, value):
        '''
        Activated whenever this Screen obtains or loses a parent, use this to
        only bind keyboard when this is the active screen.
        '''
        if value:  # Has a parent - is the active screen
            self._keyboard.bind(on_key_down=self._on_keyboard_down)
        else:
            self._keyboard.unbind(on_key_down=self._on_keyboard_down)

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        if not self._app.inhibit:
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
                elif keycode[1] == 'up':
                    self.currentset._up_song()
                elif keycode[1] == 'down':
                    self.currentset._down_song()
                else:
                    return False
            return True
