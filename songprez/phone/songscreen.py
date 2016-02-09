#!/usr/bin/env python
import kivy
# kivy.require('1.9.0')
from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.properties import BooleanProperty, NumericProperty
from kivy.adapters.listadapter import ListAdapter
from .iconfont import iconfont
from .itemlist import MyListView
from .itemlist import song_args_converter
from .itemlist import CustomListItemView
from ..control.spsong import SPSong

Builder.load_string("""
<SongScreen>:
    listview: listview
    MyListView:
        id: listview
""")

class SongScreen(Screen):
    def __init__(self, **kwargs):
        super(SongScreen, self).__init__(**kwargs)
        Clock.schedule_once(self._finish_init)

    def _finish_init(self, dt):
        pass

    def song_list(self, listofsong):
        self.listview.adapter = ListAdapter(args_converter=song_args_converter,
                                            cls=CustomListItemView,
                                            data=listofsong,
                                            selection_mode='multiple')
        self.listview.adapter.bind(on_selection_change=self.test)

    def test(self, value):
        print([s.titletext for s in self.listview.adapter.selection])
