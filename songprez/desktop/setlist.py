#!/usr/bin/env python
import kivy
# kivy.require('1.9.0')
from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, ObjectProperty
from copy import deepcopy
from .itemlist import ItemList
from .button import NormalSizeFocusButton
from .filenamedialog import FilenameDialog
from .textinput import SingleLineTextInput
from ..control.spset import SPSet
from ..network.messages import *

Builder.load_string("""
<SetList>:
    name: name
    filepath: filepath
    content: content
    orientation: 'vertical'
    padding: 0
    spacing: app.rowspace
    sendMessage: app.sendMessage
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
            on_press: root._up_song()
        NormalSizeFocusButton:
            text: 'Move Song Down'
            on_press: root._down_song()
    BoxLayout:
        orientation: 'horizontal'
        size_hint_y: None
        height: app.rowheight
        padding: 0
        spacing: app.colspace
        Widget:
        NormalSizeFocusButton:
            text: 'Save Set As'
            on_press: root._save_as()
        NormalSizeFocusButton:
            text: 'Save Set'
            on_press: root._save()
""")


class MovableItemList(ItemList):
    pass

class SetList(BoxLayout):
    _setName = StringProperty('')

    def __init__(self, **kwargs):
        super(SetList, self).__init__(**kwargs)
        self._setInit = None
        self._set = None
        Clock.schedule_once(self._finish_init)

    def _finish_init(self, dt):
        self.content.bind(adapter=self._update_set_adapter)

    def _update_set_adapter(self, instance, vaue):
        instance.adapter.bind(on_selection_change=self._song_selected)

    def _song_selected(self, adapter):
        selected = adapter.selection[0]
        self.sendMessage(ChangeEditItem, itemtype=selected.itemtype, relpath=selected.filepath)

    def _edit_set(self, set):
        setObject = deepcopy(set)
        self._setInit = setObject
        self._set = setObject
        self._set_to_list()

    def _edit_item(self, itemtype, item):
        '''
        If the current song is in the currently displayed set, select it
        '''
        dataObject = (item.filepath, item.title)
        if dataObject in self.content.adapter.data:
            index = self.content.adapter.data.index(dataObject)
            view = self.content.adapter.get_view(index)
            self.content.adapter.handle_selection(view, True)

    def _set_to_list(self):
        songList = self._set.list_songs()
        self.name.text = self._set.name
        self.filepath.text = self._set.filepath
        self.content.set_data(songList)

    def _list_to_set(self):
        setObject = deepcopy(self._setInit)
        setObject.name = self.name.text
        setObject.filepath = self.filepath.text
        songList = self.content.get_data()
        setObject.from_song_list(songList)
        return setObject

    def _save_as(self):
        setObject = self._list_to_set()
        view = FilenameDialog(SaveEditSet, inittext=setObject.filepath, set=setObject)
        view.textinput.text = self.name.text

    def _save(self):
        setObject = self._list_to_set()
        self.sendMessage(SaveEditSet, relpath=setObject.filepath, set=setObject)

    def _up_song(self):
        songList = self.content.get_data()
        i = self.content.adapter.selection[-1].index
        if i > 0:
            songList[i], songList[i-1] = songList[i-1], songList[i]
        self.content.set_data(songList)

    def _down_song(self):
        songList = self.content.get_data()
        i = self.content.adapter.selection[-1].index
        if i < len(songList)-1:
            songList[i], songList[i+1] = songList[i+1], songList[i]
        self.content.set_data(songList)
