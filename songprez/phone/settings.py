#!/usr/bin/env python
import kivy
# kivy.require('1.9.1')
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.settings import SettingsWithSpinner, SettingItem
from kivy.uix.popup import Popup
from kivy.properties import ObjectProperty, BooleanProperty, StringProperty

import os

Builder.load_string("""
#:import os os
<SettingPathEx>:
    Label:
        text: root.value or ''
        pos: root.pos
        text_size: root.width/3, None
        shorten: True

<PathPopup>:
    accept: accept
    cancel: cancel
    filepath: filepath
    browser: browser
    title_font: self.font_name
    title_size: '32sp'
    BoxLayout:
        orientation: 'vertical'
        BoxLayout:
            orientation: 'horizontal'
            size_hint_y: None
            height: '32sp'
            Button:
                text: 'Icon'
                on_press: browser.view_mode = 'icon'
            Button:
                text: 'List'
                on_press: browser.view_mode = 'list'
        Label:
            id: filepath
            size_hint_y: None
            height: '32sp'
            halign: 'left'
            text_size: self.width, None
            shorten: True
        FileChooser:
            id: browser
            path: root.path
            dirselect: root.dirselect
            FileChooserIconLayout
            FileChooserListLayout
        BoxLayout:
            orientation: 'horizontal'
            size_hint_y: None
            height: '32sp'
            Button:
                id: accept
                text: 'OK'
            Button:
                id: cancel
                text: 'Cancel'
""")


class PathPopup(Popup):
    dirselect = BooleanProperty(False)
    path = StringProperty('')

    def __init__(self, **kwargs):
        super(PathPopup, self).__init__(**kwargs)
        self.auto_dismiss = False

    def _on_keyboard_down(self, *args):
        keycode = args[1]
        if keycode == 27:  # 'esc' on desktop, 'back' key on android
            self.dismiss()
            return True

    def on_open(self):
        Window.bind(on_key_down=self._on_keyboard_down)

    def on_dismiss(self):
        Window.unbind(on_key_down=self._on_keyboard_down)


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
        value = self.popup.filepath.text
        if value:
            self.value = os.path.realpath(value)
        self._dismiss()

    def _create_popup(self, instance):
        self.popup = PathPopup(title=self.title, size_hint=(0.9, 0.9),
                               path=self.value, dirselect=self.dirselect)
        dir_filter = lambda dir, elem: os.path.isdir(elem)
        self.popup.browser.filters=[dir_filter]
        def update_filepath(instance, value):
            if len(value) == 0 or value[-1] == '':
                self.popup.filepath.text = instance.path
            elif value[-1] == '../':
                self.popup.filepath.text = os.path.dirname(instance.path)
            else:
                self.popup.filepath.text = value[-1]
        self.popup.browser.bind(selection=update_filepath)
        self.popup.accept.bind(on_release=self._validate)
        self.popup.cancel.bind(on_release=self._dismiss)
        self.popup.open()


class SPSettings(SettingsWithSpinner):
    def __init__(self, *args, **kwargs):
        super(SPSettings, self).__init__(*args, **kwargs)
        self.register_type('pathex', SettingPathEx)
