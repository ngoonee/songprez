#!/usr/bin/env python
import kivy
# kivy.require('1.9.1')
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.app import App
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import ScreenManager
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.modalview import ModalView
from kivymd.label import MDLabel
from kivymd.dialog import MDDialog
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
        md_bg_color: app.theme_cls.primary_color
        background_palette: 'Primary'
        background_hue: '500'
        left_action_items: [['menu', lambda x: app.nav_drawer.toggle()]]
    ScreenManager:
        id: sm
        SetScreen:
            id: sets
            name: 'sets'
        PresentScreen:
            id: present
            name: 'present'
        EditSetScreen:
            id: editset
            name: 'editset'
        SongScreen:
            id: songs
            name: 'songs'
        SearchScreen:
            id: search
            name: 'search'
        Screen:
            name: 'scripture'
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
        self.dialog = None
        Window.bind(on_key_down=self._on_keyboard_down)
        self.sm.bind(current=self._change_title)
        self.sm.bind(current=self._track_history)
        self.to_screen('scan')

    def _change_title(self, instance, data):
        toolbar = self.toolbar
        # Set the main label
        if data == 'scan':
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

    def _track_history(self, instance, data):
        """
        History tracking logic:-
        1. The purpose of history tracking is for the 'back' button to do
           something reasonable, rather than for repeated traversal through
           useless screens.
        2. There are two ways any screen is entered, either traversed to or
           via the back button. The latter always removes it from history,
           the former may or may not.
        4. Adding songs/items can be done to a set being edited or the active
           presentation. For convenience this can also be tracked here.
        """
        history = self._history
        print(history)
        # Save screen history
        if len(history) == 0:
            history.append(data)
        else:
            scr_prio = {'sets': 1,
                        'present': 2,
                        'editset': 3,
                        'scripture': 4, 'search': 4, 'songs': 4,
                        'editsong': 5,
                        'settings': 6, 'scan': 6}
            diff = scr_prio[data] - scr_prio[history[-1]]
            if diff == 0:  # Save level is sets<->present or songs<->search
                history.pop()
                self.sm.transition.direction = 'down'
            elif diff > 0:  # Normal case, progressing up the chain
                self.sm.transition.direction = 'left'
            else:  # 'Backward' jump, need to pare the list down
                newhistory = []
                for i, v in enumerate(history):
                    if scr_prio[data] - scr_prio[v] > 0:
                        newhistory.append(v)
                    else:
                        break
                del history[:]
                history.extend(newhistory)
                self.sm.transition.direction = 'right'
            history.append(data)
        if data == 'settings':
            app = App.get_running_app()
            app.open_settings()
        print(history)
            
    def _on_keyboard_down(self, *args):
        keycode = args[1]
        if keycode == 27:  # 'esc' on desktop, 'back' key on android
            self.back()
            return True
        return False

    def back(self):
        app = App.get_running_app()
        if self.dialog:
            # Pressing a second time to exit app
            app.stop()
        for widget in app.root_window.children:
            # If there's a modalview (Popup/MDDialog) somewhere, dismiss it
            if isinstance(widget, ModalView):
                widget.dismiss()
                return
        if len(self._history) > 1:
            if self.sm.current == 'settings':
                app.close_settings()
            self.sm.current = self._history[-2]
        else:
            title = "Exit Songprez?"
            message = ("Please confirm that you want to exit Songprez, "
                       "or press the back button again to exit.")
            content = MDLabel(font_style='Body1',
                              theme_text_color='Secondary',
                              text=message,
                              size_hint_y=None,
                              valign='top')
            content.bind(texture_size=content.setter('size'))
            self.dialog = MDDialog(title=title,
                                   content=content,
                                   size_hint=(.8, .6),
                                   auto_dismiss=True)
            self.dialog.add_icontext_button("ok", "checkbox-marked-circle-outline",
                    action=lambda x: app.stop())
            self.dialog.add_icontext_button("cancel", "close-circle",
                    action=lambda x: self.dialog.dismiss())
            self.dialog.bind(on_dismiss=self._clear_dialog)
            self.dialog.open()

    def _clear_dialog(self, *args):
        self.dialog = None

    def to_screen(self, name):
        """
        Order of events when moving back and forth through history:-
        1. All movement done using to_screen(name)
        2. Check whether sm.current can be left (unsaved changes etc.)
        3. Change sm.current
        """
        self.sm.current = name
