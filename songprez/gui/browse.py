#!/usr/bin/env python
import kivy
# kivy.require('1.9.0')
from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from .alphalist import AlphabetList
from .misc import LyricPreview, ButtonGridLayout

Builder.load_string("""
#:import sla kivy.adapters.listadapter
#:import ListItemButton kivy.uix.listview.ListItemButton
<SongBrowse@BoxLayout>:
    orientation: "horizontal"
    ListView:
        size_hint: (1,1)
        adapter:
            sla.ListAdapter(data=[], cls=ListItemButton)
        item_strings: ["Song " + str(i) for i in range(100)]
        allow_empty_selection: False
    AlphabetList:
<MinBrowse>:
    orientation: "vertical"
    SongBrowse:
    ButtonGridLayout:
        rows: 1
        MyButton:
            text: "Previous"
            _name: "browse_previous"
            on_press: root.previous()
        MyButton:
            text: "Next"
            _name: "browse_next"
            on_press: root.next()
        MyButton:
            text: "Add"
            _name: "browse_add"
            on_press: root.add()
<MaxBrowse>:
    orientation: "horizontal"
    SongBrowse:
    LyricPreview:
        base: root.__self__
""")


class BrowseWidget():
    def previous(self):
        print("ACTION: Select previous song in browse view")

    def next(self):
        print("ACTION: Select next song in browse view")

    def add(self):
        print("ACTION: Add currently selected (by browse) song to current list")

class MinBrowse(BoxLayout, BrowseWidget):
    pass


class MaxBrowse(BoxLayout, BrowseWidget):
    def __init__(self, **kwargs):
        super(MaxBrowse, self).__init__(**kwargs)
        Clock.schedule_once(self._finish_init)

    def _finish_init(self, dt):
        # Walk widget tree to find the ButtonGridLayout in the LyricPreview
        for widget in self.walk(restrict=True):
            if isinstance(widget, LyricPreview):
                for w in widget.walk(restrict=True):
                    if isinstance(w, ButtonGridLayout):
                        gridlayout = w
        for b in gridlayout.children:
            b._name = "browse" + b._name
