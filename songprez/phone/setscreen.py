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
from .iconfont import iconfont
from kivy.metrics import dp

Builder.load_string("""
<SetScreen>:
    listview: listview
    RecycleView:
        id: listview
        key_viewclass: 'viewclass'
        key_size: 'height'
""")

class SetScreen(Screen):
    def __init__(self, **kwargs):
        super(SetScreen, self).__init__(**kwargs)
        Clock.schedule_once(self._finish_init)

    def _finish_init(self, dt):
        app = App.get_running_app()
        self.listview.data = [{'viewclass': 'Label',
                               'text': 'Please wait, still loading sets!',
                               'font_size': app.ui_fs_main,
                               'height': 200}]

    def set_list(self, listofset):
        data = []
        app = App.get_running_app()
        for i, s in enumerate(listofset):
            title = s.name
            text = [item['name'] for item in s.list_songs()]
            iconsize = str(int(app.ui_fs_detail*1.5))
            if len(text) > 9:
                subtitle = [iconfont('9+', iconsize)]
            else:
                subtitle = [iconfont(str(len(text)), iconsize)]
            for item in text:
                subtitle.append(' '.join(item.split(' ', 2)[:2]))
            subtitle = " | ".join(subtitle)
            if len(text) > 7:
                summary = text[:7]
                summary.append('...')
            else:
                summary = text
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
