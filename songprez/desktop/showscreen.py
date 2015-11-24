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
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from .slide import SlideElement
from ..network.spclient import SPClientFactory

Builder.load_string("""
<ShowScreen>:
    carousel: carousel
    FloatLayout:
        Carousel:
            id: carousel
            direction: 'right'
            anim_move_duration: 0
""")


class ShowScreen(Screen):
    def __init__(self, **kwargs):
        super(ShowScreen, self).__init__(**kwargs)
        self._app = App.get_running_app()
        self._keyboard = Window.request_keyboard(None, self, 'text')
        self.bind(parent=self._parent)
        self._set = []
        self._items = []
        self._slides = []
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
                self.carousel.load_next()
            elif keycode[1] == 'up':
                self.carousel.load_previous()
            else:
                return False
            return True

    def on_connection(self, connection):
        pass

    def _running(self):
        pass

    def _song_list(self, songList):
        pass

    def _set_list(self, setList):
        pass

    def _search_list(self, searchList):
        pass

    def _show_slides(self, slideList):
        self._slides = slideList
        self._generate()

    def _show_items(self, itemList):
        self._items = itemList
        self._generate()

    def _show_set(self, set):
        self._set = set
        self._generate()

    def _show_position(self, item, slide):
        pass

    def _show_toggles(self, toggle):
        pass

    def _generate(self):
        s = SlideElement(padding=(100,100,100,100), font_size=180,
                         halign='center', valign='middle')
        s.font_size = 180
        s.text = '''Did we in our own strength confide, our striving would be losing;
 Were not the right Man on our side, the Man of God's own choosing;
 Dost ask who that may be: Christ Jesus it is He;
 Lord Sabbaoth His Name, from age to age the same,
 And He must win the battle.'''
        s2 = SlideElement(padding=(0,0,0,0), font_size=180,
                         halign='center', valign='middle')
        s2.text = u"""The sun comes up, it's a new day dawning
 太阳升起 新的一天來臨
 It's time to sing Your song again
 又是時候 唱你的歌
 Whatever may pass, and whatever lies before me
 不管發生過什麼, 不管接下來如何
 Let me be singing when the evening comes
 讓我在黃昏前 在讚美神"""
        self.carousel.add_widget(s)
        self.carousel.add_widget(s2)
        return
        slideList, itemList, set = self._slides, self._items, self._set
        if (len(slideList) == len(itemList) and
                len(itemList) == len(set.list_songs())):
            for slide, item, data in zip(slideList, itemList,
                                         set.list_songs()):
                # Verify using item and data that same sets
                # Create a SlideElement based on slide and item
                # Add SlideElement to carousel
                pass
