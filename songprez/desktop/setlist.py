#!/usr/bin/env python
import kivy
# kivy.require('1.9.0')
from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty
from blinker import signal
from .itemlist import ItemList
from .button import NormalSizeFocusButton
from .filenamedialog import FilenameDialog

Builder.load_string("""
#:import signal blinker.signal
<SetList>:
    setcontent: setcontent
    orientation: 'vertical'
    padding: 0
    spacing: app.rowspace
    ItemList:
        id: setcontent
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


class SetList(BoxLayout):
    _setName = StringProperty('')

    def __init__(self, **kwargs):
        super(SetList, self).__init__(**kwargs)
        signal('curSet').connect(self._monitor_curSet)
        Clock.schedule_once(self._finish_init)

    def _finish_init(self, dt):
        self.setcontent.bind(adapter=self._update_set_adapter)

    def _update_set_adapter(self, instance, vaue):
        instance.adapter.bind(on_selection_change=self._song_selected)

    def _song_selected(self, adapter):
        signal('changeSong').send(self, Path=adapter.selection[0].filepath)

    def _monitor_curSet(self, sender, **kwargs):
        setObject = kwargs.get('Set')
        songList = [(s.filepath, s.title) for s in setObject.list_songs()]
        self._setName = setObject.name
        self.setcontent.set_data(songList)

    def _save_set_as(self):
        view = FilenameDialog('saveSet')
        view.textinput.text = self._setName
        view.open()
