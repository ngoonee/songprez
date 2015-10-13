#!/usr/bin/env python
import kivy
# kivy.require('1.9.0')
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager
from .editscreen import EditScreen

Builder.load_string("""
<BaseWidget>:
    songedit: editscreen.songedit
    contentlist: editscreen.contentlist
    currentset: editscreen.currentset
    colwidth: self.width//13
    colspace: self.width//140
    rowheight: self.colwidth//3
    rowheight: self.songedit.title.height
    rowspace: self.colspace//2
    Screen:
        name: 'EditScreen'
        EditScreen:
            id: editscreen
""")


class BaseWidget(ScreenManager):
    def __init__(self, **kwargs):
        super(BaseWidget, self).__init__(**kwargs)
