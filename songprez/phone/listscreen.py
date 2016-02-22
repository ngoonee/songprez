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
from kivy.properties import BooleanProperty, NumericProperty, ListProperty
from kivy.adapters.listadapter import ListAdapter
from .iconfont import iconfont
from .recyclelist import SPRecycleView, ListItem
from kivy.metrics import dp, sp
from ..network.messages import Search, ChangeShowSet
from .buttonrow import Buttons

Builder.load_string("""
<SearchScreen>:
    rv: rv
    buttons: buttons
    sendMessage: app.sendMessage
    BoxLayout:
        orientation: 'vertical'
        padding: '5dp'
        spacing: '5dp'
        TextInput:
            size_hint_y: None
            height: self.minimum_height
            multiline: False
            on_text_validate: root.do_search(self.text)
        SPRecycleView:
            id: rv
            edit_action: root.bt_edit
            delete_action: root.bt_delete
        Buttons:
            id: buttons
            button1_action: root.bt_new
            button2_action: root.bt_songs
            button3_action: root.bt_add

<SongScreen>:
    rv: rv
    buttons: buttons
    sendMessage: app.sendMessage
    BoxLayout:
        orientation: 'vertical'
        padding: '5dp'
        spacing: '5dp'
        SPRecycleView:
            id: rv
            edit_action: root.bt_edit
            delete_action: root.bt_delete
        Buttons:
            id: buttons
            button1_action: root.bt_new
            button2_action: root.bt_search
            button3_action: root.bt_add

<SetScreen>:
    rv: rv
    buttons: buttons
    sendMessage: app.sendMessage
    BoxLayout:
        orientation: 'vertical'
        padding: '5dp'
        spacing: '5dp'
        SPRecycleView:
            id: rv
            edit_action: root.bt_edit
            delete_action: root.bt_delete
        Buttons:
            id: buttons
            button1_action: root.bt_new
            button2_action: root.bt_sort
            button3_action: root.bt_show
""")


class ListScreen(Screen):
    itemlist = ListProperty([])

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
                         'rv': self.rv})
        self.rv.data = data
        self.itemlist = listofitem

    def get_vals(self, item):
        return u'', u'', u''


class SearchScreen(ListScreen):
    def _finish_init(self, dt):
        app = App.get_running_app()
        self.rv.data = [{'viewclass': 'Label',
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
        self.sendMessage(Search, term=searchTerm)

    def bt_edit(self, index):
        app = App.get_running_app()
        app.base.current_song = self.itemlist[index]
        app.base.to_screen('editsong')

    def bt_delete(self, index):
        pass

    def bt_new(self):
        pass

    def bt_songs(self):
        app = App.get_running_app()
        app.base.to_screen('songs')

    def bt_add(self):
        app = App.get_running_app()
        index = self.rv.selection
        app.base.add_song(self.itemlist[index])


class SongScreen(ListScreen):
    def _finish_init(self, dt):
        app = App.get_running_app()
        self.rv.data = [{'viewclass': 'Label',
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

    def bt_edit(self, index):
        app = App.get_running_app()
        app.base.current_song = self.itemlist[index]
        app.base.to_screen('editsong')

    def bt_delete(self, index):
        pass

    def bt_new(self):
        pass

    def bt_search(self):
        app = App.get_running_app()
        app.base.to_screen('search')

    def bt_add(self):
        app = App.get_running_app()
        index = self.rv.selection
        app.base.add_song(self.itemlist[index])


class SetScreen(ListScreen):
    def _finish_init(self, dt):
        app = App.get_running_app()
        self.rv.data = [{'viewclass': 'Label',
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

    def bt_edit(self, index):
        app = App.get_running_app()
        app.base.edit_set(self.itemlist[index])
        app.base.to_screen('editset')

    def bt_delete(self, index):
        pass

    def bt_new(self):
        pass

    def bt_sort(self):
        pass

    def bt_show(self):
        app = App.get_running_app()
        index = self.rv.selection
        self.sendMessage(ChangeShowSet, set=self.itemlist[index])
        app.base.to_screen('present')
