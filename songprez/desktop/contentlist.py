#!/usr/bin/env python
import kivy
# kivy.require('1.9.0')
from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem, TabbedPanelHeader
from kivy.uix.behaviors import FocusBehavior
from blinker import signal
from .itemlist import ItemList
from .button import NormalSizeFocusButton
from .filenamedialog import FilenameDialog

Builder.load_string("""
#:import signal blinker.signal
<ContentList>:
    songlist: songlist
    searchlist: searchlist
    setlist: setlist
    songheader: songheader
    searchheader: searchheader
    setheader: setheader
    panel: panel
    orientation: 'vertical'
    padding: 0
    spacing: app.rowspace
    TabbedPanel:
        id: panel
        do_default_tab: False
        tab_height: app.rowheight
        tab_width: app.colwidth
        FocusPanelHeader:
            id: songheader
            text: 'Songs'
            content: songcontent.__self__
        FocusPanelHeader:
            id: searchheader
            text: 'Search'
            content: searchcontent.__self__
        FocusPanelHeader:
            id: setheader
            text: 'Sets'
            content: setcontent.__self__
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
                    on_text_validate: signal('search').send(None, SearchTerm=self.text); searchlist.focus = True
                    on_text_update: signal('search').send(None, SearchTerm=self.text)
                ItemList:
                    id: searchlist
            BoxLayout:
                id: setcontent
                padding: app.rowspace
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
            on_press: root._new_action()
        NormalSizeFocusButton:
            text: 'Rename'
            on_press: root._rename_action()
        NormalSizeFocusButton:
            text: 'Delete'
            on_press: root._delete_action()
""")


class FocusPanelHeader(FocusBehavior, TabbedPanelHeader):
    def on_focus(self, instance, value):
        self.bold = value

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



class ContentList(BoxLayout):
    def __init__(self, **kwargs):
        super(ContentList, self).__init__(**kwargs)
        signal('setList').connect(self._monitor_setList)
        signal('songList').connect(self._monitor_songList)
        signal('searchList').connect(self._monitor_searchList)
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
        signal('changeSong').send(self, Path=adapter.selection[0].filepath)

    def _set_selected(self, adapter):
        signal('changeSet').send(self, Path=adapter.selection[0].filepath)

    def _search_selected(self, adapter):
        signal('changeSong').send(self, Path=adapter.selection[0].filepath)

    def _monitor_setList(self, sender, **kwargs):
        setList = kwargs.get('List')
        self.setlist.set_data(setList)

    def _monitor_songList(self, sender, **kwargs):
        songList = kwargs.get('List')
        self.songlist.set_data(songList)

    def _monitor_searchList(self, sender, **kwargs):
        searchList = kwargs.get('List')
        self.searchlist.set_data(searchList)

    def _new_action(self):
        def do_new(signalSuffix):
            # Return value is a list of tuple-pairs (func, val), take first pair
            view = FilenameDialog('new' + signalSuffix)
            view.textinput.text = 'A New Song'
            view.open()
        def handle_song(song=None):
            do_new('Song')
        def handle_search():
            do_new('Song')
        def handle_set():
            do_new('Set')
        {"Songs": handle_song,
         "Search": handle_search,
         "Sets": handle_set}.get(self.panel.current_tab.text)()

    def _rename_action(self):
        def do_rename(signalSuffix, filepath):
            # Return value is a list of tuple-pairs (func, val), take first pair
            songObject = signal('get' + signalSuffix).send(None, Path=filepath)[0][1]
            view = FilenameDialog('save' + signalSuffix, Song=songObject)
            view.textinput.text = filepath
            view.open()
        def handle_song(song=None):
            filepath = (self.songlist.adapter.selection[0].filepath if
                        self.songlist.adapter.selection else None)
            if filepath:
                do_rename('Song', filepath)
        def handle_search():
            filepath = (self.searchlist.adapter.selection[0].filepath if
                        self.searchlist.adapter.selection else None)
            if filepath:
                do_rename('Song', filepath)
        def handle_set():
            filepath = (self.setlist.adapter.selection[0].filepath if
                        self.setlist.adapter.selection else None)
            if filepath:
                do_rename('Set', filepath)
        {"Songs": handle_song,
         "Search": handle_search,
         "Sets": handle_set}.get(self.panel.current_tab.text)()

    def _delete_action(self):
        def do_delete(signalSuffix, filepath):
            signal('delete' + signalSuffix).send(None, Path=filepath)
        def handle_song():
            filepath = (self.songlist.adapter.selection[0].filepath if
                        self.songlist.adapter.selection else None)
            if filepath:
                do_delete('Song', filepath)
        def handle_search():
            filepath = (self.searchlist.adapter.selection[0].filepath if
                        self.searchlist.adapter.selection else None)
            if filepath:
                do_delete('Song', filepath)
        def handle_set():
            filepath = (self.setlist.adapter.selection[0].filepath if
                        self.setlist.adapter.selection else None)
            if filepath:
                do_delete('Set', filepath)
        {"Songs": handle_song,
         "Search": handle_search,
         "Sets": handle_set}.get(self.panel.current_tab.text)()
