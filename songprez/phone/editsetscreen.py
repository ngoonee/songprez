#!/usr/bin/env python
import kivy
# kivy.require('1.9.1')
from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import Screen
from kivy.properties import ListProperty, ObjectProperty
from kivy.metrics import dp, sp
from kivymd.textfields import SingleLineTextField
from kivymd.button import MDIconButton
from copy import deepcopy
from blinker import signal
from twisted.internet import defer
from ..control.spset import SPSet
from .fontutil import iconfont
from .modalpopup import ModalPopup
from .recyclelist import SPRecycleView

Builder.load_string("""
<Divider@Widget>:
    size_hint_y: None
    height: dp(1)
    canvas.before:
        Color:
            rgba: app.theme_cls.divider_color
        Rectangle:
            size: self.width - dp(16), self.height
            pos: self.x + dp(8), self.y

<EditSetScreen>:
    setname: setname
    filepath: filepath
    rv: rv
    sendMessage: app.sendMessage
    BoxLayout:
        orientation: 'vertical'
        BoxLayout:
            orientation: 'vertical'
            spacing: dp(10)
            padding: dp(16), dp(8), dp(16), dp(16)
            size_hint_y: None
            height: self.minimum_height
            SingleLineTextField:
                id: setname
                hint_text: 'Name'
            SingleLineTextField:
                id: filepath
                hint_text: 'Saved as'
                message: "File path is relative to main SongPrez folder"
                message_mode: "on_focus"
        BoxLayout:
            orientation: 'horizontal'
            SPRecycleView:
                canvas.before:
                    Color:
                        rgba: self.theme_cls.divider_color
                    Line:
                        points: (self.x+1, self.y+self.height, self.x+self.width, self.y+self.height, self.x+self.width, self.y+1, self.x+1, self.y+1)
                id: rv
            AnchorLayout:
                anchor_y: 'top'
                size_hint_x: None
                width: dp(48)
                BoxLayout:
                    orientation: 'vertical'
                    size_hint_y: None
                    height: self.minimum_height
                    MDIconButton:
                        icon: 'playlist-plus'
                        disabled: True
                        md_bg_color: (0, 0, 0, 0)
                    MDIconButton:
                        icon: 'magnify'
                    MDIconButton:
                        icon: 'file-document'
                    MDIconButton:
                        icon: 'bible'
                    Divider
                    MDIconButton:
                        icon: 'playlist-remove'
                    Divider
                    MDIconButton:
                        icon: 'arrow-up-bold'
                    MDIconButton:
                        icon: 'arrow-down-bold'
        AnchorLayout:
            anchor_x: 'right'
            padding: dp(8)
            size_hint_y: None
            height: buttons.height + dp(16)
            BoxLayout:
                id: buttons
                orientation: 'horizontal'
                size_hint: None, None
                width: self.minimum_width
                height: self.minimum_height
                spacing: dp(8)
                IconTextButton:
                    text: "COPY"
                    icon: "content-copy"
                    background_palette: 'Primary'
                    theme_text_color: 'Custom'
                    text_color: self.specific_text_color
                IconTextButton:
                    text: "SAVE AS"
                    icon: "at"
                    background_palette: 'Primary'
                    theme_text_color: 'Custom'
                    text_color: self.specific_text_color
                IconTextButton:
                    text: "SAVE"
                    icon: "content-save"
                    md_bg_color: app.theme_cls.accent_color
                    background_palette: 'Accent'
                    theme_text_color: 'Custom'
                    text_color: self.specific_text_color
""")

class EditSetScreen(Screen):
    itemlist = ListProperty([])
    set = ObjectProperty(SPSet())
    current_set = ObjectProperty(SPSet())

    def __init__(self, **kwargs):
        super(EditSetScreen, self).__init__(**kwargs)
        self._index_to_add = -1
        Clock.schedule_once(self._finish_init)

    def _finish_init(self, dt):
        app = App.get_running_app()
        self.rv.data = [{'viewclass': 'MDLabel',
                         'text': 'Please wait, still loading songs!',
                         'font_style': 'Headline',
                         'theme_text_color': 'Primary',
                         'secondary_theme_text_color': 'Primary',
                         'height': sp(60)}]
        signal('ownSet').connect(self._update_set)

    def _update_set(self, sender=None):
        app = App.get_running_app()
        if isinstance(app.client.ownSet, SPSet):
            self.set = app.client.ownSet
            self.current_set = deepcopy(self.set)
            Clock.schedule_once(self.set_to_UI)
        else:
            message = ("Could not load this set.")
            popup = ModalPopup(message=message,
                               righttext=iconfont('ok') + ' OK')
            popup.open()


    def add_song(self, songObject):
        self.current_set.add_song(songObject, self._index_to_add)
        self._index_to_add = -1
        self.set_to_UI()

    @defer.inlineCallbacks
    def set_to_UI(self, dt=None):
        self.itemlist = []
        self.rv.data = []
        setObject = self.current_set
        self.setname.text = setObject.name
        self.filepath.text = setObject.filepath
        app = App.get_running_app()
        del self.rv.data[:]
        data = self.rv.data
        if len(setObject.list_songs()):
            for i, v in enumerate(setObject.list_songs()):
                name = v['name']
                itemtype = v['itemtype']
                if itemtype == 'scripture':
                    continue
                filepath = v['filepath']
                item = yield app.client.get_item(itemtype, filepath)
                item = yield item
                if item:
                    # First get the requisite title, subtitle, and text values
                    title = item.title
                    subtitle = [] 
                    for t in (item.author, item.aka, item.key_line):
                        if t:
                            subtitle.append(t)
                    subtitle = " | ".join(subtitle)
                    data.append({'title_text': title,
                                 'subtitle_text': subtitle,
                                 'viewclass': 'DragItem',
                                 's': (None, dp(60)) if subtitle else (None, dp(40)),
                                 'relpath': item.filepath})
                    self.itemlist.append(item)
                else:
                    data.append({'title_text': 'Error loading {}'.format(v['filepath']),
                                 'subtitle_text': '',
                                 'viewclass': 'BasicItem',
                                 's': (None, dp(60)),
                                 'relpath': v['filepath']})
                    self.itemlist.append(item)
    
    def UI_to_set(self):
        setObject = SPSet()
        setObject.name = self.setname.text
        setObject.filepath = self.filepath.text
        for item in self.itemlist:
            setObject.add_song(item)
        return setObject

    def bt_edit(self, index):
        app = App.get_running_app()
        app.base.current_song = self.itemlist[index]
        app.base.to_screen('editsong')

    def bt_delete(self, index):
        self.bt_remove_item(index)

    def bt_move_up(self, i):
        rv = self.rv
        data = self.rv.data
        itemlist = self.itemlist
        if i > 0:
            # Save the selected state of the 'other' item
            prevselect = rv.adapter.get_view(i-1).is_selected
            # Swap the data dict and the actual item
            data[i-1], data[i] = data[i], data[i-1]
            itemlist[i-1], itemlist[i] = itemlist[i], itemlist[i-1]
            # Change the index values
            data[i-1]['index'] = i-1
            data[i]['index'] = i
            # Update the selected states
            rv.adapter.get_view(i-1).is_selected = True
            rv.adapter.get_view(i).is_selected = prevselect

    def bt_move_down(self, i):
        rv = self.rv
        data = self.rv.data
        itemlist = self.itemlist
        if i+2 < len(data):  # 'data' includes the additional blank item
            # Save the selected state of the 'other' item
            prevselect = rv.adapter.get_view(i+1).is_selected
            # Swap the data dict and the actual item
            data[i+1], data[i] = data[i], data[i+1]
            itemlist[i+1], itemlist[i] = itemlist[i], itemlist[i+1]
            # Change the index values
            data[i+1]['index'] = i+1
            data[i]['index'] = i
            # Update the selected states
            rv.adapter.get_view(i+1).is_selected = True
            rv.adapter.get_view(i).is_selected = prevselect

    def bt_scripture(self, index):
        pass

    def bt_remove_item(self, i):
        if i+1 < len(self.rv.data):  # 'data' includes the additional blank item
            obj = self.itemlist[i]
            self.current_set.remove_song(obj)
            self.set_to_UI()

    def bt_add_item(self, index):
        app = App.get_running_app()
        app.base.to_screen('search')
        self._index_to_add = index+1

    def bt_copy(self):
        pass

    def bt_saveas(self):
        setObject = self.UI_to_set()
        message = ("Save the set '{0}' as".
                   format(setObject.name))
        if setObject.filepath:
            suggestpath = setObject.filepath
        else:
            suggestpath = setObject.name
        popup = ModalPopup(message=message,
                           lefttext=iconfont('save') + ' Save',
                           leftcolor=(0, 0.6, 0, 1),
                           righttext=iconfont('cancel') + ' Cancel',
                           inputtext=suggestpath)
        popup.bind(on_left_action=self._do_save)
        popup.open()

    def bt_save(self):
        setObject = self.UI_to_set()
        if setObject != self.set or setObject.name != self.set.name:
            if setObject.filepath == '':
                return self.bt_saveas()
            message = ("Save the set '{0}' to file named '{1}'?".
                       format(setObject.name, setObject.filepath))
            popup = ModalPopup(message=message,
                               lefttext=iconfont('save') + ' Save',
                               leftcolor=(0, 0.6, 0, 1),
                               righttext=iconfont('cancel') + ' Cancel')
            popup.bind(on_left_action=self._do_save)
        else:
            message = ("Set '{0}' has not changed.".
                       format(setObject.name))
            popup = ModalPopup(message=message,
                               righttext=iconfont('ok') + ' Ok')
            popup.bind(on_left_action=self._noop)
        popup.open()

    def _noop(self, instance):
        return True

    def _do_save(self, instance):
        setObject = self.UI_to_set()
        if instance.input.text:
            if setObject.filepath:
                self.sendMessage(DeleteEditSet,
                                 relpath=setObject.filepath)
            setObject.filepath = instance.input.text
        self.sendMessage(SaveEditSet, set=setObject,
                         relpath=setObject.filepath)
        self.set = setObject
