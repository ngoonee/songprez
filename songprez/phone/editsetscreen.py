#!/usr/bin/env python
import kivy
# kivy.require('1.9.1')
from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import Screen
from kivy.properties import ListProperty, ObjectProperty
from kivy.metrics import dp
from copy import deepcopy
from ..control.spset import SPSet
from .fontutil import iconfont
from .buttonrow import Buttons
from .modalpopup import ModalPopup
from ..network.messages import GetItem, SaveEditSet, DeleteEditSet
from .recyclelist import SPRecycleView, ListItem

Builder.load_string("""
#:set left_width '75sp'

<LeftLabel@Label>:
    size_hint_x: None
    width: left_width
    text_size: self.size
    align: 'left'
    font_size: app.ui_fs_detail

<RightTextInput@TextInput>:
    multiline: False
    size_hint_y: None
    height: self.minimum_height
    font_size: app.ui_fs_detail

<EditSetScreen>:
    setname: setname
    filepath: filepath
    rv: rv
    buttons: buttons
    sendMessage: app.sendMessage
    BoxLayout:
        orientation: 'vertical'
        padding: '5dp'
        spacing: '5dp'
        canvas.before:
            Color:
                rgba: (.125, .125, .125, 1)
            RoundedRectangle:
                size: self.size
                pos: self.pos
                radius: dp(10),
        GridLayout:
            id: top
            cols: 2
            spacing: '5dp'
            size_hint_y: None
            height: self.minimum_height
            LeftLabel:
                text: 'Name'
            RightTextInput:
                id: setname
            LeftLabel:
                text: 'Saved As'
            RightTextInput:
                id: filepath
                height: self.minimum_height
                readonly: True
        SPRecycleView:
            id: rv
            edit_action: root.bt_edit
            delete_action: root.bt_delete
            move_up_action: root.bt_move_up
            move_down_action: root.bt_move_down
            scripture_action: root.bt_scripture
            remove_item_action: root.bt_remove_item
            add_item_action: root.bt_add_item
        Buttons:
            id: buttons
            button1_action: root.bt_copy
            button2_action: root.bt_saveas
            button3_action: root.bt_save
""")

class EditSetScreen(Screen):
    itemlist = ListProperty([])
    set = ObjectProperty(None)
    current_set = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(EditSetScreen, self).__init__(**kwargs)
        Clock.schedule_once(self._finish_init)

    def _finish_init(self, dt):
        app = App.get_running_app()
        self.buttons.button1.text = iconfont('copy', app.ui_fs_button) + ' Copy'
        self.buttons.button2.text = iconfont('saveas', app.ui_fs_button) + ' Save As'
        self.buttons.button3.text = iconfont('save', app.ui_fs_button) + ' Save'

    def update_set(self, setObject):
        set = SPSet()
        self.set = setObject
        self.current_set = deepcopy(setObject)
        self.set_to_UI()

    def add_song(self, songObject):
        self.current_set.add_song(songObject)
        self.set_to_UI()

    def set_to_UI(self):
        self.itemlist = []
        self.rv.data = []
        setObject = self.current_set
        self.setname.text = setObject.name
        self.filepath.text = setObject.filepath
        for i, v in enumerate(setObject.list_songs()):
            name = v['name']
            itemtype = v['itemtype']
            if itemtype == 'scripture':
                continue
            filepath = v['filepath']
            app = App.get_running_app()
            def act(item, index):
                # First get the requisite title, subtitle, and text values
                title = item.title
                subtitle = [] 
                for t in (item.author, item.aka, item.key_line):
                    if t:
                        subtitle.append(t)
                subtitle = " | ".join(subtitle)
                text = item.words.split('\n')
                text = [t for t in text 
                        if t != '' and not (t[0] == '[' and t[-1] == ']')]
                summary = text[0:4]
                # Then create the dict
                if subtitle:
                    viewclass = 'ListItem'
                    h = app.ui_fs_main*1.5 + app.ui_fs_detail*1.5 + dp(10)
                else:
                    viewclass = 'ListItem'
                    h = app.ui_fs_main*1.5 + dp(10)
                self.rv.data.append({'index': index, 'titletext': title,
                                     'subtitletext': subtitle,
                                     'summarytext': summary,
                                     'expand_angle': 0, 'button_opacity': 0,
                                     'viewclass': viewclass, 'height': h,
                                     'set_edit': True, 'rv': self.rv})
                self.itemlist.append(item)
            self.sendMessage(GetItem, itemtype=itemtype, relpath=filepath,
                             callback=act, callbackKeywords={'index': i})
    
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
        pass

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
        if i+1 < len(data):
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

    def bt_remove_item(self, index):
        pass

    def bt_add_item(self, index):
        app = App.get_running_app()
        app.base.to_screen('search')

    def bt_copy(self):
        pass

    def bt_saveas(self):
        setObject = self.UI_to_set()
        message = ("Save the set '{0}' as".
                   format(setObject.name))
        popup = ModalPopup(message=message,
                           lefttext=iconfont('save') + ' Save',
                           leftcolor=(0, 0.6, 0, 1),
                           righttext=iconfont('cancel') + ' Cancel',
                           inputtext=setObject.filepath)
        popup.bind(on_left_action=self._do_save)
        popup.open()

    def bt_save(self):
        setObject = self.UI_to_set()
        if setObject != self.set or setObject.name != self.set.name:
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
            self.sendMessage(DeleteEditSet,
                             relpath=setObject.filepath)
            setObject.filepath = instance.input.text
        self.sendMessage(SaveEditSet, set=setObject,
                         relpath=setObject.filepath)
        self.set = setObject
