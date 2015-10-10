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
from ..control import spcontrol
from .basewidget import BaseWidget
from .settingsjson import _default_settings, _build_settings


class SongPrezApp(App):
    base = ObjectProperty(None)
    colwidth = NumericProperty(0)
    colspace = NumericProperty(0)
    rowheight = NumericProperty(0)
    rowspace = NumericProperty(0)

    def __init__ (self, **kwargs):
        super(SongPrezApp, self).__init__(**kwargs)
        self._keyboard = Window.request_keyboard(None, self, 'text')
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
        self.control = spcontrol.SPControl(u'/tmp/searchindex', u'/home/data/Dropbox/OpenSong')
        self.control.daemon = True
        Clock.schedule_once(self._finish_init)

    def _finish_init(self, dt):
        self.control.start()

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
        print(keycode, text, modifiers)
        # Handle shortcut keys
        if modifiers == ['alt']:
            if keycode[1] == 's':
                self.root.contentlist.searchheader.trigger_action()
            elif keycode[1] == 'e':
                self.root.contentlist.setheader.trigger_action()
            elif keycode[1] == 'o':
                self.root.contentlist.songheader.trigger_action()
            elif keycode[1] == 'a':
                self.root.songedit.addtoset.trigger_action()
            elif keycode[1] == 'r':
                self.root.songedit.removefromset.trigger_action()
        return True

    def build(self):
        Window.bind(on_resize=self.win_cb)
        self.settings_cls = SettingsWithSidebar
        self.use_kivy_settings = False
        self.base = BaseWidget()
        self.base.bind(colwidth=self._colwidth)
        self.base.bind(colspace=self._colspace)
        self.base.bind(rowheight=self._rowheight)
        self.base.bind(rowspace=self._rowspace)
        return self.base

    def _colwidth(self, instance, value):
        self.colwidth = value

    def _colspace(self, instance, value):
        self.colspace = value

    def _rowheight(self, instance, value):
        self.rowheight = value

    def _rowspace(self, instance, value):
        self.rowspace = value

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
        '''
        if section == 'interface' and key == 'fontsize':
            self.systemFontSize = int(value)
            '''
        print(config, section, key, value)

    '''
    def display_settings(self, settings):
        manager = self.root.main._sm.get_screen("settings")
        if settings not in manager.children:
            manager.add_widget(settings)
            return True
        return False
        '''

    def close_settings(self, *largs):
        '''
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
            '''
