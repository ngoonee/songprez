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
from .button import NormalSizeFocusButton
from .filenamedialog import FilenameDialog
from ..control.spsong import SPSong
from ..network.messages import *

Builder.load_string("""
<ContentSelect>:
    songlist: songlist
    searchlist: searchlist
    setlist: setlist
    songheader: songheader
    searchheader: searchheader
    setheader: setheader
    sendMessage: app.sendMessage
    do_default_tab: False
    FocusPanelHeader:
        id: songheader
        markup: True
        text: 'S[color=ffff00][b]o[/b][/color]ngs'
        content: songcontent.__self__
    FocusPanelHeader:
        id: searchheader
        markup: True
        text: '[color=ffff00][b]S[/b][/color]earch'
        content: searchcontent.__self__
    FocusPanelHeader:
        id: setheader
        markup: True
        text: 'S[color=ffff00][b]e[/b][/color]ts'
        content: setcontent.__self__
    FocusPanelHeader:
        id: scriptureheader:
        markup: True
        text: 'Scripture'
        content: scripturecontent.__self__
    FloatLayout:
        BoxLayout:
            id: songcontent
            padding: app.rowspace
            ItemList:
                id: songlist
        BoxLayout:
            id: searchcontent
            orientation: "vertical"
            padding: app.rowspace
            spacing: app.rowspace
            SingleLineTextInput:
                on_text_validate: root._send_search(self.text); searchlist.focus = True
                on_text_update: root._send_search(self.text);
            ItemList:
                id: searchlist
        BoxLayout:
            id: setcontent
            padding: app.rowspace
            ItemList:
                id: setlist
        BoxLayout:
            id: scripturecontent
            padding: app.rowspace
            ItemList:
                id: scripturelist
""")


class FocusPanelHeader(FocusBehavior, TabbedPanelHeader):
    def __init__(self, **kwargs):
        super(FocusPanelHeader, self).__init__(**kwargs)
        self.bind(pos=self._draw_outline)
        self.bind(size=self._draw_outline)
        self.bind(focus=self._draw_outline)

    def _draw_outline(self, instance, value):
        try:
            self.canvas.remove(self._outline)
        except AttributeError:
            pass
        if self.focus:
            with self.canvas:
                Color(1, 0, 0, 0.6)
                rectOpt = (self.pos[0], self.pos[1], self.size[0], self.size[1])
                self._outline = Line(rectangle=rectOpt, width=2)

    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        super(FocusPanelHeader, self).keyboard_on_key_down(window, keycode, text, modifiers)
        if keycode[1] in ("enter", "spacebar"):
            self.trigger_action()
            return True
        return False

    def trigger_action(self, **kwargs):
        # When triggered, focus on focusable widgets in self.content (if any)
        super(FocusPanelHeader, self).trigger_action(**kwargs)
        self.focus = True
        for widget in self.content.walk(restrict=True):
            if isinstance(widget, FocusBehavior):
                widget.focus = True
                break


class ContentSelect(TabbedPanel):
    def __init__(self, **kwargs):
        super(ContentSelect, self).__init__(**kwargs)
        Clock.schedule_once(self._finish_init)

    def _finish_init(self, dt):
        self.songlist.bind(adapter=self._update_song_adapter)
        self.setlist.bind(adapter=self._update_set_adapter)
        self.searchlist.bind(adapter=self._update_search_adapter)
        self.searchlist.set_data([])
        self.songlist.set_data([])
        self.setlist.set_data([])

    def _update_song_adapter(self, instance, value):
        instance.adapter.bind(on_selection_change=self._song_selected)

    def _update_set_adapter(self, instance, value):
        instance.adapter.bind(on_selection_change=self._set_selected)

    def _update_search_adapter(self, instance, value):
        instance.adapter.bind(on_selection_change=self._search_selected)

    def _song_selected(self, adapter):
        self.sendMessage(ChangeEditItem, itemtype='song',
                        relpath=adapter.selection[0].filepath)

    def _set_selected(self, adapter):
        self.sendMessage(ChangeEditSet, relpath=adapter.selection[0].filepath)

    def _search_selected(self, adapter):
        self.sendMessage(ChangeEditItem, itemtype='song',
                        relpath=adapter.selection[0].filepath)

    def _send_search(self, text):
        self.sendMessage(Search, term=text)

    def _song_list(self, listofsong):
        self.songlist.set_data(listofsong)

    def _set_list(self, listofset):
        self.setlist.set_data(listofset)

    def _search_list(self, listofsearch):
        self.searchlist.set_data(listofsearch)
