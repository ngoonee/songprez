#!/usr/bin/env python
import kivy
# kivy.require('1.9.1')
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.app import App
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import ScreenManager
from kivy.uix.boxlayout import BoxLayout
from ..control.spset import SPSet
from .scanscreen import ScanScreen
from .mainscreen import MainScreen
from .presentscreen import PresentScreen
from .listscreen import SetScreen, SongScreen, SearchScreen
from .fontutil import iconfont
from .editsetscreen import EditSetScreen
from .editsongscreen import EditSongScreen
from .toolbar import SPToolbar

Builder.load_string("""
#:import FallOutTransition kivy.uix.screenmanager.FallOutTransition
#:import NoTransition kivy.uix.screenmanager.NoTransition
#:import SwapTransition kivy.uix.screenmanager.SwapTransition
<Widget>:
    # Use same font throughout. Needed because SlideElement is a BoxLayout and
    # needs to have a font_name.
    font_name: 'NotoSans'
    # Sometime between revision 700 (g048821a) and 828 (g132be35) this was made
    # to work. Before that we needed to apply font_size separately to label and
    # TextInput.
<BaseWidget>:
    present: present
    sets: sets
    songs: songs
    search: search
    editset: editset
    editsong: editsong
    settings: settings
    sm: sm
    toolbar: toolbar
    orientation: "vertical"
    SPToolbar:
        id: toolbar
        title: 'SongPrez'
        background_color: app.theme_cls.primary_color
        left_action_items: [['menu', lambda x: app.nav_drawer.toggle()]]
    ScreenManager:
        id: sm
        Screen:
            name: 'preload'
        MainScreen:
            name: 'main'
        PresentScreen:
            id: present
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
            id: editset
            name: 'editset'
        EditSongScreen:
            id: editsong
            name: 'editsong'
        Screen:
            id: settings
            name: 'settings'
        ScanScreen:
            name: 'scan'
""")


class BaseWidget(BoxLayout):
    def __init__(self, **kwargs):
        super(BaseWidget, self).__init__(**kwargs)
        self.presenting = True
        self._history = []
        Window.bind(on_key_down=self._on_keyboard_down)
        self.sm.bind(current=self._change_title)
        self.to_screen('scan')

    def _change_title(self, instance, data):
        toolbar = self.toolbar
        # Set the main label
        if data == 'main' or data == 'preload' or data == 'scan':
            toolbar.title = 'SongPrez'
        elif data == 'sets':
            toolbar.title = 'Sets ' + iconfont('sets')
        elif data == 'songs':
            toolbar.title = 'Songs ' + iconfont('songs')
        elif data == 'present':
            self.presenting = True
            toolbar.title = 'Present ' + iconfont('present')
        elif data == 'search':
            toolbar.title = 'Search ' + iconfont('search')
        elif data == 'scripture':
            toolbar.title = 'Scripture ' + iconfont('scripture')
        elif data == 'settings':
            toolbar.title = 'Settings ' + iconfont('settings')
        elif data == 'editset':
            self.presenting = False
            toolbar.title = (iconfont('edit') + ' Edit Set ' + iconfont('sets'))
        elif data == 'editsong':
            toolbar.title = (iconfont('edit') + ' Edit Song ' + iconfont('songs'))
        return
        # Save screen history
        if data in ('preload', 'scan'):
            pass
        elif data == 'main' and self._history == []:
            self._history = ['main',]
        elif data == 'settings':
            app = App.get_running_app()
            app.open_settings()
        else:
            scr_prio = {'main': 1,
                        'present': 3, 'sets': 2,
                        'editset': 4,
                        'scripture': 5, 'search': 5, 'songs': 5,
                        'editsong': 6}
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
            self.back()
            return True
        return False

    def back(self):
        if len(self._history) > 1:
            self.sm.current = self._history[-2]
        elif self.sm.current == 'settings':
            self.to_screen(self._history[-1])
            App.get_running_app().close_settings()
        else:
            App.get_running_app().stop()  # Quit the app

    def to_screen(self, name):
        self.sm.current = name
