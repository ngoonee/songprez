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
from twisted.internet import defer
from blinker import signal
from functools import partial
from .fontutil import iconfont
from .recyclelist import SPRecycleView, ListItem
from kivy.metrics import dp, sp
from .buttonrow import Buttons
from .modalpopup import ModalPopup
from ..control.spsong import SPSong
from ..control.spset import SPSet
from ..network.messages import Search

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
    def __init__(self, **kwargs):
        super(ListScreen, self).__init__(**kwargs)
        Clock.schedule_once(self._finish_init)

    def _finish_init(self, dt):
        pass


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

    @defer.inlineCallbacks
    def do_search(self, searchTerm):
        app = App.get_running_app()
        searchList = yield app.client.search(searchTerm)
        data = []
        for i, item in enumerate(searchList):
            viewclass = 'ListItem'
            h = app.ui_fs_main*1.5 + dp(10)
            data.append({'titletext': item['name'],
                         'expand_angle': 0, 'button_opacity': 0,
                         'viewclass': viewclass, 'height': h,
                         'rv': self.rv, 'relpath': item['relpath']})
        self.rv.data = data

    def bt_edit(self, relpath):
        app = App.get_running_app()
        app.client.change_own_item('song', relpath)
        app.base.to_screen('editsong')

    def bt_delete(self, relpath):
        app = App.get_running_app()
        songObject = yield app.client.get_item('song', relpath)
        if songObject != None:
            message = ("Are you sure you want to delete '{0}'?".
                       format(songObject.filepath))
            popup = ModalPopup(message=message,
                               lefttext=iconfont('delete') + ' Delete',
                               leftcolor=(0.8, 0, 0, 1),
                               righttext=iconfont('cancel') + ' Cancel')
            popup.bind(on_left_action=partial(self._do_delete_song,
                                              'song',
                                              songObject.filepath))
            popup.open()
        else:
            message = ("Error reading from '{0}'."
                       .format(relpath))
            popup = ModalPopup(message=message,
                               righttext=iconfont('ok') + ' OK')
            popup.open()

    def _do_delete_song(self, itemtype, filepath, instance):
        self.sendMessage(DeleteEditItem, itemtype=itemtype, relpath=filepath)

    def bt_new(self):
        app = App.get_running_app()
        app.client.change_own_item('song', '')
        app.base.to_screen('editsong')

    def bt_songs(self):
        app = App.get_running_app()
        app.base.to_screen('songs')

    def bt_add(self):
        app = App.get_running_app()
        relpath = self.rv.selection
        if not relpath:  # No valid selection
            return
        if app.base.presenting:  # Most recently presenting a song
            presentscreen = app.base.sm.get_screen('present')
            presentscreen.add_item('song', relpath)
        else:  # Most recently editing a set
            if app.client.ownSet:
                app.client.add_item_to_own_set('song', relpath)


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
        signal('songList').connect(self.update_songs)
        Clock.schedule_once(self._get_details, 1)

    @defer.inlineCallbacks
    def _get_details(self, dt=None):
        data = self.rv.data
        for e in data:
            if not e.has_key('subtitletext') and e.has_key('relpath'):
                app = App.get_running_app()
                item = yield app.client.get_item('song', e['relpath'])
                if item == None:
                    e['subtitletext'] = 'Error loading'
                else:
                    subtitle = []
                    for t in (item.author, item.aka, item.key_line):
                        if t:
                            subtitle.append(t)
                    subtitle = " | ".join(subtitle)
                    text = item.words.split('\n')
                    text = [t for t in text 
                            if t != '' and not (t[0] == '[' and t[-1] == ']')]
                    summary = text[0:4]
                    if subtitle:
                        viewclass = 'ListItem'
                        h = app.ui_fs_main*1.5 + app.ui_fs_detail*1.5 + dp(10)
                    else:
                        viewclass = 'ListItem'
                        h = app.ui_fs_main*1.5 + dp(10)
                    e['subtitletext'] = subtitle
                    e['summarytext'] = summary
                    e['viewclass'] = viewclass
                    e['height'] = h
        Clock.schedule_once(self._get_details, 1)


    def update_songs(self, sender=None):
        app = App.get_running_app()
        songList = app.client.songList
        data = []
        for i, item in enumerate(songList):
            viewclass = 'ListItem'
            h = app.ui_fs_main*1.5 + dp(10)
            data.append({'titletext': item['name'],
                         'expand_angle': 0, 'button_opacity': 0,
                         'viewclass': viewclass, 'height': h,
                         'rv': self.rv, 'relpath': item['relpath'],
                         'mtime': item['mtime']})
        self.rv.data = data

    def bt_edit(self, relpath):
        app = App.get_running_app()
        app.client.change_own_item('song', relpath)
        app.base.to_screen('editsong')

    @defer.inlineCallbacks
    def bt_delete(self, relpath):
        app = App.get_running_app()
        songObject = yield app.client.get_item('song', relpath)
        if songObject != None:
            message = ("Are you sure you want to delete '{0}'?".
                       format(songObject.filepath))
            popup = ModalPopup(message=message,
                               lefttext=iconfont('delete') + ' Delete',
                               leftcolor=(0.8, 0, 0, 1),
                               righttext=iconfont('cancel') + ' Cancel')
            popup.bind(on_left_action=partial(self._do_delete_song,
                                              'song',
                                              songObject.filepath))
            popup.open()
        else:
            message = ("Error reading from '{0}'."
                       .format(relpath))
            popup = ModalPopup(message=message,
                               righttext=iconfont('ok') + ' OK')
            popup.open()

    def _do_delete_song(self, itemtype, filepath, instance):
        app = App.get_running_app()
        app.client.delete_item(itemtype=itemtype, relpath=filepath)

    def bt_new(self):
        app = App.get_running_app()
        app.client.change_own_item('song', '')
        app.base.to_screen('editsong')

    def bt_search(self):
        app = App.get_running_app()
        app.base.to_screen('search')

    def bt_add(self):
        app = App.get_running_app()
        relpath = self.rv.selection
        if not relpath:  # No valid selection
            return
        if app.base.presenting:  # Most recently presenting a song
            presentscreen = app.base.sm.get_screen('present')
            presentscreen.add_item('song', relpath)
        else:  # Most recently editing a set
            if app.client.ownSet:
                app.client.add_item_to_own_set('song', relpath)


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
        signal('setList').connect(self.update_sets)
        Clock.schedule_once(self._get_details, 1)

    @defer.inlineCallbacks
    def _get_details(self, dt=None):
        data = self.rv.data
        for e in data:
            if not e.has_key('subtitletext') and e.has_key('relpath'):
                app = App.get_running_app()
                item = yield app.client.get_set(e['relpath'])
                if item == None:
                    e['subtitletext'] = 'Error loading'
                else:
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
                    if subtitle:
                        viewclass = 'ListItem'
                        h = app.ui_fs_main*1.5 + app.ui_fs_detail*1.5 + dp(10)
                    else:
                        viewclass = 'ListItem'
                        h = app.ui_fs_main*1.5 + dp(10)
                    e['subtitletext'] = subtitle
                    e['summarytext'] = summary
                    e['viewclass'] = viewclass
                    e['height'] = h
        Clock.schedule_once(self._get_details, 1)

    def update_sets(self, sender=None):
        app = App.get_running_app()
        setList = app.client.setList
        data = []
        for i, item in enumerate(setList):
            viewclass = 'ListItem'
            h = app.ui_fs_main*1.5 + dp(10)
            data.append({'titletext': item['name'],
                         'expand_angle': 0, 'button_opacity': 0,
                         'viewclass': viewclass, 'height': h,
                         'rv': self.rv, 'relpath': item['relpath']})
        self.rv.data = data

    def bt_edit(self, relpath):
        app = App.get_running_app()
        app.client.change_own_set(relpath)
        app.base.to_screen('editset')

    @defer.inlineCallbacks
    def bt_delete(self, relpath):
        app = App.get_running_app()
        setObject = yield app.client.get_set(relpath)
        if setObject != None:
            message = ("Are you sure you want to delete '{0}'?".
                       format(setObject.filepath))
            popup = ModalPopup(message=message,
                               lefttext=iconfont('delete') + ' Delete',
                               leftcolor=(0.8, 0, 0, 1),
                               righttext=iconfont('cancel') + ' Cancel')
            popup.bind(on_left_action=partial(self._do_delete_set, setObject.filepath))
            popup.open()
        else:
            message = ("Error reading from '{0}'."
                       .format(relpath))
            popup = ModalPopup(message=message,
                               righttext=iconfont('ok') + ' OK')
            popup.open()

    def _do_delete_set(self, filepath, instance):
        app = App.get_running_app()
        app.client.delete_set(relpath=filepath)

    def bt_new(self):
        app = App.get_running_app()
        app.client.change_own_set('')
        app.base.to_screen('editset')

    def bt_sort(self):
        pass

    @defer.inlineCallbacks
    def bt_show(self):
        app = App.get_running_app()
        relpath = self.rv.selection
        if relpath:
            setObject = yield app.client.get_set(relpath)
            if setObject != None:
                app.client.change_current_set(setObject)
                app.base.to_screen('present')
            else:
                message = ("Error reading from '{0}'."
                           .format(relpath))
                popup = ModalPopup(message=message,
                                   righttext=iconfont('ok') + ' OK')
                popup.open()
