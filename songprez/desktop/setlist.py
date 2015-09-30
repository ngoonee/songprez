#!/usr/bin/env python
import kivy
# kivy.require('1.9.0')
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from .itemlist import ItemList
from .button import NormalSizeFocusButton

Builder.load_string("""
<SetList>:
    setcontent: setcontent
    orientation: 'vertical'
    padding: 0
    spacing: app.rowspace
    ItemList:
        id: setcontent
    BoxLayout:
        orientation: 'horizontal'
        size_hint_y: None
        height: app.rowheight
        padding: 0
        spacing: app.colspace
        Widget:
        NormalSizeFocusButton:
            text: 'Save Set As'
        NormalSizeFocusButton:
            text: 'Save Set'
""")


class SetList(BoxLayout):
    pass
