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
from time import sleep


class SongPrezApp(App):
    base = ObjectProperty(None)
    colwidth = NumericProperty(0)
    colspace = NumericProperty(0)
    rowheight = NumericProperty(0)
    rowspace = NumericProperty(0)
    inhibit = BooleanProperty(False)
    dataDir = StringProperty('')
    indexDir = StringProperty('')

    def build(self):
        self.settings_cls = SettingsWithSidebar
        self.use_kivy_settings = False
        self.control = None
        signal('initialized').connect(self._control_loaded)
        self.base = BaseWidget()
        self.base.bind(colwidth=self._colwidth)
        self.base.bind(colspace=self._colspace)
        self.base.bind(rowheight=self._rowheight)
        self.base.bind(rowspace=self._rowspace)
        self.base.current = 'LoadScreen'
        self.dataDir = self.config.get('filesfolders', 'datadir')
        self.indexDir = self.config.get('filesfolders', 'indexdir')
        Clock.schedule_once(self._verify_spcontrol)
        return self.base

    def _verify_spcontrol(self, dt):
        try:
            self.control = spcontrol.SPControl(self.indexDir, self.dataDir)
            self.control.daemon = True
            self.control.start()
        except Exception as e:
            print(e)
            self.open_settings()

    def _control_loaded(self, sender, **kwargs):
        self.base.current = 'EditScreen'
        self.inhibit = False

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
        if section == 'filesfolders' and key == 'searchindex':
            self._check_indexdir(value)
        if section == 'filesfolders' and key == 'datadir':
            self._check_datadir(value)

    def _check_indexdir(self, path):
        '''
        Verify that this path is valid directory
        '''
        if os.path.isdir(path) and os.path.isabs(path):
            self.indexDir = path

    def _check_datadir(self, path):
        '''
        Verify that this path is a valid directory, and create the necessary
        SongPrez folders if they don't exist yet. This will only happen if the
        directory is already empty though.
        '''
        if os.path.isdir(path) and os.path.isabs(path):
            self.dataDir = path
            if not os.listdir(path):
                # path is an empty directory
                if not os.path.exists(os.path.join(path, 'Songs')):
                    os.mkdir(os.path.join(path, 'Songs'))
                if not os.path.exists(os.path.join(path, 'Sets')):
                    os.mkdir(os.path.join(path, 'Sets'))


    def display_settings(self, settings):
        if not self.inhibit:
            super(SongPrezApp, self).display_settings(settings)
        self.inhibit = True

    def close_settings(self, *largs):
        super(SongPrezApp, self).close_settings(*largs)
        self.inhibit = False
        if not self.control:
            Clock.schedule_once(self._verify_spcontrol)
            # Maybe a pop-up here to mention WHY going back to settings?
