#!/usr/bin/env python
import kivy
kivy.require('1.9.1')
from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.uix.stencilview import StencilView
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import StringProperty, ObjectProperty, ListProperty
from kivy.properties import NumericProperty, BooleanProperty, DictProperty
from kivy.metrics import dp
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivymd.theming import ThemableBehavior
from kivymd.list import TwoLineListItem
from kivymd.label import MDLabel
from kivymd.backgroundcolorbehavior import SpecificBackgroundColorBehavior
from functools import partial

Builder.load_string('''
#:import md_icons kivymd.icon_definitions.md_icons
<MDRecycleView>:
    layout: layout
    key_viewclass: 'viewclass'
    SelectableRecycleBoxLayout:
        id: layout
        default_size: None, None
        default_size_hint: 1, None
        size_hint_y: None
        key_size: 's'
        height: self.minimum_height if self.minimum_height else self._min_list_height
        padding: 0, self._list_vertical_padding
        orientation: 'vertical'

<SelectableItem>:
    canvas:
        Color:
            rgba: self.theme_cls.primary_color if self.selected else (1, 1, 1, 0)
        Rectangle:
            pos: self.x + self.width - dp(8), self.y
            size: dp(8), self.height
    theme_text_color: 'Primary'
    secondary_theme_text_color: 'Primary'

<SingleLine@MDLabel>:
    size_hint: None, None
    height: self.texture_size[1]
    halign: 'left'
    valign: 'middle'
    shorten: True
    shorten_from: 'right'
    theme_text_color: root.parent.theme_text_color
    x: root.parent.x + dp(16)
    width: root.parent.x + root.parent.width - dp(16) - dp(48)

<BasicItem>:
    title: title
    subtitle: subtitle
    #height: dp(60) if self.subtitle_text else dp(40)
    canvas:
        Color:
            rgba: self.theme_cls.divider_color
        Line:
            points: (root.x+dp(16), root.y+1, root.x+self.width-dp(16), root.y+1)
    SingleLine:
        id: title
        text: root.title_text
        font_style: 'Subhead'
        y: root.y + (dp(31) if root.subtitle_text else dp(11))
    SingleLine:
        id: subtitle
        text: root.subtitle_text
        font_style: 'Body1'
        y: root.y + dp(10)

<CountItem>:
    num: num
    MDLabel:
        id: num
        size_hint: None, None
        size: dp(24), dp(24)
        font_style: 'Icon'
        text: u"{}".format(md_icons[root.icon]) if root.icon else u""
        theme_text_color: root.theme_text_color
        x: root.x + root.width - dp(16) - dp(24)
        y: root.y + (dp(18) if root.subtitle_text else dp(8))

<ScanItem>:
    ripple_alpha: 0
    height: dp(60)
    divider: 'Inset'
''')


class MDRecycleView(ThemableBehavior, RecycleView):
    selection = StringProperty([])
    select_action = ObjectProperty(None)
    long_press_action = ObjectProperty(None)


class SelectableRecycleBoxLayout(LayoutSelectionBehavior,
                                 RecycleBoxLayout):
    _min_list_height = dp(16)
    _list_vertical_padding = dp(8)
    multiselect = False
    touch_multiselect = False


class SelectableItem(RecycleDataViewBehavior):
    ''' Adds selection and focus behaviour to the view. '''
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)
    rv = ObjectProperty(None)

    def refresh_view_attrs(self, rv, index, data):
        self.index = index
        self.rv = rv
        return super(SelectableItem, self).refresh_view_attrs(
            rv, index, data)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos) and self.selectable:
            self.create_clock(touch)
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        ''' Respond to the selection of items in the view. '''
        self.selected = is_selected

    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos) and self.selectable:
            self.delete_clock(touch)
            if self.rv.primary_action:
                self.rv.primary_action(self.rv.data[self.index])

    def create_clock(self, touch):
        callback = partial(self.long_press, touch)
        Clock.schedule_once(callback, 0.5)
        touch.ud['event'] = callback

    def delete_clock(self, touch):
        Clock.unschedule(touch.ud['event'])

    def long_press(self, touch, dt):
        if self.rv.long_press_action:
            self.rv.long_press_action(self.rv.data[self.index], self)


class BasicItem(SelectableItem, ThemableBehavior, FloatLayout,
                     StencilView
                     ):
    title_text = StringProperty('')
    subtitle_text = StringProperty('')

    def apply_selection(self, rv, index, is_selected):
        super(BasicItem, self).apply_selection(rv, index, is_selected)
        if is_selected:
            rv.selection = rv.data[index].get('relpath', u'')


class CountItem(BasicItem):
    num_items = NumericProperty(0)
    icon = StringProperty(u"")

    def on_num_items(self, instance, value):
        if value == 0:
            self.icon = u""
        elif value < 10:
            self.icon = u"numeric-" + str(value) + u"-box"
        else:
            self.icon = u"numeric-9-plus-box"


class ScanItem(SelectableItem, TwoLineListItem):
    def apply_selection(self, rv, index, is_selected):
        ''' Respond to the selection of items in the view. '''
        super(ScanItem, self).apply_selection(rv, index, is_selected)
        if is_selected:
            rv.selection = rv.data[index]['secondary_text']
