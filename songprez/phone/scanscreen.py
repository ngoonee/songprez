#!/usr/bin/env python
import kivy
kivy.require('1.9.0')
from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.carousel import Carousel
from .recyclelist import SPRecycleView
from kivy.properties import ListProperty, StringProperty
from kivymd.label import MDLabel
from kivymd.theming import ThemableBehavior
import kivymd.material_resources as m_res
from kivymd.button import MDRaisedButton, MDFlatButton
from .icontextbutton import IconTextButton

Builder.load_string("""
#:import STANDARD_INCREMENT kivymd.material_resources.STANDARD_INCREMENT
<Instructions>:
    text: ''
    padding: (dp(16), 0.3*STANDARD_INCREMENT, root.theme_cls.horizontal_margins, 0.3*STANDARD_INCREMENT)
    size_hint: 1, None
    height: self.minimum_height
    MDLabel:
        id: label
        text: root.text
        font_style: 'Headline'
        theme_text_color: root.theme_text_color
        text_color: root.text_color
        size_hint: 1, None
        height: self.texture_size[1]
<ScanScreen>:
    rv: rv
    button: connect
    BoxLayout:
        orientation: 'vertical'
        Instructions:
            text: 'Select the SongPrez host you want to connect to.'
        SPRecycleView:
            id: rv
        AnchorLayout:
            anchor_x: 'right'
            padding: dp(8)
            size_hint_y: None
            height: connect.height + dp(16)
            IconTextButton:
                id: connect
                text: "CONNECT"
                icon: 'remote'
                disabled: True
                on_press: root._done_preload()
""")


class Instructions(ThemableBehavior, BoxLayout):
    text_color = ListProperty(None, allownone=True)
    theme_text_color = StringProperty('Primary',allownone=True)


class ScanScreen(Screen):
    def __init__(self, **kwargs):
        super(ScanScreen, self).__init__(**kwargs)
        self.scanner = Clock.schedule_interval(self._do_scan, 1)
        Clock.schedule_once(self._finish_init)

    def _finish_init(self, dt):
        self.rv.bind(selected_identifier=self._activate_button)

    def _activate_button(self, instance, value):
        self.button.disabled = not(value)

    def _do_scan(self, dt):
        app = App.get_running_app()
        if app.seeker:
            app.seeker.findTargets()
            data = []
            for t in app.seeker.targets:
                data.append({'text': t['name'],
                             'secondary_text': t['addr'],
                             'viewclass': 'ScanItem'})
            self.rv.data = data

    def _done_preload(self):
        if self.rv.selected_identifier:
            app = App.get_running_app()
            self.scanner.cancel()
            app.base.to_screen('main')
