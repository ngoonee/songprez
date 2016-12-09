#!/usr/bin/env python
import kivy
kivy.require('1.9.1')
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.stencilview import StencilView
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import StringProperty, ObjectProperty, ListProperty
from kivy.properties import NumericProperty, BooleanProperty, DictProperty
from kivy.metrics import dp
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivymd.theming import ThemableBehavior
from kivymd.list import TwoLineListItem

Builder.load_string('''
<MDRecycleView>:
    SelectableRecycleBoxLayout:
        default_size: None, None
        default_size_hint: 1, None
        size_hint_y: None
        height: self.minimum_height if self.minimum_height else self._min_list_height
        padding: 0, self._list_vertical_padding
        orientation: 'vertical'

<ListItem2>:
    title_fs: app.ui_fs_main
    detail_fs: app.ui_fs_detail
    button_fs: app.ui_fs_button
    buttonsize: app.buttonsize

    title: title
    canvas.before:
        Color:
            rgba: self.theme_cls.primary_color if self.selected else (0, 0, 0, 0)
        Rectangle:
            pos: self.pos
            size: self.size
        Color:
            rgba: self.theme_cls.primary_color if self.selected else (0, 0, 0, 0)
        Line:
            rounded_rectangle: [self.pos[0], self.pos[1], self.size[0], self.size[1], 10]
    Label:
        id: title
        pos: root.pos
        halign: 'left'
        valign: 'middle'
        text: root.text
        text_size: root.size
        shorten: True
        shorten_from: 'right'
        font_size: root.title_fs
<ScanItem>:
    canvas.before:
        Color:
            rgba: self.theme_cls.primary_color if self.selected else (0, 0, 0, 0)
        Rectangle:
            pos: self.pos
            size: self.size
''')


class MDRecycleView(ThemableBehavior, RecycleView):
    selection = StringProperty([])

class SelectableRecycleBoxLayout(LayoutSelectionBehavior,
                                 RecycleBoxLayout):
    ''' Adds selection and focus behaviour to the view. '''
    _min_list_height = dp(16)
    _list_vertical_padding = dp(8)


class ScanItem(RecycleDataViewBehavior, TwoLineListItem):
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)
    def __init__(self, **kwargs):
        super(ScanItem, self).__init__(**kwargs)
        self.divider = 'Inset'

    def refresh_view_attrs(self, rv, index, data):
        ''' Catch and handle the view changes '''
        self.index = index
        return super(ScanItem, self).refresh_view_attrs(
            rv, index, data)

    def on_touch_down(self, touch):
        ''' Add selection on touch down '''
        handled = super(ScanItem, self).on_touch_down(touch)
        selected = False
        if self.collide_point(*touch.pos) and self.selectable:
            selected = self.parent.select_with_touch(self.index, touch)
        return handled or selected

    def apply_selection(self, rv, index, is_selected):
        ''' Respond to the selection of items in the view. '''
        self.selected = is_selected
        if is_selected:
            rv.selection = rv.data[index]['secondary_text']


class ListItem2(ThemableBehavior, RecycleDataViewBehavior, FloatLayout, StencilView):
    ''' Add selection support to the Label '''
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

    text = StringProperty('')
    #subtitletext = StringProperty('')
    #summarytext = ListProperty([])
    #rv = ObjectProperty(None)
    #expand_angle = NumericProperty(0)
    #button_opacity = NumericProperty(0)
    #set_edit = BooleanProperty(False)
    #relpath = StringProperty('')
    #backcolor = ListProperty([0, 0, 0, 0])
    #_summary = ListProperty([])

    def __init__(self, **kwargs):
        super(ListItem2, self).__init__(**kwargs)

    def refresh_view_attrs(self, rv, index, data):
        ''' Catch and handle the view changes '''
        self.index = index
        return super(ListItem2, self).refresh_view_attrs(
            rv, index, data)

    def on_touch_down(self, touch):
        ''' Add selection on touch down '''
        if super(ListItem2, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        ''' Respond to the selection of items in the view. '''
        self.selected = is_selected
        print(self.size)
        print(self.title.size)
        if is_selected:
            print("selection changed to {0}".format(rv.data[index]))
        else:
            print("selection removed for {0}".format(rv.data[index]))
