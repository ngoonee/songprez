#!/usr/bin/env python
# -*- coding: utf-8 -*-
import kivy
# kivy.require('1.9.0')
# install_twisted_rector must be called before importing the reactor, so do
# it here before anything else is loaded
from kivy.support import install_twisted_reactor
try:
    install_twisted_reactor()
except Exception as e:
    print(e)
from twisted.internet import reactor
from kivy.app import App
from kivy.properties import ObjectProperty
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from time import time
from ..control.spsong import SPSong
from .slide import SlideElement
from ..network.spclient import SPClientFactory
from ..network.messages import *

Builder.load_string("""
<ShowScreen>:
    carousel: carousel
    FloatLayout:
        Carousel:
            id: carousel
            direction: 'right'
            anim_move_duration: 0.3
""")


class ShowScreen(Screen):
    sendMessage = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(ShowScreen, self).__init__(**kwargs)
        self._app = App.get_running_app()
        self._keyboard = Window.request_keyboard(None, self, 'text')
        self.bind(parent=self._parent)
        self._set = []
        Clock.schedule_once(self._finish_init)

    def _finish_init(self, dt):
        reactor.connectTCP('localhost', 1916, SPClientFactory(self))

    def _parent(self, instance, value):
        '''
        Activated whenever this Screen obtains or loses a parent, use this to
        only bind keyboard when this is the active screen.
        '''
        if value:  # Has a parent - is the active screen
            self._keyboard.bind(on_key_down=self._on_keyboard_down)
        else:
            self._keyboard.unbind(on_key_down=self._on_keyboard_down)
            # Unfocus any focused widgets
            for widget in self.walk(restrict=True):
                if hasattr(widget, 'focus'):
                    widget.focus = False

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        if not self._app.inhibit:
            # Handle shortcut keys
            if keycode[1] == 'down':
                oldduration = self.carousel.anim_move_duration
                self.carousel.anim_move_duration = 0
                self.carousel.load_next()
                self.carousel.anim_move_duration = oldduration
            elif keycode[1] == 'up':
                oldduration = self.carousel.anim_move_duration
                self.carousel.anim_move_duration = 0
                self.carousel.load_previous()
                self.carousel.anim_move_duration = oldduration
            else:
                return False
            return True

    def on_connection(self, connection):
        self.sendMessage = connection.sendMessage

    def _running(self):
        pass

    def _song_list(self, songList):
        pass

    def _set_list(self, setList):
        pass

    def _search_list(self, searchList):
        pass

    def _show_set(self, set):
        self._set = set
        self._generate()

    def _show_position(self, item, slide):
        pass

    def _show_toggles(self, toggle):
        pass

    def _generate(self):
        for i, s in enumerate(self._set.list_songs()):
            # Create a SlideElement based on slide and item
            # Add SlideElement to carousel
            def act(so, carousel):
                slides = so.split_slides(presentation=s['presentation'])
                for sl in slides:
                    se = SlideElement(padding=(100, 100, 100, 100),
                                     font_size=180,
                                     halign='center', valign='middle')
                    se.text = sl['string']
                    carousel.add_widget(se)
            self.sendMessage(GetItem, itemtype='song', relpath=s['filepath'],
                             callback=act,
                             callbackKeywords={'carousel': self.carousel})
