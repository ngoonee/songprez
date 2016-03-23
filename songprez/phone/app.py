#!/usr/bin/env python
import kivy
# kivy.require('1.9.2')
from kivy.config import Config
Config.set('kivy', 'desktop', 0)
Config.set('kivy', 'keyboard_mode', "")
# install_twisted_rector must be called before importing the reactor, so do
# it here before anything else is loaded
from kivy.support import install_twisted_reactor
install_twisted_reactor()
from twisted.internet import reactor
from twisted.internet.endpoints import clientFromString
import os
from kivy.app import App
from kivy.clock import Clock
from kivy.properties import StringProperty, BooleanProperty, ListProperty
from kivy.properties import NumericProperty, ObjectProperty, DictProperty
from kivy.metrics import dp, sp
from ..control import spcontrol
from .basewidget import BaseWidget
from .settings import SPSettings
from .settingsjson import default_settings, build_settings
from ..network.spclient import SPClientFactory
from .fontutil import font_register


class SongPrezApp(App):
    base = ObjectProperty(None)
    dataDir = StringProperty('')
    indexDir = StringProperty('')
    sendMessage = ObjectProperty(None)
    buttonsize = NumericProperty(dp(32))
    ui_fs_button = NumericProperty(sp(24))
    ui_fs_title = NumericProperty(sp(24))
    ui_fs_main = NumericProperty(sp(18))
    ui_fs_detail = NumericProperty(sp(15))

    def build(self):
        self.settings_cls = SPSettings
        self.control = None
        font_register()
        self.base = BaseWidget()
        Clock.schedule_once(self._verify_spcontrol)
        return self.base

    def _verify_spcontrol(self, dt):
        try:
            indexDir = self.config.get("filesfolders", "indexdir")
            dataDir = self.config.get("filesfolders", "datadir")
            self.control = spcontrol.SPControl(indexDir, dataDir)
            client = clientFromString(reactor, 'tcp:localhost:1916')
            client.connect(SPClientFactory(self.base))
        except Exception as e:
            print(e)
            self.open_settings()

    def on_pause(self):
        return True

    def on_resume(self):
        pass

    def on_stop(self):
        self.control.quit()

    def _control_loaded(self):
        pass

    def get_application_config(self):
        return os.path.join(self.user_data_dir, 'songprez.ini')

    def build_config(self, config):
        default_settings(config)

    def build_settings(self, settings):
        build_settings(settings, self.config)

    def on_config_change(self, config, section,
                         key, value):
        print(config, section, key, value)

    def display_settings(self, settings):
        screen = self.base.sm.get_screen('settings')
        if settings not in screen.children:
            screen.add_widget(settings)

    def close_settings(self, *largs):
        super(SongPrezApp, self).close_settings(*largs)
        if not self.control:
            Clock.schedule_once(self._verify_spcontrol)
        if len(largs) and largs[0] is self._app_settings:
            # Called using close button
            self.base.back()
            return True
