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
from kivy.properties import ObjectProperty, DictProperty
from twisted.internet import defer
from blinker import signal
from functools import partial
from kivymd.dialog import MDDialog
from kivymd.label import MDLabel
from kivymd.menu import MDDropdownMenu
from kivymd.button import MDFloatingActionButton
from .fontutil import iconfont
from .recyclelist import SPRecycleView
from kivy.metrics import dp, sp
from .icontextbutton import IconTextMenuItem
from .modalpopup import ModalPopup
from ..control.spsong import SPSong
from ..control.spset import SPSet
from ..network.messages import Search

Builder.load_string("""
<SearchScreen>:
    rv: rv
    BoxLayout:
        orientation: 'vertical'
        spacing: '5dp'
        TextInput:
            size_hint_y: None
            height: self.minimum_height
            multiline: False
            on_text_validate: root.do_search(self.text)
        SPRecycleView:
            id: rv
            primary_action: root.primary_action
            long_press_action: root.long_press_action

<SongScreen>:
    rv: rv
    BoxLayout:
        orientation: 'vertical'
        SPRecycleView:
            id: rv
            primary_action: root.primary_action
            long_press_action: root.long_press_action
    MDFloatingActionButton:
        icon: 'plus'
        size: dp(40), dp(40)
        pos: root.x + root.width - dp(56), root.y + dp(16)
        on_release: root.do_new()

<SetScreen>:
    rv: rv
    BoxLayout:
        orientation: 'vertical'
        SPRecycleView:
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
    song_detail_cache = {}

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
        self.rv.data = [{'viewclass': 'MDLabel',
                         'text': 'No search results yet!',
                         'font_style': 'Headline',
                         'theme_text_color': 'Primary',
                         'secondary_theme_text_color': 'Primary',
                         'height': sp(60)}]
        Clock.schedule_once(self._get_details, 1)

    @defer.inlineCallbacks
    def _get_details(self, dt=None):
        app = App.get_running_app()
        data = self.rv.data
        i = 0
        while i < len(data):
            e = data[i]
            if not e.has_key('subtitle_text') and e.has_key('relpath'):
                item = yield app.client.get_item('song', e['relpath'])
                if i >= len(data) or data[i] != e:
                    # yield is async, and something may have changed data
                    # in the meantime. If so, time to break the loop and
                    # restart everything.
                    break
                elif item == None:
                    e['subtitle_text'] = 'Error loading'
                else:
                    subtitle = []
                    for t in (item.author, item.aka, item.key_line):
                        if t:
                            subtitle.append(t)
                    subtitle = " | ".join(subtitle)
                    e['subtitle_text'] = subtitle
                    e['s'] = (None, dp(60)) if subtitle else (None, dp(40))
                    ListScreen.song_detail_cache[e['relpath']] = e
                    self.rv.refresh_from_data(modified=slice(i, i+1, None))
                    # Specifying the refreshed part saves 33% of time used
            i += 1
        Clock.schedule_once(self._get_details, 1)

    @defer.inlineCallbacks
    def do_search(self, searchTerm):
        self.dismiss_all()
        app = App.get_running_app()
        searchList = yield app.client.search(searchTerm)
        del self.rv.data[:]
        newdata = [{'title_text': item['name'],
                    'viewclass': 'BasicItem',
                    's': (None, dp(40)),
                    'relpath': item['relpath'],
                    'mtime': item['mtime']}
                   for item in searchList]
        for d in newdata:
            if d['relpath'] in self.song_detail_cache.keys():
                val = self.song_detail_cache[d['relpath']]
                if d['mtime'] == val['mtime'] and val.has_key('subtitle_text'):
                    d['subtitle_text'] = val['subtitle_text']
                    d['s'] = val['s']
        self.rv.data.extend(newdata)

    def do_edit(self, relpath):
        self.dismiss_all()
        app = App.get_running_app()
        app.client.change_own_item('song', relpath)
        app.base.to_screen('editsong')

    def do_copy(self, relpath):
        self.dismiss_all()
        print('Song copy not yet implemented')

    @defer.inlineCallbacks
    def do_delete(self, relpath):
        self.dismiss_all()
        app = App.get_running_app()
        songObject = yield app.client.get_item('song', relpath)
        if songObject != None:
            title = "Delete permanently?"
            message = ("You are about to delete '{0}'. This cannot be undone."
                       .format(songObject.filepath))
            content = MDLabel(font_style='Body1',
                              theme_text_color='Secondary',
                              text=message,
                              size_hint_y=None,
                              valign='top')
            content.bind(texture_size=content.setter('size'))
            self.dialog = MDDialog(title=title,
                                   content=content,
                                   size_hint=(.8, .6),
                                   auto_dismiss=False)
            self.dialog.add_icontext_button("delete", "delete",
                    action=lambda x: self._do_delete_song('song', relpath))
            self.dialog.add_icontext_button("cancel", "close-circle",
                    action=lambda x: self.dialog.dismiss())
            self.dialog.open()
        else:
            self.error_dialog(relpath)

    def _do_delete_song(self, itemtype, filepath):
        self.dismiss_all()
        app = App.get_running_app()
        app.client.delete_item(itemtype=itemtype, relpath=filepath)

    def do_add(self):
        self.dismiss_all()
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

    @defer.inlineCallbacks
    def primary_action(self, item_data):
        self.dismiss_all()
        app = App.get_running_app()
        relpath = item_data.get('relpath')
        if relpath:
            songObject = yield app.client.get_item('song', relpath)
            if songObject != None:
                content = MDLabel(font_style='Body1',
                                  theme_text_color='Secondary',
                                  text=songObject.words,
                                  size_hint_y=None,
                                  valign='top')
                content.bind(texture_size=content.setter('size'))
                self.dialog = MDDialog(title=songObject.title,
                                       content=content,
                                       size_hint=(.8, .6),
                                       auto_dismiss=True)
                self.dialog.add_icontext_button("edit", "pencil",
                        action=lambda x: self.do_edit(relpath))
                self.dialog.add_icontext_button("add", "playlist-plus",
                        action=lambda x: self.do_add(relpath))
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
                                               'text': 'Delete Song',
                                               'on_release': lambda: self.do_delete(relpath)},
                                              {'viewclass': 'IconTextMenuItem',
                                               'icon': 'content-copy',
                                               'text': 'Copy Song',
                                               'on_release': lambda: self.do_copy(relpath)},],
                                       width_mult=3
                                      )
            self.menu.open(caller)

    def error_dialog(self, relpath):
        self.dismiss_all()
        content = MDLabel(font_style='Body1',
                          theme_text_color='Secondary',
                          text=u"Song at '{}' not found".format(relpath),
                          size_hint_y=None,
                          valign='top')
        content.bind(texture_size=content.setter('size'))
        self.dialog = MDDialog(title=u"Problem loading song",
                               content=content,
                               size_hint=(.8, .4),
                               auto_dismiss=True)
        self.dialog.add_action_button("OK",
                action=lambda x: self.dialog.dismiss())
        self.dialog.open()


class SongScreen(ListScreen):
    def _finish_init(self, dt):
        app = App.get_running_app()
        self.rv.data = [{'viewclass': 'MDLabel',
                         'text': 'Please wait, still loading songs!',
                         'font_style': 'Headline',
                         'theme_text_color': 'Primary',
                         'secondary_theme_text_color': 'Primary',
                         'height': sp(60)}]
        signal('songList').connect(self.update_songs)
        Clock.schedule_once(self._get_details, 1)

    @defer.inlineCallbacks
    def _get_details(self, dt=None):
        app = App.get_running_app()
        data = self.rv.data
        i = 0
        while i < len(data):
            e = data[i]
            if not e.has_key('subtitle_text') and e.has_key('relpath'):
                item = yield app.client.get_item('song', e['relpath'])
                if i >= len(data) or data[i] != e:
                    # yield is async, and something may have changed data
                    # in the meantime. If so, time to break the loop and
                    # restart everything.
                    break
                elif item == None:
                    e['subtitle_text'] = 'Error loading'
                else:
                    subtitle = []
                    for t in (item.author, item.aka, item.key_line):
                        if t:
                            subtitle.append(t)
                    subtitle = " | ".join(subtitle)
                    e['subtitle_text'] = subtitle
                    e['s'] = (None, dp(60)) if subtitle else (None, dp(40))
                    ListScreen.song_detail_cache[e['relpath']] = e
                    self.rv.refresh_from_data(modified=slice(i, i+1, None))
                    # Specifying the refreshed part saves 33% of time used
            i += 1
        Clock.schedule_once(self._get_details, 1)

    def update_songs(self, sender=None):
        del self.rv.data[:]
        app = App.get_running_app()
        songList = app.client.songList
        newdata = [{'title_text': item['name'],
                    'viewclass': 'BasicItem',
                    's': (None, dp(40)),
                    'relpath': item['relpath'],
                    'mtime': item['mtime']}
                    for item in songList]
        for d in newdata:
            if d['relpath'] in self.song_detail_cache.keys():
                val = self.song_detail_cache[d['relpath']]
                if d['mtime'] == val['mtime'] and val.has_key('subtitle_text'):
                    d['subtitle_text'] = val['subtitle_text']
                    d['s'] = val['s']
        self.rv.data.extend(newdata)

    def do_edit(self, relpath):
        self.dismiss_all()
        app = App.get_running_app()
        app.client.change_own_item('song', relpath)
        app.base.to_screen('editsong')

    def do_copy(self, relpath):
        self.dismiss_all()
        print('Song copy not yet implemented')

    @defer.inlineCallbacks
    def do_delete(self, relpath):
        self.dismiss_all()
        app = App.get_running_app()
        songObject = yield app.client.get_item('song', relpath)
        if songObject != None:
            title = "Delete permanently?"
            message = ("You are about to delete '{0}'. This cannot be undone."
                       .format(songObject.filepath))
            content = MDLabel(font_style='Body1',
                              theme_text_color='Secondary',
                              text=message,
                              size_hint_y=None,
                              valign='top')
            content.bind(texture_size=content.setter('size'))
            self.dialog = MDDialog(title=title,
                                   content=content,
                                   size_hint=(.8, .6),
                                   auto_dismiss=False)
            self.dialog.add_icontext_button("delete", "delete",
                    action=lambda x: self._do_delete_song('song', relpath))
            self.dialog.add_icontext_button("cancel", "close-circle",
                    action=lambda x: self.dialog.dismiss())
            self.dialog.open()
        else:
            self.error_dialog(relpath)

    def _do_delete_song(self, itemtype, filepath):
        self.dismiss_all()
        app = App.get_running_app()
        app.client.delete_item(itemtype=itemtype, relpath=filepath)

    def do_new(self):
        self.dismiss_all()
        app = App.get_running_app()
        app.client.change_own_item('song', '')
        app.base.to_screen('editsong')

    def do_add(self, relpath):
        self.dismiss_all()
        app = App.get_running_app()
        if not relpath:  # No valid selection
            return
        if app.base.presenting:  # Most recently presenting a song
            presentscreen = app.base.sm.get_screen('present')
            presentscreen.add_item('song', relpath)
        else:  # Most recently editing a set
            if app.client.ownSet:
                app.client.add_item_to_own_set('song', relpath)

    @defer.inlineCallbacks
    def primary_action(self, item_data):
        self.dismiss_all()
        app = App.get_running_app()
        relpath = item_data.get('relpath')
        if relpath:
            songObject = yield app.client.get_item('song', relpath)
            if songObject != None:
                content = MDLabel(font_style='Body1',
                                  theme_text_color='Secondary',
                                  text=songObject.words,
                                  size_hint_y=None,
                                  valign='top')
                content.bind(texture_size=content.setter('size'))
                self.dialog = MDDialog(title=songObject.title,
                                       content=content,
                                       size_hint=(.8, .6),
                                       auto_dismiss=True)
                self.dialog.add_icontext_button("edit", "pencil",
                        action=lambda x: self.do_edit(relpath))
                self.dialog.add_icontext_button("add", "playlist-plus",
                        action=lambda x: self.do_add(relpath))
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
                                               'text': 'Delete Song',
                                               'on_release': lambda: self.do_delete(relpath)},
                                              {'viewclass': 'IconTextMenuItem',
                                               'icon': 'content-copy',
                                               'text': 'Copy Song',
                                               'on_release': lambda: self.do_copy(relpath)},],
                                       width_mult=3
                                      )
            self.menu.open(caller)

    def error_dialog(self, relpath):
        self.dismiss_all()
        content = MDLabel(font_style='Body1',
                          theme_text_color='Secondary',
                          text=u"Song at '{}' not found".format(relpath),
                          size_hint_y=None,
                          valign='top')
        content.bind(texture_size=content.setter('size'))
        self.dialog = MDDialog(title=u"Problem loading song",
                               content=content,
                               size_hint=(.8, .4),
                               auto_dismiss=True)
        self.dialog.add_action_button("OK",
                action=lambda x: self.dialog.dismiss())
        self.dialog.open()


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
        app = App.get_running_app()
        data = self.rv.data
        i = 0
        while i < len(data):
            e = data[i]
            if not e.has_key('subtitle_text') and e.has_key('relpath'):
                item = yield app.client.get_set(e['relpath'])
                if i >= len(data) or data[i] != e:
                    # yield is async, and something may have changed data
                    # in the meantime. If so, time to break the loop and
                    # restart everything.
                    break
                elif item == None:
                    e['subtitle_text'] = 'Error loading'
                else:
                    text = [s['name'] for s in item.list_songs()]
                    subtitle = []
                    for s in text:
                        subtitle.append(' '.join(s.split(' ', 2)[:2]))
                    subtitle = " | ".join(subtitle)
                    e['subtitle_text'] = subtitle
                    e['num_items'] = len(text)
            i += 1
        Clock.schedule_once(self._get_details, 1)

    def update_sets(self, sender=None):
        del self.rv.data[:]
        app = App.get_running_app()
        setList = app.client.setList
        newdata = [{'title_text': item['name'],
                    'viewclass': 'CountItem',
                    's': (None, dp(60)),
                    'relpath': item['relpath']}
                   for item in setList]
        self.rv.data.extend(newdata)

    def do_edit(self, relpath):
        self.dismiss_all()
        app = App.get_running_app()
        app.client.change_own_set(relpath)
        app.base.to_screen('editset')

    def do_copy(self, relpath):
        self.dismiss_all()
        print('Set copy not yet implemented')

    @defer.inlineCallbacks
    def do_delete(self, relpath):
        self.dismiss_all()
        app = App.get_running_app()
        setObject = yield app.client.get_set(relpath)
        if setObject != None:
            title = "Delete permanently?"
            message = ("You are about to delete '{0}'. This cannot be undone."
                       .format(setObject.filepath))
            content = MDLabel(font_style='Body1',
                              theme_text_color='Secondary',
                              text=message,
                              size_hint_y=None,
                              valign='top')
            content.bind(texture_size=content.setter('size'))
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
            self.error_dialog(relpath)

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
                                  size_hint_y=None,
                                  valign='top')
                content.bind(texture_size=content.setter('size'))
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
                          size_hint_y=None,
                          valign='top')
        content.bind(texture_size=content.setter('size'))
        self.dialog = MDDialog(title=u"Problem loading set",
                               content=content,
                               size_hint=(.8, .4),
                               auto_dismiss=True)
        self.dialog.add_action_button("OK",
                action=lambda x: self.dialog.dismiss())
        self.dialog.open()
