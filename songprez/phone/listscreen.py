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
from kivy.properties import ObjectProperty
from twisted.internet import defer
from blinker import signal
from functools import partial
from kivymd.dialog import MDDialog
from kivymd.label import MDLabel
from kivymd.menu import MDDropdownMenu
from kivymd.button import MDFloatingActionButton
from .fontutil import iconfont
from .recyclelist import SPRecycleView, ListItem
from .recycle2list import MDRecycleView
from kivy.metrics import dp, sp
from .buttonrow import Buttons
from .icontextbutton import IconTextMenuItem
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
    sendMessage: app.sendMessage
    BoxLayout:
        orientation: 'vertical'
        MDRecycleView:
            id: rv
            primary_action: root.primary_action
            long_press_action: root.long_press_action
    MDFloatingActionButton:
        icon: 'plus'
        size: dp(40), dp(40)
        pos: root.x + root.width - dp(56), root.y + dp(16)
        on_release: root.do_new()
""")


class ListScreen(Screen):
    dialog = ObjectProperty(None)
    menu = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(ListScreen, self).__init__(**kwargs)
        Clock.schedule_once(self._finish_init)

    def _finish_init(self, dt):
        pass

    def dismiss_all(self):
        if self.dialog:
            self.dialog.dismiss()
        if self.menu:
            self.menu.dismiss()


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
        self.rv.data = [{'viewclass': 'MDLabel',
                         'text': 'Please wait, still loading sets!',
                         'font_style': 'Headline',
                         'theme_text_color': 'Primary',
                         'secondary_theme_text_color': 'Primary',
                         'height': sp(60)}]
        signal('setList').connect(self.update_sets)
        Clock.schedule_once(self._get_details, 1)

    @defer.inlineCallbacks
    def _get_details(self, dt=None):
        data = self.rv.data
        for e in data:
            if not e.has_key('subtitle_text') and e.has_key('relpath'):
                app = App.get_running_app()
                item = yield app.client.get_set(e['relpath'])
                if item == None:
                    e['subtitle_text'] = 'Error loading'
                else:
                    text = [i['name'] for i in item.list_songs()]
                    subtitle = []
                    for i in text:
                        subtitle.append(' '.join(i.split(' ', 2)[:2]))
                    subtitle = " | ".join(subtitle)
                    e['subtitle_text'] = subtitle
                    e['viewclass'] = 'CountItem'
                    e['num_items'] = len(text)
        Clock.schedule_once(self._get_details, 1)

    def update_sets(self, sender=None):
        app = App.get_running_app()
        setList = app.client.setList
        data = []
        for i, item in enumerate(setList):
            h = app.ui_fs_main*1.5 + dp(10)
            data.append({'title_text': item['name'],
                         'viewclass': 'CountItem',
                         'relpath': item['relpath']})
        self.rv.data = data

    def do_edit(self, relpath):
        self.dismiss_all()
        app = App.get_running_app()
        app.client.change_own_set(relpath)
        app.base.to_screen('editset')

    def do_copy(self, relpath):
        self.dismiss_all()

    @defer.inlineCallbacks
    def do_delete(self, relpath):
        self.dismiss_all()
        app = App.get_running_app()
        setObject = yield app.client.get_set(relpath)
        if setObject != None:
            title = "Delete permanently?"
            message = ("You are about to delete '{0}'. This cannot be undone"
                       .format(setObject.filepath))
            content = MDLabel(font_style='Body1',
                              theme_text_color='Secondary',
                              text=message,
                              valign='top')
            content.bind(size=content.setter('text_size'))
            self.dialog = MDDialog(title=title,
                                   content=content,
                                   size_hint=(.8, .6),
                                   auto_dismiss=False)
            self.dialog.add_icontext_button("delete", "delete",
                    action=lambda x: self._do_delete_set(relpath))
            self.dialog.add_icontext_button("cancel", "close-circle",
                    action=lambda x: self.dialog.dismiss())
            self.dialog.open()
        else:
            message = ("Error reading from '{0}'."
                       .format(relpath))
            popup = ModalPopup(message=message,
                               righttext=iconfont('ok') + ' OK')
            popup.open()

    def _do_delete_set(self, filepath):
        self.dismiss_all()
        app = App.get_running_app()
        app.client.delete_set(relpath=filepath)

    def do_new(self):
        self.dismiss_all()
        app = App.get_running_app()
        app.client.change_own_set('')
        app.base.to_screen('editset')

    def do_sort(self):
        self.dismiss_all()

    @defer.inlineCallbacks
    def do_show(self, relpath):
        self.dismiss_all()
        app = App.get_running_app()
        if relpath:
            setObject = yield app.client.get_set(relpath)
            if setObject != None:
                app.client.change_current_set(setObject)
                app.base.to_screen('present')
            else:
                self.error_dialog(relpath)

    @defer.inlineCallbacks
    def primary_action(self, item_data):
        self.dismiss_all()
        app = App.get_running_app()
        relpath = item_data.get('relpath')
        if relpath:
            setObject = yield app.client.get_set(relpath)
            if setObject != None:
                song_list = setObject.list_songs()
                song_names = u"\n".join([s['name'] for s in song_list])
                content = MDLabel(font_style='Body1',
                                  theme_text_color='Secondary',
                                  text=song_names,
                                  valign='top')
                content.bind(size=content.setter('text_size'))
                self.dialog = MDDialog(title=setObject.name,
                                       content=content,
                                       size_hint=(.8, .6),
                                       auto_dismiss=True)
                self.dialog.add_icontext_button("edit", "pencil",
                        action=lambda x: self.do_edit(relpath))
                self.dialog.add_icontext_button("show", "format-indent-increase",
                        action=lambda x: self.do_show(relpath))
                self.dialog.open()
            else:
                self.error_dialog(relpath)

    def long_press_action(self, item_data, caller):
        self.dismiss_all()
        app = App.get_running_app()
        relpath = item_data.get('relpath')
        if relpath:
            self.menu = MDDropdownMenu(items=[{'viewclass': 'IconTextMenuItem',
                                               'icon': 'delete',
                                               'text': 'Delete Set',
                                               'on_release': lambda: self.do_delete(relpath)},
                                              {'viewclass': 'IconTextMenuItem',
                                               'icon': 'content-copy',
                                               'text': 'Copy Set',
                                               'on_release': lambda: self.do_copy(relpath)},],
                                       width_mult=3
                                      )
            self.menu.open(caller)

    def error_dialog(self, relpath):
        self.dismiss_all()
        content = MDLabel(font_style='Body1',
                          theme_text_color='Secondary',
                          text=u"Set at '{}' not found".format(relpath),
                          valign='top')
        content.bind(size=content.setter('text_size'))
        self.dialog = MDDialog(title=u"Problem loading set",
                               content=content,
                               size_hint=(.8, .4),
                               auto_dismiss=True)
        self.dialog.add_action_button("OK",
                action=lambda x: self.dialog.dismiss())
        self.dialog.open()
