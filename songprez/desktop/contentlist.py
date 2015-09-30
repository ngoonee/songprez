#!/usr/bin/env python
import kivy
# kivy.require('1.9.0')
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from .itemlist import ItemList
from .button import NormalSizeFocusButton

Builder.load_string("""
<ContentList>:
    songlist: songlist
    searchlist: searchlist
    setlist: setlist
    orientation: 'vertical'
    padding: 0
    spacing: app.rowspace
    TabbedPanel:
        do_default_tab: False
        tab_height: app.rowheight
        tab_width: app.colwidth
        TabbedPanelItem:
            text: 'Songs'
            ItemList:
                id: songlist
        TabbedPanelItem:
            text: 'Search'
            ItemList:
                id: searchlist
        TabbedPanelItem:
            text: 'Sets'
            ItemList:
                id: setlist
    BoxLayout:
        orientation: 'horizontal'
        size_hint_y: None
        height: app.rowheight
        padding: 0
        spacing: app.colspace
        NormalSizeFocusButton:
            text: 'New'
        NormalSizeFocusButton:
            text: 'Rename'
        NormalSizeFocusButton:
            text: 'Delete'
""")


class ContentList(BoxLayout):
    pass
