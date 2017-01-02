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
from .presentscreen import PresentScreen
from .listscreen import SetScreen, SongScreen, SearchScreen
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
        left_action_items: [['keyboard-backspace', lambda x: app.base.back()]]
        right_action_items: [['menu', lambda x: app.nav_drawer.toggle()]]
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
        app = App.get_running_app()
        self.presenting = True
        self._history = ['sets']
        self.sm.current = 'sets'
        self.toolbar.title = 'Sets'
        self.toolbar.left_action_items = [['home', lambda x: None]]
        self.toolbar.right_action_items = [['book-open-page-variant', lambda x: None],
                                           ['menu', lambda x: app.nav_drawer.toggle()]]
        self.dialog = None
        Window.bind(on_key_down=self._on_keyboard_down)
        self.sm.bind(current=self._change_title)

    def _change_title(self, instance, data):
        app = App.get_running_app()
        toolbar = self.toolbar
        toolbar.left_action_items = [['keyboard-backspace', self.back]]
        # Set the main label
        if data == 'scan':
            toolbar.title = 'SongPrez'
            toolbar.right_action_items = [['remote', lambda x: None]]
        elif data == 'sets':
            toolbar.title = 'Sets'
            toolbar.left_action_items = [['home', lambda x: None]]
            toolbar.right_action_items = [['book-open-page-variant', lambda x: None]]
        elif data == 'songs':
            toolbar.title = 'Songs'
            toolbar.right_action_items = [['file-document', lambda x: None]]
        elif data == 'present':
            self.presenting = True
            toolbar.title = 'Present'
            toolbar.right_action_items = [['presentation-play', lambda x: None]]
        elif data == 'search':
            toolbar.title = 'Search'
            toolbar.right_action_items = [['magnify', lambda x: None]]
        elif data == 'scripture':
            toolbar.title = 'Scripture'
            toolbar.right_action_items = [['bible', lambda x: None]]
        elif data == 'settings':
            toolbar.title = 'Settings'
            toolbar.right_action_items = [['settings', lambda x: None]]
        elif data == 'editset':
            self.presenting = False
            toolbar.title = 'Edit Set'
            toolbar.right_action_items = [['pencil', lambda x: None],
                                          ['book-open-page-variant', lambda x: None]]
        elif data == 'editsong':
            toolbar.title = 'Edit Song'
            toolbar.right_action_items = [['pencil', lambda x: None],
                                          ['file-document', lambda x: None]]
        toolbar.right_action_items.append(['menu', lambda x: app.nav_drawer.toggle()])

    def _plan_history_change(self, name):
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
        new_history = self._history[:]
        removed_screens = []
        # Save screen history
        if len(new_history) == 0:
            new_history.append(name)
        else:
            scr_prio = {'sets': 1,
                        'present': 2,
                        'editset': 3,
                        'scripture': 4, 'search': 4, 'songs': 4,
                        'editsong': 5,
                        'settings': 6, 'scan': 6}
            diff = scr_prio[name] - scr_prio[new_history[-1]]
            if diff == 0:  # Save level is sets<->present or songs<->search
                removed_screens.append(new_history.pop())
                self.sm.transition.direction = 'down'
            elif diff > 0:  # Normal case, progressing up the chain
                self.sm.transition.direction = 'left'
            else:  # 'Backward' jump, need to pare the list down
                for i, v in enumerate(new_history):
                    if scr_prio[name] - scr_prio[v] > 0:
                        split_point = i
                    else:
                        break
                removed_screens = new_history[i+1:]
                new_history = new_history[:i]
                self.sm.transition.direction = 'right'
            new_history.append(name)
        return new_history, removed_screens
            
    def _on_keyboard_down(self, *args):
        keycode = args[1]
        if keycode == 27:  # 'esc' on desktop, 'back' key on android
            self.back()
            return True
        return False

    def back(self, skip_modal=False):
        app = App.get_running_app()
        if self.dialog:
            # Pressing a second time to exit app
            app.stop()
        if not skip_modal:
            for widget in app.root_window.children:
                # If there's a modalview (Popup/MDDialog) somewhere, dismiss it
                if isinstance(widget, ModalView):
                    widget.dismiss()
                    return
        if len(self._history) > 1:
            if self.sm.current == 'settings':
                app.close_settings()
            self.to_screen(self._history[-2])
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

    def to_screen(self, name, skip_save_check=False):
        """
        All screen changes must be done using to_screen(screen_name).

        This allows for checks to be run prior to actually changinge the
        screen (if necessary).
        """
        # Check if current screen needs a save reminder
        if not skip_save_check:
            cur_scr = self.sm.current_screen
            if getattr(cur_scr, 'safe_to_exit', None):
                if not cur_scr.safe_to_exit():
                    return
        new_history, removed_screens = self._plan_history_change(name)
        # Check if skipped-over screens need a save reminder
        for scr_name in reversed(removed_screens):
            scr = self.sm.get_screen(scr_name)
            if getattr(scr, 'safe_to_exit', None):
                if not scr.safe_to_exit():
                    self.sm.current = scr_name
                    return
        # Passed all checks, go ahead and change both history and screen
        self._history = new_history
        self.sm.current = name
        if name == 'settings':
            app = App.get_running_app()
            app.open_settings()

    def add_item(self, itemtype, relpath):
        if self.presenting:
            self.present.add_item(itemtype, relpath)
        else:
            self.editset.add_item(itemtype, relpath)
