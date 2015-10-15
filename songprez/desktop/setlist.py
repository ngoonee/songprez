#!/usr/bin/env python
import kivy
# kivy.require('1.9.0')
from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty
from blinker import signal
from copy import deepcopy
from .itemlist import ItemList
from .button import NormalSizeFocusButton
from .filenamedialog import FilenameDialog
from .textinput import SingleLineTextInput

Builder.load_string("""
#:import signal blinker.signal
<SetList>:
    name: name
    filepath: filepath
    content: content
    orientation: 'vertical'
    padding: 0
    spacing: app.rowspace
    BoxLayout:
        size_hint_y: None
        height: app.rowheight
        MinimalLabel:
            text: 'Set Name: '
        SingleLineTextInput:
            id: name
    BoxLayout:
        orientation: 'horizontal'
        size_hint_y: None
        padding_y: app.rowspace
        height: app.rowheight
        MinimalLabel:
            id: filepath_pre
            text: 'Saved as '
        MinimalLabel:
            size_hint__x: 1
            text_size: self.parent.width - filepath_pre.width, None
            shorten: True
            id: filepath
    MovableItemList:
        id: content
    BoxLayout:
        orientation: 'horizontal'
        size_hint_y: None
        height: app.rowheight
        padding: 0
        spacing: app.colspace
        Widget:
        NormalSizeFocusButton:
            text: 'Move Song Up'
            on_press: signal('upSong').send(None)
        NormalSizeFocusButton:
            text: 'Move Song Down'
            on_press: signal('downSong').send(None)
    BoxLayout:
        orientation: 'horizontal'
        size_hint_y: None
        height: app.rowheight
        padding: 0
        spacing: app.colspace
        Widget:
        NormalSizeFocusButton:
            text: 'Save Set As'
            on_press: root._save_set_as()
        NormalSizeFocusButton:
            text: 'Save Set'
            on_press: signal('saveSet').send(None)
""")


class MovableItemList(ItemList):
    pass

class SetList(BoxLayout):
    _setName = StringProperty('')

    def __init__(self, **kwargs):
        super(SetList, self).__init__(**kwargs)
        signal('curSet').connect(self._monitor_curSet)
        Clock.schedule_once(self._finish_init)

    def _finish_init(self, dt):
        self.content.bind(adapter=self._update_set_adapter)

    def _update_set_adapter(self, instance, vaue):
        instance.adapter.bind(on_selection_change=self._song_selected)

    def _song_selected(self, adapter):
        signal('changeSong').send(self, Path=adapter.selection[0].filepath)

    def _monitor_curSet(self, sender, **kwargs):
        setObject = kwargs.get('Set')
        self._setInit = setObject
        songList = [(s.filepath, s.title) for s in setObject.list_songs()]
        self.name.text = setObject.name
        self.filepath.text = setObject.filepath
        self.content.set_data(songList)

    def _save_set_as(self):
        setObject = deepcopy(self._setInit)
        setObject.name = self.name.text
        view = FilenameDialog('saveSet', Set=setObject)
        view.textinput.text = self.name.text
        view.open()
