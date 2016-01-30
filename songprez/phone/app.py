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
from ..control import spcontrol
from .basewidget import BaseWidget
from ..network.spclient import SPClientFactory
from .iconfont import icon_font_register


class SongPrezApp(App):
    base = ObjectProperty(None)
    dataDir = StringProperty('')
    indexDir = StringProperty('')
    sendMessage = ObjectProperty(None)

    def build(self):
        self.control = None
        self.base = BaseWidget()
        icon_font_register()
        Clock.schedule_once(self._verify_spcontrol)
        return self.base

    def _verify_spcontrol(self, dt):
        try:
            self.control = spcontrol.SPControl(self.indexDir, self.dataDir)
            client = clientFromString(reactor, 'tcp:localhost:1916')
            client.connect(SPClientFactory(self.base))
        except Exception as e:
            print(e)
            #self.open_settings()

    def on_stop(self):
        self.control.quit()

    def _control_loaded(self):
        pass

    def get_application_config(self):
        return os.path.join(self.user_data_dir, 'songprez.ini')
