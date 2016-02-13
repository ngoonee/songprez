#!/usr/bin/env python
import kivy
# kivy.require('1.9.1')
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout

Builder.load_string("""
<Buttons>:
    button1: button1
    button2: button2
    button3: button3
    size_hint_y: None
    height: app.buttonsize + dp(10)
    spacing: '5dp'
    Button:
        id: button1
        markup: True
        font_size: app.ui_fs_button
        on_press: root.button1_action()
    Button:
        id: button2
        markup: True
        font_size: app.ui_fs_button
        on_press: root.button2_action()
    Button:
        id: button3
        markup: True
        font_size: app.ui_fs_button
        on_press: root.button3_action()
""")

class Buttons(BoxLayout):
    pass
