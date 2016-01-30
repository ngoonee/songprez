#!/usr/bin/env python
import kivy
# kivy.require('1.9.0')
from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen, ScreenManager
from .iconfont import iconfont

Builder.load_string("""
<MyStencil@BoxLayout+StencilView>
    padding: 0

<PresentScreen>:
    words: words
    pbadd: pbadd
    pbtranspose: pbtranspose
    BoxLayout:
        padding: '24dp'
        MyStencil:
            RelativeLayout:
                Label:
                    canvas.after:
                        Color:
                            rgba: 1, 0, 0, 0.1
                        Rectangle:
                            pos: self.pos
                            size: self.size
                    id: words
                Button:
                    id: pbadd
                    size_hint: None, None
                    size: '36dp', '36dp'
                    pos: self.parent.size[0] - dp(54), dp(72)
                    markup: True
                Button:
                    id: pbtranspose
                    size_hint: None, None
                    size: '36dp', '36dp'
                    pos: self.parent.size[0] - self.size[0] - dp(18), dp(18)
                    markup: True
""")


class PresentScreen(Screen):
    def __init__(self, **kwargs):
        super(PresentScreen, self).__init__(**kwargs)
        Clock.schedule_once(self._finish_init)

    def _finish_init(self, dt):
        self.pbadd.text = iconfont('plus')
        self.pbtranspose.text = iconfont('transpose')
        self.words.text = """
[C]
.F                   Bb      F
 Jesus Christ is the Lord of all
.C               F
 Lord of all the earth
.F                   Bb      F
 Jesus Christ is the Lord of all
.C               F
 Lord of all the earth

[V1]
.F        Bb  C       F
 Only one God  over the nations
.F        Bb      C
 Only one Lord of all
.   F        Bb   C            F
 In no other name  is there salvation
.F        Bb   C  F
 Jesus is Lord of all

[V2]
 Christ is the Head
 We are His body
 Satan beneath our feet
 We will proclaim
 He is our Vict'ry
 Jesus is Lord of all"""
