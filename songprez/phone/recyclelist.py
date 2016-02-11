#!/usr/bin/env python
import kivy
# kivy.require('1.9.0')
from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.uix.scrollview import ScrollView
from kivy.uix.listview import ListItemButton, ListView
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.adapters.listadapter import ListAdapter
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.widget import Widget
from kivy.graphics import Color, Line
from kivy.uix.selectableview import SelectableView
from kivy.properties import StringProperty, ObjectProperty, ListProperty
from .iconfont import iconfont
from kivy.garden.recycleview import RecycleViewMixin, LayoutChangeException

Builder.load_string("""
<ListItem>:
    index: 0
    titletext: ''
    subtitletext: ''
    summarytext: []
    rv: None

    topbar: topbar
    bottombar: bottombar
    title: title
    expand: expand
    summary: summary
    edit: edit
    delete: delete
    orientation: 'vertical'
    size_hint_y: None
    padding: 0, '5dp', 0, '5dp'
    canvas:
        Color:
            rgba: (.25, .25, .25, 1) if self.index % 2 else (.125, .125, .125, 1)
        RoundedRectangle:
            size: self.size
            pos: self.pos
            radius: 5,
        Color:
            rgba: 0, 0, 0, 1
        Line:
            rounded_rectangle: [self.pos[0], self.pos[1], self.size[0], self.size[1], 5]
    BoxLayout:
        id: topbar
        orientation: 'horizontal'
        padding: 10, 0, '32dp', 0
        size_hint_y: None
        height: title.height
        Label:
            id: title
            size_hint_y: None
            height: self.texture_size[1]
            halign: 'left'
            text_size: self.width, None
            text: root.titletext
            shorten: True
            shorten_from: 'right'
            font_size: app.ui_fs_main
        Label:
            id: expand
            size_hint_x: None
            width: app.buttonsize
            font_size: app.ui_fs_button
            markup: True
    BoxLayout:
        id: bottombar
        orientation: 'horizontal'
        padding: 40, 0, '32dp', 0
        size_hint_y: None
        height: max(summary.height, sidebar.height)
        BoxLayout:
            id: summary
            orientation: 'vertical'
            size_hint_y: None
            height: 0  # Initial value, this is set later
        BoxLayout:
            id: sidebar
            orientation: 'vertical'
            size_hint_x: None
            width: app.buttonsize
            size_hint_y: None
            height: summary.height
            Label:
                id: edit
                markup: True
                size_hint_y: None
                font_size: app.ui_fs_button
            Label:
                id: delete
                markup: True
                size_hint_y: None
                font_size: app.ui_fs_button
            Widget:

<SummaryLine>:
    size_hint_y: None
    font_size: app.ui_fs_detail
    height: 0 if not self.text else self.texture_size[1]
    halign: 'left'
    text_size: self.width, None
    pos_hint: {'top': 0}
    shorten: True
    shorten_from: 'right'
    markup: True
""")


class SummaryLine(Label):
    pass


class ListItem(SelectableView, RecycleViewMixin, BoxLayout):
    titletext = StringProperty('')
    subtitletext = StringProperty('')
    summarytext = ListProperty([])
    rv = ObjectProperty(None)

    def refresh_view_attrs(self, rv, data):
        self.rv = rv
        super(ListItem, self).refresh_view_attrs(rv, data)

    def refresh_view_layout(self, rv, index, pos, size, viewport):
        super(ListItem, self).refresh_view_layout(rv, index, pos, size, viewport)
        self.is_selected = False
        self.summary.clear_widgets()
        self.edit.text = ''
        self.edit.height = 0
        self.delete.text = ''
        self.delete.height = 0
        self.expand.text = iconfont('expand')
        self.summary.height = 0

    def on_touch_down(self, touch):
        if self.topbar.collide_point(*touch.pos) or self.summary.collide_point(*touch.pos):
            self.is_selected = not self.is_selected
            for i, d in enumerate(self.rv.data):
                if d.get('index', None) == self.index:
                    app = App.get_running_app()
                    if self.is_selected:
                        viewclass = 'ListItemWithSummary'
                        summaryheight = app.ui_fs_detail*len(self.summarytext)*1.5
                        if summaryheight < 2*app.buttonsize:
                            summaryheight = 2*app.buttonsize
                        h = (app.ui_fs_main*1.5 
                                + summaryheight
                                + self.padding[1] + self.padding[3])
                    elif self.subtitletext:
                        viewclass = 'ListItemWithSubTitle'
                        h = (app.ui_fs_main*1.5 + app.ui_fs_detail*1*1.5
                                + self.padding[1] + self.padding[3])
                    else:
                        viewclass = 'ListItem'
                        h = (app.ui_fs_main*1.5
                                + self.padding[1] + self.padding[3])
                    self.rv.data[i]['viewclass'] = viewclass
                    self.rv.data[i]['height'] = h
                    self.rv.adapter.views.pop(self.index)
                    self.rv.ask_refresh_all()
            return True
        return super(ListItem, self).on_touch_down(touch)

class ListItemWithSubTitle(ListItem):
    def refresh_view_layout(self, rv, index, pos, size, viewport):
        super(ListItemWithSubTitle, self).refresh_view_layout(rv, index, pos, size, viewport)
        self.summary.add_widget(SummaryLine(text=self.subtitletext))
        for c in self.summary.children:
            c.texture_update()
            self.summary.height += c.height
        self.edit.text = ''
        self.edit.height = 0
        self.delete.text = ''
        self.delete.height = 0
        self.expand.text = iconfont('expand')

class ListItemWithSummary(ListItem):
    def refresh_view_layout(self, rv, index, pos, size, viewport):
        super(ListItemWithSummary, self).refresh_view_layout(rv, index, pos, size, viewport)
        self.is_selected = True
        app = App.get_running_app()
        lines = self.summarytext
        self.summary.clear_widgets()
        for l in lines:
            self.summary.add_widget(SummaryLine(text=l))
        self.summary.height = 0
        for c in self.summary.children:
            c.texture_update()
            self.summary.height += c.height
        if self.summary.height < 2*app.buttonsize:
            spacer = 2*app.buttonsize - self.summary.height
            self.summary.add_widget(Widget(size_hint_y=None, height=spacer))
            self.summary.height = 2*app.buttonsize
        self.edit.text = iconfont('edit')
        self.edit.height = app.buttonsize
        self.delete.text = iconfont('delete')
        self.delete.height = app.buttonsize
        self.expand.text = iconfont('collapse')
