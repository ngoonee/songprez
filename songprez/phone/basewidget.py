#!/usr/bin/env python
import kivy
# kivy.require('1.9.1')
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.app import App
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import ScreenManager
from kivy.uix.boxlayout import BoxLayout
from .mainscreen import MainScreen
from .presentscreen import PresentScreen
from .listscreen import SetScreen, SongScreen, SearchScreen
from .iconfont import iconfont
from .editsetscreen import EditSetScreen
from .editsongscreen import EditSongScreen

Builder.load_string("""
#:import FallOutTransition kivy.uix.screenmanager.FallOutTransition
#:import NoTransition kivy.uix.screenmanager.NoTransition
#:import SwapTransition kivy.uix.screenmanager.SwapTransition
<Widget>:
    # Use same font throughout. Needed because SlideElement is a BoxLayout and
    # needs to have a font_name.
    font_name: 'NotoSansCJK'
    # Sometime between revision 700 (g048821a) and 828 (g132be35) this was made
    # to work. Before that we needed to apply font_size separately to label and
    # TextInput.
<BaseWidget>:
    sets: sets
    songs: songs
    search: search
    editsong: editsong
    sm: sm
    title: title
    orientation: "vertical"
    Label:
        id: title
        size_hint_y: None
        height: '48dp'
        markup: True
        font_size: app.ui_fs_title
    ScreenManager:
        id: sm
        Screen:
            name: 'preload'
        MainScreen:
            name: 'main'
        PresentScreen:
            name: 'present'
        SetScreen:
            id: sets
            name: 'sets'
        SongScreen:
            id: songs
            name: 'songs'
        SearchScreen:
            id: search
            name: 'search'
        Screen:
            name: 'scripture'
        EditSetScreen:
            name: 'editset'
        EditSongScreen:
            id: editsong
            name: 'editsong'
        Screen:
            name: 'settings'
""")


class BaseWidget(BoxLayout):
    current_song = ObjectProperty(None)
    current_set = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(BaseWidget, self).__init__(**kwargs)
        self._history = []
        Window.bind(on_key_down=self._on_keyboard_down)
        self.sm.bind(current=self._change_title)
        self.sm.current = 'main'

    def _change_title(self, instance, data):
        title = self.title
        # Set the main label
        if data == 'main':
            title.text = 'SongPrez'
        elif data == 'sets':
            title.text = 'Sets ' + iconfont('sets')
        elif data == 'songs':
            title.text = 'Songs ' + iconfont('songs')
        elif data == 'present':
            title.text = 'Present ' + iconfont('present')
        elif data == 'search':
            title.text = 'Search ' + iconfont('search')
        elif data == 'scripture':
            title.text = 'Scripture ' + iconfont('scripture')
        elif data == 'settings':
            title.text = 'Settings ' + iconfont('settings')
        elif data == 'editset':
            title.text = (iconfont('edit') + ' Edit Set ' + iconfont('sets'))
        elif data == 'editsong':
            title.text = (iconfont('edit') + ' Edit Song ' + iconfont('songs'))
        # Save screen history
        if data == 'main' and self._history == []:
            self._history = ['main',]
        elif data == 'settings':
            pass
        else:
            scr_prio = {'main': 1,
                        'present': 2, 'sets': 2,
                        'editset': 3,
                        'scripture': 4, 'search': 4, 'songs': 4,
                        'editsong': 5}
            diff = scr_prio[data] - scr_prio[self._history[-1]]
            if diff == 0:  # Save level is sets<->present or songs<->search
                self._history.pop()
                self.sm.transition.direction = 'down'
            elif diff > 0:  # Normal case, progressing up the chain
                self.sm.transition.direction = 'left'
            else:  # 'Backward' jump, need to pare the list down
                newhistory = []
                for i, v in enumerate(self._history):
                    if scr_prio[data] - scr_prio[v] > 0:
                        newhistory.append(v)
                    else:
                        break
                self._history = newhistory
                self.sm.transition.direction = 'right'
            self._history.append(data)
            
    def _on_keyboard_down(self, *args):
        keycode = args[1]
        if keycode == 27:  # 'esc' on desktop, 'back' key on android
            if len(self._history) > 1:
                self.sm.current = self._history[-2]
            elif self.sm.current == 'settings':
                self.sm.current = self._history[-1]
            else:
                App.get_running_app().stop()  # Quit the app
            return True
        return False

    def on_connection(self, connection):
        print('connected successfully')
        app = App.get_running_app()
        app.sendMessage = connection.sendMessage

    def to_screen(self, name):
        self.sm.current = name

    def _running(self):
        app = App.get_running_app()
        app._control_loaded()

    def _song_list(self, listofsong):
        self.songs.item_list(listofsong)

    def _set_list(self, listofset):
        self.sets.item_list(listofset)

    def _search_list(self, listofsearch):
        self.search.item_list(listofsearch)

    def _scripture_list(self, listofscripture):
        pass

    def _edit_item(self, itemtype, item):
        pass

    def _edit_set(self, item):
        pass

    def _show_set(self, set):
        self.current_set = set
