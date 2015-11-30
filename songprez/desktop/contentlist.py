#!/usr/bin/env python
import kivy
# kivy.require('1.9.0')
from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem, TabbedPanelHeader
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.stencilview import StencilView
from kivy.graphics import Color, Line
from .itemlist import ItemList
from .contentselect import ContentSelect
from .button import NormalSizeFocusButton
from .filenamedialog import FilenameDialog
from ..control.spsong import SPSong
from ..network.messages import *

Builder.load_string("""
<ContentList>:
    songlist: panel.songlist
    searchlist: panel.searchlist
    setlist: panel.setlist
    songheader: panel.songheader
    searchheader: panel.searchheader
    setheader: panel.setheader
    panel: panel
    orientation: 'vertical'
    padding: 0
    spacing: app.rowspace
    sendMessage: app.sendMessage
    ContentSelect:
        id: panel
        tab_height: app.rowheight
        tab_width: app.colwidth
    BoxLayout:
        orientation: 'horizontal'
        size_hint_y: None
        height: app.rowheight
        padding: 0
        spacing: app.colspace
        NormalSizeFocusButton:
            text: 'New'
            on_press: root._new_action()
        NormalSizeFocusButton:
            text: 'Rename'
            on_press: root._rename_action()
        NormalSizeFocusButton:
            text: 'Delete'
            on_press: root._delete_action()
""")


class ContentList(BoxLayout, StencilView):
    def _new_action(self):
        def do_new(message, **kwargs):
            view = FilenameDialog(message, **kwargs)
        def handle_song():
            do_new(NewEditItem, inittext=u'A New Song', itemtype='song')
        def handle_search():
            do_new(NewEditItem, inittext=u'A New Song', itemtype='song')
        def handle_set():
            do_new(NewEditSet, inittext=u'A New Set')
        {self.songheader: handle_song,
         self.searchheader: handle_search,
         self.setheader: handle_set}.get(self.panel.current_tab)()

    def _rename_action(self):
        def handle_song():
            filepath = (self.songlist.adapter.selection[0].filepath if
                        self.songlist.adapter.selection else None)
            if filepath:
                def act(result, *args, **kwargs):
                    view = FilenameDialog(SaveEditItem, inittext=filepath,
                                          delmessage=DeleteEditItem,
                                          itemtype='song', item=result)
                self.sendMessage(GetItem, itemtype='song', relpath=filepath,
                                 callback=act)
        def handle_search():
            filepath = (self.searchlist.adapter.selection[0].filepath if
                        self.searchlist.adapter.selection else None)
            if filepath:
                def act(result, *args, **kwargs):
                    view = FilenameDialog(SaveEditItem, inittext=filepath,
                                          delmessage=DeleteEditItem,
                                          itemtype='song', item=result)
                self.sendMessage(GetItem, itemtype='song', relpath=filepath,
                                 callback=act)
        def handle_set():
            filepath = (self.setlist.adapter.selection[0].filepath if
                        self.setlist.adapter.selection else None)
            if filepath:
                def act(result, *args, **kwargs):
                    view = FilenameDialog(SaveEditSet, inittext=filepath,
                                          delmessage=DeleteEditSet,
                                          set=result)
                self.sendMessage(GetSet, relpath=filepath, callback=act)
        {self.songheader: handle_song,
         self.searchheader: handle_search,
         self.setheader: handle_set}.get(self.panel.current_tab)()

    def _delete_action(self):
        def handle_song():
            filepath = (self.songlist.adapter.selection[0].filepath if
                        self.songlist.adapter.selection else None)
            if filepath:
                self.sendMessage(DeleteEditItem, itemtype='song', relpath=filepath)
        def handle_search():
            filepath = (self.searchlist.adapter.selection[0].filepath if
                        self.searchlist.adapter.selection else None)
            if filepath:
                self.sendMessage(DeleteEditItem, itemtype='song', relpath=filepath)
        def handle_set():
            filepath = (self.setlist.adapter.selection[0].filepath if
                        self.setlist.adapter.selection else None)
            if filepath:
                self.sendMessage(DeleteEditSet, relpath=filepath)
        {self.songheader: handle_song,
         self.searchheader: handle_search,
         self.setheader: handle_set}.get(self.panel.current_tab)()
