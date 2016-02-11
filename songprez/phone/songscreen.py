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
from kivy.garden.recycleview import RecycleView
from .recyclelist import ListItem, ListItemWithSummary, ListItemWithSubTitle

Builder.load_string("""
<SongScreen>:
    listview: listview
    RecycleView:
        id: listview
        key_viewclass: 'viewclass'
        key_size: 'height'
""")

class SongScreen(Screen):
    def __init__(self, **kwargs):
        super(SongScreen, self).__init__(**kwargs)
        Clock.schedule_once(self._finish_init)

    def _finish_init(self, dt):
        app = App.get_running_app()
        self.listview.data = [{'viewclass': 'Label',
                               'text': 'Please wait, still loading songs!',
                               'font_size': app.ui_fs_main,
                               'height': 200}]

    def song_list(self, listofsong):
        data = []
        for i, s in enumerate(listofsong):
            title = s.title
            subtitle = [] 
            for t in (s.author, s.aka, s.key_line):
                if t:
                    subtitle.append(t)
            subtitle = " | ".join(subtitle)
            text = s.words.split('\n')
            text = [t for t in text if t != '' and not (t[0] == '[' and t[-1] == ']')]
            summary = text[0:4]
            app = App.get_running_app()
            from kivy.metrics import dp
            if subtitle:
                viewclass = 'ListItemWithSubTitle'
                h = app.ui_fs_main*1.5 + app.ui_fs_detail*1.5 + dp(10)
            else:
                viewclass = 'ListItem'
                h = app.ui_fs_main*1.5 + dp(10)
            data.append({'index': i, 'titletext': title,
                         'subtitletext': subtitle, 'summarytext': summary,
                         'viewclass': viewclass, 'height': h, 'rv': self.listview})
        self.listview.data = data
