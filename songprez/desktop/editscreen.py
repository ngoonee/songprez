#!/usr/bin/env python
import kivy
# kivy.require('1.9.0')
from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from blinker import signal
from .button import FocusButton, NormalSizeFocusButton
from .itemlist import ItemList
from .setlist import SetList
from .contentlist import ContentList
from .songedit import SongEdit

Builder.load_string("""
#:import signal blinker.signal
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
        Clock.schedule_once(self._finish_init)

    def _finish_init(self, dt):
        pass
