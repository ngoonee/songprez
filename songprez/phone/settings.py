#!/usr/bin/env python
import kivy
# kivy.require('1.9.1')
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.settings import Settings, SettingItem
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty, BooleanProperty
from kivy.garden.filebrowser import FileBrowser
import os

Builder.load_string("""
<SettingPathEx>:
    Label:
        text: root.value or ''
        pos: root.pos
""")


class SettingPathEx(SettingItem):
    popup = ObjectProperty(None, allownone=True)
    dirselect = BooleanProperty(False)
    show_hidden = BooleanProperty(False)

    def on_panel(self, instance, value):
        if value is None:
            return
        self.bind(on_release=self._create_popup)

    def _dismiss(self, *largs):
        if self.popup:
            self.popup.dismiss()
        self.popup = None

    def _validate(self, instance):
        self._dismiss()
        if len(instance.selection):
            value = instance.selection[0]
            if not value:
                return
            self.value = os.path.realpath(value)

    def _create_popup(self, instance):
        content = BoxLayout()
        self.popup = Popup(title=self.title, content=content,
                           size_hint=(0.9, 0.9))
        browser = FileBrowser(select_string='Select', path=self.value,
                              dirselect=self.dirselect,
                              show_hidden=self.show_hidden)
        content.add_widget(browser)
        browser.bind(on_success=self._validate, on_canceled=self._dismiss)
        self.popup.open()


class SPSettings(Settings):
    def __init__(self, *args, **kwargs):
        super(SPSettings, self).__init__(*args, **kwargs)
        self.register_type('pathex', SettingPathEx)
