#!/usr/bin/env python
import kivy
# kivy.require('1.9.0')
from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.uix.screenmanager import Screen, ScreenManager
from ..control.spset import SPSet
from .iconfont import iconfont
from .chordlabel import ChordLabel
from ..network.messages import GetItem

Builder.load_string("""
<MyStencil@BoxLayout+StencilView>
    padding: 0

<PresentScreen>:
    carousel: carousel
    pbadd: pbadd
    pbtranspose: pbtranspose
    sendMessage: app.sendMessage
    BoxLayout:
        padding: '10dp'
        MyStencil:
            FloatLayout:
                Carousel:
                    id: carousel
                    size: self.parent.size
                    pos: self.parent.pos
                Button:
                    id: pbadd
                    size_hint: None, None
                    size: app.buttonsize, app.buttonsize
                    pos: self.parent.size[0] - 1.5*app.buttonsize, 2*app.buttonsize
                    markup: True
                    on_press: app.base.to_screen('search')
                Button:
                    id: pbtranspose
                    size_hint: None, None
                    size: app.buttonsize, app.buttonsize
                    pos: self.parent.size[0] - self.size[0] - 0.5*app.buttonsize, 0.5*app.buttonsize
                    markup: True
""")


class PresentScreen(Screen):
    def __init__(self, **kwargs):
        super(PresentScreen, self).__init__(**kwargs)
        Clock.schedule_once(self._finish_init)

    def _finish_init(self, dt):
        self.pbadd.text = iconfont('plus')
        self.pbtranspose.text = iconfont('transpose')
        app = App.get_running_app()
        app.base.bind(current_set=self.on_set)

    def on_set(self, instance, value):
        if value and type(value) == type(SPSet()):
            carousel = self.carousel
            carousel.clear_widgets()
            def act(song):
                s = ChordLabel()
                carousel.add_widget(s)
                s.text = song.lyrics
            for item in value.list_songs():
                self.sendMessage(GetItem, itemtype='song',
                                 relpath=item['filepath'], callback=act)
