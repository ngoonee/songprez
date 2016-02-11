#!/usr/bin/env python
import kivy
# kivy.require('1.9.0')
from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.uix.scrollview import ScrollView
from kivy.uix.listview import ListItemButton, ListView
from kivy.adapters.listadapter import ListAdapter
from kivy.uix.behaviors import FocusBehavior
from kivy.graphics import Color, Line

from kivy.event import EventDispatcher
from kivy.compat import PY2
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.adapters.simplelistadapter import SimpleListAdapter
from kivy.uix.abstractview import AbstractView
from kivy.properties import ObjectProperty, DictProperty, \
        NumericProperty, ListProperty, BooleanProperty, StringProperty
from math import ceil, floor

from ..control.spsong import SPSong
from ..control.spset import SPSet

Builder.load_string("""
<CustomListItemButton>:
    font_name: 'songprez/fonts/NotoSansMonoCJKsc-Regular.otf'
<ListView>:
    scroll: scroll
    container: container
    ScrollView:
        id: scroll
        pos: root.pos
        on_scroll_y: root._scroll(args[1])
        do_scroll_x: False
        bar_width: 20
        scroll_type: ['bars', 'content']
        effect_cls: 'ScrollEffect'
        GridLayout:
            cols: 1
            id: container
            size_hint_y: None
<ItemList>:
""")


class CustomListItemButton(ListItemButton):
    _was_pressed = BooleanProperty(False)
    filepath = StringProperty(u'')
    presentation = StringProperty(u'')
    itemtype = StringProperty(u'')
    index = NumericProperty(-1)


class CustomListAdapter(ListAdapter):
    def handle_selection(self, view, hold_dispatch=False, *args):
        if view not in self.selection:
            if self.selection_mode in ['none', 'single'] and \
                    len(self.selection) > 0:
                for selected_view in self.selection:
                    self.deselect_item_view(selected_view)
            if self.selection_mode != 'none':
                if self.selection_mode == 'multiple':
                    if self.allow_empty_selection:
                        # If < 0, selection_limit is not active.
                        if self.selection_limit < 0:
                            self.select_item_view(view)
                        else:
                            if len(self.selection) < self.selection_limit:
                                self.select_item_view(view)
                    else:
                        self.select_item_view(view)
                else:
                    self.select_item_view(view)
        else:
            if len(self.selection) == 1 and not self.allow_empty_selection:
                # Maintain selection rather than always defaulting to first
                # item. This probably invalidates the next if section, but I
                # am unable to test all corner cases out, and leaving it in
                # does not hurt anything.
                pass
            else:
                self.deselect_item_view(view)
            if self.selection_mode != 'none':
                # If the deselection makes selection empty, the following call
                # will check allows_empty_selection, and if False, will
                # select the first item. If view happens to be the first item,
                # this will be a reselection, and the user will notice no
                # change, except perhaps a flicker.
                #
                self.check_for_empty_selection()

        if not hold_dispatch:
            self.dispatch('on_selection_change')

class ItemList(FocusBehavior, ListView):
    def __init__(self, **kwargs):
        super(ItemList, self).__init__(**kwargs)
        self.bind(pos=self._draw_outline)
        self.bind(size=self._draw_outline)
        self.bind(focus=self._draw_outline)

    def on_focus(self, instance, value):
        if not isinstance(self.adapter, CustomListAdapter):
            return
        if not value:
            pass
        else:
            if not len(self.adapter.selection):
                item = self.adapter.get_view(0)
                if item:
                    self.adapter.handle_selection(item)

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
        super(ItemList, self).keyboard_on_key_down(window, keycode, text, modifiers)
        if not isinstance(self.adapter, CustomListAdapter):
            # No adapter initialized
            return False
        if len(self.adapter.selection) == 0:
            # No content or empty content
            return False
        if keycode[1] in ("enter", "spacebar"):
            curIndex = self.adapter.selection[0].index
            item = self.adapter.get_view(curIndex)
            self.adapter.handle_selection(item)
            return True
        elif (keycode[1] in ("down", "up", "pagedown", "pageup", "home", "end")
                and not modifiers):
            # Movement keys, but not if modifiers used
            # Handle the normal directional keys, jump up and down in the list
            curIndex = self.adapter.selection[0].index
            pageSkip = int(self.height//(15*1.5))
            dataLen = len(self.adapter.data)-1
            newIndex = {'down': curIndex + 1,
                        'up': curIndex - 1,
                        'pagedown': curIndex + pageSkip,
                        'pageup': curIndex - pageSkip,
                        'home': 0,
                        'end': dataLen}.get(keycode[1])
            if newIndex < 0:
                newIndex = 0
            if newIndex > dataLen:
                newIndex = dataLen
            if dataLen > 0:
                item = self.adapter.get_view(newIndex)
                # hold_dispatch means will not trigger on_selection_change event,
                # to prevent scrolling through from consecutively selecting many
                # items. Flip side is that need to manually call the 'scroll_to'
                # function for proper visibility.
                self.adapter.handle_selection(item, hold_dispatch=True)
                self._scroll_to_item(self.adapter)
            return True
        return False

    def _scroll_to_item(self, adapter):
        # Try to keep selected item in center of ScrollView
        index = self.adapter.selection[-1].index
        pageSkip = int(self.height//(15*1.5))
        targetIndex = index - pageSkip//2
        dataLen = len(adapter.data)-1-pageSkip
        if dataLen > 0:
            targetY = 1.0 - float(targetIndex)/dataLen
            if targetY < 0: targetY = 0.0
            if targetY > 1.0: targetY = 1.0
            self.scroll.scroll_y = targetY

    def set_data(self, datalist):
        item = None
        try:
            oldindex = self.adapter.selection[0].index
            item = self.adapter.get_view(oldindex)
        except IndexError:  # No selection yet
            pass
        except AttributeError:  # Not yet given an adapter
            pass
        self.adapter = CustomListAdapter(data=datalist,
                                   args_converter=self.args_converter,
                                   cls=CustomListItemButton,
                                   selection_mode='single',
                                   allow_empty_selection=False)
        self.adapter.bind(on_selection_change=self._scroll_to_item)
        if item:
            newitem = 0
            for i, data in enumerate(self.adapter.data):
                if data.get('filepath'):
                    if item.filepath == data['filepath']:
                        newitem = self.adapter.get_view(i)
                        break
            if newitem:
                self.adapter.handle_selection(newitem, hold_dispatch=True)
                self._scroll_to_item(self.adapter)

    def get_data(self):
        return self.adapter.data

    def args_converter(self, row_index, an_obj):
        if type(an_obj) == type(SPSong()):
            return {'text': an_obj.title,
                    'size_hint_y': None,
                    'height': 15*1.5,
                    'filepath': an_obj.filepath,
                    'itemtype': u'song',
                    'presentation': u'',
                    'index': row_index}
        elif type(an_obj) == type(SPSet()):
            return {'text': an_obj.name,
                    'size_hint_y': None,
                    'height': 15*1.5,
                    'filepath': an_obj.filepath,
                    'itemtype': u'',
                    'presentation': u'',
                    'index': row_index}
        else:  # If its not a song or set, its a scripture-related object
            return {'text': an_obj['name'],
                    'size_hint_y': None,
                    'height': 15*1.5,
                    'filepath': an_obj.get('filepath', u''),
                    'itemtype': an_obj.get('itemtype', u''),
                    'presentation': an_obj.get('presentation', u''),
                    'index': row_index}
