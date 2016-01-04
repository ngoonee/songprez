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
from twisted.internet.endpoints import clientFromString
from kivy.app import App
from kivy.properties import ObjectProperty
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.stencilview import StencilView
from time import time
from ..control.spsong import SPSong
from .slide import SlideElement
from ..network.spclient import SPClientFactory
from ..network.messages import *
from .contentselect import ContentSelect

Builder.load_string("""
<ShowScreen>:
    carousel: carousel
    panel: panel
    FloatLayout:
        Carousel:
            id: carousel
            direction: 'right'
            anim_move_duration: 0.3
        ContentSelect:
            id: panel
            tab_height: app.rowheight
            tab_width: app.colwidth
            size_hint_x: None
            width: app.colwidth*3 + app.colspace*2
            width: 0
""")


class ShowScreen(Screen, StencilView):
    sendMessage = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(ShowScreen, self).__init__(**kwargs)
        self._app = App.get_running_app()
        self._keyboard = Window.request_keyboard(None, self, 'text')
        self.bind(parent=self._parent)
        self._set = []
        self._indices = []
        self._showchords = False
        Clock.schedule_once(self._finish_init)

    def _finish_init(self, dt):
        client = clientFromString(reactor, 'tcp:host=localhost:port=1916')
        client.connect(SPClientFactory(self))

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
            elif keycode[1] == 'right':
                cur = self.carousel.index
                for i in self._indices:
                    if i > cur:
                        self.carousel.index = i
                        break
            elif keycode[1] == 'left':
                cur = self.carousel.index
                for i in reversed(self._indices):
                    if i < cur:
                        self.carousel.index = i
                        break
            elif keycode[1] == 't':
                self._showchords = not self._showchords
                self._generate()
            elif keycode[1] == 'escape':
                self.carousel.clear_widgets()
                self.parent.current = 'EditScreen'
            else:
                return False
            return True

    def on_connection(self, connection):
        self.sendMessage = connection.sendMessage

    def _running(self):
        pass

    def _song_list(self, listofsong):
        self.panel._song_list(listofsong)

    def _set_list(self, listofset):
        self.panel._set_list(listofset)

    def _search_list(self, listofsearch):
        self.panel._search_list(listofsearch)

    def _scripture_list(self, listofscripture):
        pass

    def _show_set(self, set):
        self._set = set
        self._generate()

    def _show_position(self, item, slide):
        pass

    def _show_toggles(self, toggle):
        pass

    def _generate(self):
        self._indices = []
        # Save current index and length to reapply for the regenerating case
        # TODO: use specific content in specific item instead
        cur = self.carousel.index
        length = len(self.carousel.slides)
        self.carousel.clear_widgets()
        for i, s in enumerate(self._set.list_songs()):
            if s['itemtype'] == 'song':
                # Create a SlideElement based on slide and item
                # Add SlideElement to carousel
                def act(so):
                    carousel = self.carousel
                    slides = so.split_slides(presentation=s['presentation'])
                    self._indices.append(len(carousel.slides))
                    for sl in slides:
                        # If showing chords, need a different font and string
                        halign = 'left' if self._showchords else 'center'
                        if self._showchords:
                            font = 'songprez/fonts/NotoSansMonoCJKsc-Regular.otf' 
                        else:
                            font = 'songprez/fonts/NotoSansCJK-Regular.ttc' 
                        se = SlideElement(padding=(100, 100, 100, 100),
                                         font_size=180, font_name=font,
                                         halign=halign, valign='middle')
                        if self._showchords:
                            se.text = sl['string']
                        else:
                            se.text = so.remove_chords(sl['string'])
                        if se.text:  # No point having a blank slide
                            carousel.add_widget(se)
                        # This check succeeds on last call if regenerating
                        # identical collection of slides
                        if len(carousel.slides) == length:
                            carousel.index = cur
                        else:
                            carousel.index = 0
                self.sendMessage(GetItem, itemtype='song', relpath=s['filepath'],
                                 callback=act)
            elif s['itemtype'] == 'scripture':
                print('not yet done scripture!')
