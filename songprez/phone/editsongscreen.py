#!/usr/bin/env python
import kivy
# kivy.require('1.9.1')
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import Screen
from kivy.metrics import dp

Builder.load_string("""
#:set left_width '100sp'
<LeftLabel@Label>:
    size_hint_x: None
    width: left_width
    text_size: self.size
    align: 'left'
<RightTextInput@TextInput>:
    multiline: False
    size_hint_y: None
    height: self.minimum_height
<EditSongScreen>:
    ScrollView:
        do_scroll_x: False
        canvas.before:
            Color:
                rgba: (.125, .125, .125, 1)
            RoundedRectangle:
                size: self.size
                pos: self.pos
                radius: dp(10),
        BoxLayout:
            padding: '10dp'
            spacing: '5dp'
            orientation: 'vertical'
            size_hint_y: None
            height: top.height + lyrics.height + bottom.height + dp(10)
            GridLayout:
                id: top
                cols: 2
                spacing: '5dp'
                size_hint_y: None
                height: self.minimum_height
                LeftLabel:
                    text: 'Title'
                RightTextInput:
                LeftLabel:
                    text: 'Author'
                RightTextInput:
                LeftLabel:
                    text: 'AKA'
                RightTextInput:
                LeftLabel:
                    text: 'Key Line'
                RightTextInput:
                LeftLabel:
                    text: 'Saved As'
                RightTextInput:
                    height: self.minimum_height
                    readonly: True
            TextInput:
                id: lyrics
                size_hint_y: None
                height: self.minimum_height
            GridLayout:
                id: bottom
                cols: 2
                spacing: '5dp'
                size_hint_y: None
                height: self.minimum_height
                LeftLabel:
                    text: 'Order'
                RightTextInput:
                LeftLabel:
                    text: 'Hymn #'
                RightTextInput:
                LeftLabel:
                    text: 'Copyright'
                RightTextInput:
                LeftLabel:
                    text: 'CCLI'
                RightTextInput:
                LeftLabel:
                    text: 'Key'
                RightTextInput:
                LeftLabel:
                    text: 'Capo'
                RightTextInput:
                LeftLabel:
                    text: 'Tempo'
                RightTextInput:
                LeftLabel:
                    text: 'Time Sig'
                RightTextInput:
                LeftLabel:
                    text: 'Theme'
                RightTextInput:
                LeftLabel:
                    text: 'User 1'
                RightTextInput:
                LeftLabel:
                    text: 'User 2'
                RightTextInput:
                LeftLabel:
                    text: 'User 3'
                RightTextInput:
""")

class EditSongScreen(Screen):
    pass
