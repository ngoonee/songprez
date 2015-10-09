#!/usr/bin/env python
import kivy
# kivy.require('1.9.0')
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.label import Label

Builder.load_string("""
<MinimalLabel>:
    size_hint_x: None
    width: self.texture_size[0]
""")


class MinimalLabel(Label):
    pass
