#!/usr/bin/env python
import kivy
# kivy.require('1.9.1')
from kivy.config import Config
Config.set('kivy', 'desktop', 1)
Config.set('kivy', 'keyboard_mode', "")
import os
from kivy.app import App
from kivy.uix.settings import SettingsWithSidebar
from kivy.clock import Clock
from kivy.properties import StringProperty, BooleanProperty, ListProperty
from kivy.properties import NumericProperty, ObjectProperty, DictProperty
from kivy.uix.behaviors import FocusBehavior
from blinker import signal
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
        self.control = spcontrol.SPControl(u'/tmp/searchindex', u'/home/data/Dropbox/OpenSong')
        self.control.daemon = True
        Clock.schedule_once(self._finish_init)

    def _finish_init(self, dt):
        signal('initialized').connect(self._control_loaded)
        self.control.start()

    def _control_loaded(self, sender, **kwargs):
        self.base.current = 'EditScreen'

    def build(self):
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

    def get_application_config(self):
        return os.path.join(self.user_data_dir, 'songprez.ini')

    def build_config(self, config):
        _default_settings(config)

    def build_settings(self, settings):
        _build_settings(settings, self.config)

    def on_config_change(self, config, section,
                         key, value):
        print(config, section, key, value)

    def display_settings(self, settings):
        super(SongPrezApp, self).display_settings(settings)
        self.inhibit = True

    def close_settings(self, *largs):
        super(SongPrezApp, self).close_settings(*largs)
        self.inhibit = False
