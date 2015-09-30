#!/usr/bin/env python
import kivy
# kivy.require('1.9.0')
from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.properties import ListProperty, ObjectProperty, DictProperty
from kivy.properties import StringProperty
from kivy.uix.button import Button
from kivy.uix.stencilview import StencilView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.carousel import Carousel

Builder.load_string("""
<BaseWidget>:
    base: base.__self__
    BoxLayout:
        orientation: "horizontal"
        StencilView:
            size: self.size
            RelativeLayout:
                size: self.parent.size
                pos: self.parent.pos
                id: base

<PresentWidget>:
    base: base
    size_hint: None, None
    RelativeLayout:
        id: base
        size: self.parent.size
        pos: self.parent.pos
""")


class PresentWidget(StencilView):
    pass


class BaseWidget(BoxLayout):
    pass
