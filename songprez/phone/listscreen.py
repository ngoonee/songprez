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
from kivy.metrics import dp, sp
from ..network.messages import Search

Builder.load_string("""
<RecycleView>:
    canvas.before:
        Color:
            rgba: (.125, .125, .125, 1)
        RoundedRectangle:
            size: self.size
            pos: self.pos
            radius: dp(10),
    key_viewclass: 'viewclass'
    key_size: 'height'

<Buttons@BoxLayout>:
    button1: button1
    button2: button2
    button3: button3
    size_hint_y: None
    height: app.buttonsize + dp(10)
    spacing: '5dp'
    Button:
        id: button1
        markup: True
        font_size: app.ui_fs_button
        on_press: root.parent.parent.button1()
    Button:
        id: button2
        markup: True
        font_size: app.ui_fs_button
        on_press: root.parent.parent.button2()
    Button:
        id: button3
        markup: True
        font_size: app.ui_fs_button
        on_press: root.parent.parent.button3()

<SearchScreen>:
    listview: listview
    buttons: buttons
    BoxLayout:
        orientation: 'vertical'
        padding: '5dp'
        spacing: '5dp'
        TextInput:
            size_hint_y: None
            height: self.minimum_height
            multiline: False
            on_text_validate: root.do_search(self.text)
        RecycleView:
            id: listview
        Buttons:
            id: buttons

<SongScreen>:
    listview: listview
    buttons: buttons
    BoxLayout:
        orientation: 'vertical'
        padding: '5dp'
        spacing: '5dp'
        RecycleView:
            id: listview
        Buttons:
            id: buttons

<SetScreen>:
    listview: listview
    buttons: buttons
    BoxLayout:
        orientation: 'vertical'
        padding: '5dp'
        spacing: '5dp'
        RecycleView:
            id: listview
        Buttons:
            id: buttons
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

    def button1(self):
        pass

    def button2(self):
        pass

    def button3(self):
        pass


class SearchScreen(ListScreen):
    def _finish_init(self, dt):
        app = App.get_running_app()
        self.listview.data = [{'viewclass': 'Label',
                               'text': 'No search results yet',
                               'font_size': app.ui_fs_main,
                               'height': sp(50)}]
        self.buttons.button1.text = iconfont('new', app.ui_fs_button) + ' New'
        self.buttons.button2.text = iconfont('songs', app.ui_fs_button) + ' Songs'
        self.buttons.button3.text = iconfont('listadd', app.ui_fs_button) + ' Add'

    def get_vals(self, item):
        title = item.title
        subtitle = [] 
        for t in (item.author, item.aka, item.key_line):
            if t:
                subtitle.append(t)
        subtitle = " | ".join(subtitle)
        text = item.words.split('\n')
        text = [t for t in text 
                if t != '' and not (t[0] == '[' and t[-1] == ']')]
        summary = text[0:4]
        return title, subtitle, summary

    def do_search(self, searchTerm):
        print('searching for ', searchTerm)
        app = App.get_running_app()
        app.sendMessage(Search, term=searchTerm)

    def button2(self):
        app = App.get_running_app()
        app.base.sm.current = 'songs'


class SongScreen(ListScreen):
    def _finish_init(self, dt):
        app = App.get_running_app()
        self.listview.data = [{'viewclass': 'Label',
                               'text': 'Please wait, still loading songs!',
                               'font_size': app.ui_fs_main,
                               'height': sp(50)}]
        self.buttons.button1.text = iconfont('new', app.ui_fs_button) + ' New'
        self.buttons.button2.text = iconfont('search', app.ui_fs_button) + ' Search'
        self.buttons.button3.text = iconfont('listadd', app.ui_fs_button) + ' Add'

    def get_vals(self, item):
        title = item.title
        subtitle = [] 
        for t in (item.author, item.aka, item.key_line):
            if t:
                subtitle.append(t)
        subtitle = " | ".join(subtitle)
        text = item.words.split('\n')
        text = [t for t in text 
                if t != '' and not (t[0] == '[' and t[-1] == ']')]
        summary = text[0:4]
        return title, subtitle, summary

    def button2(self):
        app = App.get_running_app()
        app.base.sm.current = 'search'


class SetScreen(ListScreen):
    def _finish_init(self, dt):
        app = App.get_running_app()
        self.listview.data = [{'viewclass': 'Label',
                               'text': 'Please wait, still loading sets!',
                               'font_size': app.ui_fs_main,
                               'height': sp(50)}]
        self.buttons.button1.text = iconfont('new', app.ui_fs_button) + ' New'
        self.buttons.button2.text = iconfont('sort', app.ui_fs_button) + ' Sort'
        self.buttons.button3.text = iconfont('showset', app.ui_fs_button) + ' Show'

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
