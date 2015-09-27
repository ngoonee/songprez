#!/usr/bin/env python
import kivy
# kivy.require('1.9.0')
from kivy.config import Config
Config.set('kivy', 'desktop', 1)
Config.set('kivy', 'keyboard_mode', "")
import os
from kivy.core.window import Window
from kivy.app import App
from kivy.uix.settings import SettingsWithSidebar
from kivy.clock import Clock
from kivy.properties import StringProperty, BooleanProperty, ListProperty
from kivy.properties import NumericProperty, ObjectProperty, DictProperty
from kivy.uix.behaviors import FocusBehavior
from .basewidget import BaseWidget
from .settingsjson import _default_settings, _build_settings
"search"
"browse_previous"
"browse_next"
"browse_add"
"edit_new"
"edit_copy"
"edit_rename"
"edit_delete"
"edit_undo"
"edit_save"
"edit_save"
"list_newset"
"list_saveset"
"list_renameset"
"list_deleteset"
"list_up"
"list_up"
"list_down"
"list_addsong"
"list_deletesong"
"search_previous"
"search_next"
"search_add"
"transpose_apply"
"transpose_sharpflat"


class SongPrezApp(App):
    landscape = BooleanProperty(False)
    tablet = BooleanProperty(False)
    minimal = BooleanProperty(False)
    height = NumericProperty(1920)
    width = NumericProperty(1080)
    buttons = DictProperty(None)
    root = ObjectProperty(None)
    _textinputs = ListProperty(None)
    systemFontSize = NumericProperty(None)

    def __init__ (self, **kwargs):
        super(SongPrezApp, self).__init__(**kwargs)
        self._keyboard = Window.request_keyboard(None, self, 'text')
        self._keyboard.bind(on_key_down=self._on_keyboard_down)

    def register_textinput(self, textInstance, value):
        '''
        All TextInput objects in SongPrez must register themselves here when
        having focus, and similarly de-register when losing focus. This is
        easily done using on_focus (see gui/misc.py)
        '''
        if value:
            self._textinputs.append(textInstance)
        else:
            self._textinputs.remove(textInstance)

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        def _invert(setting):
            if setting == "minimal":
                self.minimal = not self.minimal
            elif setting == "tablet":
                self.tablet = not self.tablet
        func, arg = {"escape": (self.root._back, None),
                     "m": (_invert, "minimal"),
                     "a": (_invert, "tablet"),
                     "g": (self.root._advance, "settings"),
                     "l": (self.root._advance, "list"),
                     "e": (self.root._advance, "edit"),
                     "t": (self.root._advance, "transpose"),
                     "b": (self.root._advance, "browse"),
                     "s": (self.root._advance, "search")}.get(keycode[1], (None, None))
        if func and len(self._textinputs) == 0:
            func(arg) if arg else func()
        return True

    def _handle_menu_button(self, button):
        func, arg = {"menu_list": (self.root._advance, "list"),
                     "menu_edit": (self.root._advance, "edit"),
                     "menu_transpose": (self.root._advance, "transpose"),
                     "menu_settings": (self.root._advance, "settings"),
                     "menu_browse": (self.root._advance, "browse"),
                     "menu_search": (self.root._advance, "search")
         }.get(button._name)
        func(arg)

    def build(self):
        Window.bind(on_resize=self.win_cb)
        self.settings_cls = SettingsWithSidebar
        self.use_kivy_settings = False
        self.root = BaseWidget()
        return self.root

    def win_cb(self, window, width, height):
        self.width = width
        self.height = height
        if width > height:
            self.landscape = True
        else:
            self.landscape = False

    def get_application_config(self):
        return os.path.join(self.user_data_dir, 'songprez.ini')

    def build_config(self, config):
        _default_settings(config)

    def build_settings(self, settings):
        _build_settings(settings, self.config)

    def on_config_change(self, config, section,
                         key, value):
        if section == 'interface' and key == 'fontsize':
            self.systemFontSize = int(value)
        print(config, section, key, value)

    def display_settings(self, settings):
        manager = self.root.main._sm.get_screen("settings")
        if settings not in manager.children:
            manager.add_widget(settings)
            return True
        return False

    def close_settings(self, *largs):
        if len(largs) and largs[0] is self._app_settings:
            # Called using close button
            self.root._back()
            return True
        else:
            manager = self.root.main._sm.get_screen("settings")
            settings = self._app_settings
            if settings is None:
                return
            if settings in manager.children:
                manager.remove_widget(settings)
                return True
            return False
