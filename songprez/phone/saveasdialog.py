#!/usr/bin/env python
import kivy
# kivy.require('1.9.2')
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty

Builder.load_string("""
<SaveAsDialogContent>:
    filepath: filepath
    orientation: 'vertical'
    spacing: dp(16)
    size_hint_y: None
    height: self.minimum_height
    MDLabel:
        font_style: 'Body1'
        theme_text_color: 'Secondary'
        text: root.message
        size_hint_y: None
        height: self.texture_size[1]
    MDTextField:
        id: filepath
        text: root.suggestpath
        hint_text: "File path"
""")


class SaveAsDialogContent(BoxLayout):
    message = StringProperty('')
    suggestpath = StringProperty('')
