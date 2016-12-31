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
from kivymd.label import MDLabel
from kivymd.dialog import MDDialog
from copy import deepcopy
from blinker import signal
from twisted.internet import defer
from ..control.spset import SPSet
from .fontutil import iconfont
from .saveasdialog import SaveAsDialogContent
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
                        on_release: root.add_from_search()
                    MDIconButton:
                        icon: 'file-document'
                        on_release: root.add_from_list()
                    MDIconButton:
                        icon: 'bible'
                        on_release: root.add_scripture()
                    Divider
                    MDIconButton:
                        icon: 'playlist-remove'
                        on_release: root.remove_item()
                    Divider
                    MDIconButton:
                        icon: 'arrow-up-bold'
                        on_release: root.do_move_up()
                    MDIconButton:
                        icon: 'arrow-down-bold'
                        on_release: root.do_move_down()
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
                    text: "SAVE AS"
                    icon: "at"
                    background_palette: 'Primary'
                    theme_text_color: 'Custom'
                    text_color: self.specific_text_color
                    on_release: root.do_saveas()
                IconTextButton:
                    text: "SAVE"
                    disabled: True if not root.filepath.text else False
                    icon: "content-save"
                    md_bg_color: app.theme_cls.accent_color
                    background_palette: 'Accent'
                    theme_text_color: 'Custom'
                    text_color: self.specific_text_color
                    on_release: root.do_save()
""")

class EditSetScreen(Screen):
    itemlist = ListProperty([])
    edit_set = ObjectProperty(SPSet())  # The internal set being modified
    dialog = ObjectProperty(None)

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
            self.edit_set = deepcopy(app.client.ownSet)
            Clock.schedule_once(self.set_to_UI)
        else:
            title = 'Error loading set'
            self.dialog = MDDialog(title=title,
                                   size_hint=(.8, .3),
                                   auto_dismiss=True)
            self.dialog.open()

    @defer.inlineCallbacks
    def add_item(self, itemtype, relpath):
        app = App.get_running_app()
        i = self.rv.selected_index
        target = i + 1 if i != -1 else i
        songObject = yield app.client.get_item(itemtype, relpath)
        self.edit_set.add_item(songObject, itemtype, target)
        self.set_to_UI()

    @defer.inlineCallbacks
    def set_to_UI(self, dt=None):
        self.itemlist = []
        self.rv.data = []
        setObject = self.edit_set
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
            setObject.add_item(item, 'song')
        return setObject

    def dismiss_all(self):
        if self.dialog:
            self.dialog.dismiss()

    def do_edit(self, index):
        self.dismiss_all()
        app = App.get_running_app()
        app.base.current_song = self.itemlist[index]
        app.base.to_screen('editsong')

    def add_from_search(self):
        self.dismiss_all()
        app = App.get_running_app()
        app.base.to_screen('search')

    def add_from_list(self):
        self.dismiss_all()
        app = App.get_running_app()
        app.base.to_screen('songs')

    def add_scripture(self):
        self.dismiss_all()
        pass

    def remove_item(self):
        self.dismiss_all()
        rv = self.rv
        data = self.rv.data
        itemlist = self.itemlist
        i = rv.selected_index
        if i != -1:  # -1 when nothing selected
            data.pop(i)
            itemlist.pop(i)
            if i < len(data):
                rv.layout_manager.select_node(i)
            else:
                rv.layout_manager.select_node(i-1)
            self.edit_set = self.UI_to_set()

    def do_move_up(self):
        self.dismiss_all()
        rv = self.rv
        data = self.rv.data
        itemlist = self.itemlist
        i = rv.selected_index
        if i != -1:  # -1 when nothing selected
            target = i-1
            if target > -1:
                data[target], data[i] = data[i], data[target]
                itemlist[target], itemlist[i] = itemlist[i], itemlist[target]
                rv.layout_manager.select_node(target)
                self.edit_set = self.UI_to_set()

    def do_move_down(self):
        self.dismiss_all()
        rv = self.rv
        data = self.rv.data
        itemlist = self.itemlist
        i = rv.selected_index
        if i != -1:  # -1 when nothing selected
            target = i+1
            if target < len(data):
                data[target], data[i] = data[i], data[target]
                itemlist[target], itemlist[i] = itemlist[i], itemlist[target]
                rv.layout_manager.select_node(target)
                self.edit_set = self.UI_to_set()

    def do_saveas(self):
        self.dismiss_all()
        setObject = self.UI_to_set()
        title = "Save set as a different file?"
        message = ("Save the set '{0}' as".
                   format(setObject.name))
        if setObject.filepath:
            suggestpath = setObject.filepath
        else:
            suggestpath = setObject.name
        content = SaveAsDialogContent(message=message,
                                      suggestpath=suggestpath)
        self.dialog = MDDialog(title=title,
                               content=content,
                               size_hint=(.8, .6),
                               auto_dismiss=False)
        self.dialog.add_icontext_button("save", "content-save",
                action=lambda x: self._do_save(setObject,
                    self.dialog.content.filepath.text))
        self.dialog.add_icontext_button("cancel", "close-circle",
                action=lambda x: self.dialog.dismiss())
        self.dialog.open()

    def do_save(self):
        self.dismiss_all()
        app = App.get_running_app()
        setObject = self.UI_to_set()
        if (setObject != app.client.ownSet
                or setObject.name != app.client.ownSet.name):
            if setObject.filepath == '':
                return self.do_saveas()
            title = "Save set?"
            message = ("Save the set '{0}' to file named '{1}'?".
                       format(setObject.name, setObject.filepath))
            content = MDLabel(font_style='Body1',
                              theme_text_color='Secondary',
                              text=message,
                              size_hint_y=None,
                              valign='top')
            content.bind(texture_size=content.setter('size'))
            self.dialog = MDDialog(title=title,
                                   content=content,
                                   size_hint=(.8, .6),
                                   auto_dismiss=False)
            self.dialog.add_icontext_button("save", "content-save",
                    action=lambda x: self._do_save(setObject, setObject.filepath))
            self.dialog.add_icontext_button("cancel", "close-circle",
                    action=lambda x: self.dialog.dismiss())
        else:
            title = "Nothing to save"
            message = ("Set '{0}' has not changed.".
                       format(setObject.name))
            content = MDLabel(font_style='Body1',
                              theme_text_color='Secondary',
                              text=message,
                              size_hint_y=None,
                              valign='top')
            content.bind(texture_size=content.setter('size'))
            self.dialog = MDDialog(title=title,
                                   content=content,
                                   size_hint=(.8, .4),
                                   auto_dismiss=True)
        self.dialog.open()

    def _do_save(self, setObject, relpath):
        self.dismiss_all()
        setObject.filepath = relpath
        app = App.get_running_app()
        app.client.save_set(set=setObject, relpath=relpath)
        app.client.change_own_set(relpath)
