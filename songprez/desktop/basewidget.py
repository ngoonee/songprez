#!/usr/bin/env python
import kivy
# kivy.require('1.9.0')
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from blinker import signal
from .button import FocusButton, NormalSizeFocusButton
from .itemlist import ItemList
from .setlist import SetList
from .contentlist import ContentList

Builder.load_string("""
<BaseWidget>:
    orientation: 'horizontal'
    colwidth: self.width//13
    colspace: self.width//140
    rowheight: self.colwidth//3
    rowspace: self.colspace//2
    padding: (self.width - self.colwidth*12 - self.colspace*11)//2
    spacing: self.colspace
    setlist: setlist
    BoxLayout:
        orientation: 'vertical'
        padding: 0
        spacing: root.rowspace*3
        size_hint_x: None
        width: root.colwidth*3 + root.colspace*2
        ContentList:
            size_hint_y: 4
        SetList:
            id: setlist
            size_hint_y: 3
    BoxLayout:
        orientation: 'vertical'
        padding: 0
        spacing: root.rowspace
        size_hint_x: None
        width: root.colwidth*7 + root.colspace*6
        Button:
        BoxLayout:
            orientation: 'horizontal'
            size_hint_y: None
            height: root.rowheight
            padding: 0
            spacing: root.colspace
            NormalSizeFocusButton:
                text: 'Add to Set'
                on_release: print(app)
            NormalSizeFocusButton:
                text: 'Remove from Set'
                on_release: print(app.root)
            Widget:
                #size_hint_x: None
                #width: root.colwidth*3 + root.colspace*2
            NormalSizeFocusButton:
                text: 'Save Song As'
            NormalSizeFocusButton:
                text: 'Save Song'
    BoxLayout:
        orientation: 'vertical'
        padding: 0
        spacing: root.rowspace
        size_hint_x: None
        width: root.colwidth*2 + root.colspace*1
        Button:
        BoxLayout:
            orientation: 'horizontal'
            size_hint_y: None
            height: root.rowheight
            spacing: root.colspace
            BoxLayout:
                size_hint_x: None
                width: root.colwidth
            NormalSizeFocusButton:
                text: 'Settings'
        FocusButton:
            size_hint_y: None
            height: root.rowheight*2 + root.rowspace
            text: 'Present'
""")


class BaseWidget(BoxLayout):
    def __init__(self, **kwargs):
        super(BaseWidget, self).__init__(**kwargs)
        signal('curSet').connect(self._monitor_set)

    def _monitor_set(self, curset):
        self.setlist.setcontent.set_data(curset)

    pass
