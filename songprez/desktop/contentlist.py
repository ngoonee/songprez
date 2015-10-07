#!/usr/bin/env python
import kivy
# kivy.require('1.9.0')
from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock
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
    def __init__(self, **kwargs):
        super(ContentList, self).__init__(**kwargs)
        Clock.schedule_once(self._finish_init)

    def _finish_init(self, dt):
        self.songlist.bind(adapter=self._update_song_adapter)
        self.setlist.bind(adapter=self._update_set_adapter)
        self.searchlist.bind(adapter=self._update_search_adapter)

    def _update_song_adapter(self, instance, value):
        instance.adapter.bind(on_selection_change=self._song_selected)

    def _update_set_adapter(self, instance, value):
        instance.adapter.bind(on_selection_change=self._set_selected)

    def _update_search_adapter(self, instance, value):
        instance.adapter.bind(on_selection_change=self._search_selected)

    def _song_selected(self, adapter):
        print(adapter)
        print(adapter.selection)
        print(adapter.selection[0])
        #print(adapter.data)

    def _set_selected(self, adapter):
        print(adapter)

    def _search_selected(self, adapter):
        print(adapter)
