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
from kivy.garden.recycleview import RecycleView
from .recyclelist import ListItem
from kivy.metrics import dp

Builder.load_string("""
<ListScreen>:
    listview: listview
    RecycleView:
        id: listview
        key_viewclass: 'viewclass'
        key_size: 'height'
""")

class ListScreen(Screen):
    def __init__(self, **kwargs):
        super(ListScreen, self).__init__(**kwargs)
        Clock.schedule_once(self._finish_init)

    def _finish_init(self, dt):
        pass

    def item_list(self, listofitem):
        data = []
        app = App.get_running_app()
        for i, item in enumerate(listofitem):
            title, subtitle, summary = self.get_vals(item)
            if subtitle:
                viewclass = 'ListItem'
                h = app.ui_fs_main*1.5 + app.ui_fs_detail*1.5 + dp(10)
            else:
                viewclass = 'ListItem'
                h = app.ui_fs_main*1.5 + dp(10)
            data.append({'index': i, 'titletext': title,
                         'subtitletext': subtitle, 'summarytext': summary,
                         'expand_angle': 0, 'button_opacity': 0,
                         'viewclass': viewclass, 'height': h,
                         'rv': self.listview})
        self.listview.data = data

    def get_vals(self, item):
        return u'', u'', u''


class SongScreen(ListScreen):
    def _finish_init(self, dt):
        app = App.get_running_app()
        self.listview.data = [{'viewclass': 'Label',
                               'text': 'Please wait, still loading songs!',
                               'font_size': app.ui_fs_main,
                               'height': 200}]

    def get_vals(self, item):
        title = item.title
        subtitle = [] 
        for t in (item.author, item.aka, item.key_line):
            if t:
                subtitle.append(t)
        subtitle = " | ".join(subtitle)
        text = item.words.split('\n')
        text = [t for t in text if t != '' and not (t[0] == '[' and t[-1] == ']')]
        summary = text[0:4]
        return title, subtitle, summary


class SetScreen(ListScreen):
    def _finish_init(self, dt):
        app = App.get_running_app()
        self.listview.data = [{'viewclass': 'Label',
                               'text': 'Please wait, still loading sets!',
                               'font_size': app.ui_fs_main,
                               'height': 200}]

    def get_vals(self, item):
        app = App.get_running_app()
        title = item.name
        text = [i['name'] for i in item.list_songs()]
        iconsize = str(int(app.ui_fs_detail*1.5))
        if len(text) > 9:
            subtitle = [iconfont('9+', iconsize)]
        else:
            subtitle = [iconfont(str(len(text)), iconsize)]
        for i in text[:4]:
            subtitle.append(' '.join(i.split(' ', 2)[:2]))
        if len(text) > 4:
            summary = text[:4]
            summary.append('...')
            subtitle.append('...')
        else:
            summary = text
        subtitle = " | ".join(subtitle)
        return title, subtitle, summary
