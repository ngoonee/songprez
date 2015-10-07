#!/usr/bin/env python
import kivy
# kivy.require('1.9.0')
from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.uix.scrollview import ScrollView
from kivy.uix.listview import ListItemButton, ListView
from kivy.adapters.listadapter import ListAdapter

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

Builder.load_string("""
<CustomListItemButton>:
    font_name: 'songprez/fonts/NSimSun.ttf'
<ListView>:
    container: container
    ScrollView:
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
    filepath = StringProperty('')

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

class ItemList(ListView):
    def set_data(self, datalist):
        self.adapter = CustomListAdapter(data=datalist,
                                   args_converter=self.args_converter,
                                   cls=CustomListItemButton,
                                   selection_mode='single',
                                   allow_empty_selection=False)

    def args_converter(self, row_index, an_obj):
        return {'text': an_obj[1],
                'size_hint_y': None,
                'height': 15*1.5,
                'filepath': an_obj[0]}
