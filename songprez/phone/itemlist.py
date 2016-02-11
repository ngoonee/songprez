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
from kivy.uix.selectableview import SelectableView
from .iconfont import iconfont

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
<CustomListItemView>:
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
    height: topbar.height + bottombar.height + self.padding[1] + self.padding[3]
    titletext: ''
    subtitletext: ''
    summarytext: []
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
<MyListView>:
""")


class SummaryLine(Label):
    pass


class CustomListItemView(SelectableView, BoxLayout):
    titletext = StringProperty('')
    subtitletext = StringProperty('')
    summarytext = ListProperty([])
    def __init__(self, **kwargs):
        super(CustomListItemView, self).__init__(**kwargs)
        self.register_event_type('on_release')
        Clock.schedule_once(self._finish_init)

    def _finish_init(self, dt):
        # Need to initialize how the view looks once
        if self.is_selected:
            self.select()
        else:
            self.deselect()

    def on_touch_down(self, touch):
        if self.topbar.collide_point(*touch.pos) or self.summary.collide_point(*touch.pos):
            self.dispatch('on_release')
            return True
        return super(CustomListItemView, self).on_touch_down(touch)

    def on_release(self):
        pass
    
    def select(self):
        app = App.get_running_app()
        lines = self.summarytext.split('\n')
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
    
    def deselect(self):
        self.summary.clear_widgets()
        self.summary.add_widget(SummaryLine(text=self.subtitletext))
        self.summary.height = 0
        for c in self.summary.children:
            c.texture_update()
            self.summary.height += c.height
        self.edit.text = ''
        self.edit.height = 0
        self.delete.text = ''
        self.delete.height = 0
        self.expand.text = iconfont('expand')


def song_args_converter(row_index, an_obj):
    title = an_obj.title
    subtitle = []
    for t in (an_obj.author, an_obj.aka, an_obj.key_line):
        if t:
            subtitle.append(t)
    subtitle = " | ".join(subtitle)
    text = an_obj.words.split('\n')
    text = [t for t in text if t != '' and not (t[0] == '[' and t[-1] == ']')]
    summary = text[0:4]
    return {'titletext': title,
            'subtitletext': subtitle,
            'summarytext': summary}


class MyListView(ListView):
    def __init__(self, **kwargs):
        super(MyListView, self).__init__(**kwargs)

    def _scroll(self, scroll_y):
        if self.row_height is None:
            return
        self._scroll_y = scroll_y
        scroll_y = 1 - min(1, max(scroll_y, 0))
        container = self.container
        mstart = (container.height - self.height) * scroll_y
        mend = mstart + self.height

        # convert distance to index
        rh = self.row_height
        istart = int(ceil(mstart / rh))
        iend = int(floor(mend / rh))
        real_h = 0
        sizes = self._sizes
        i = 0
        while real_h < mstart:
            real_h += sizes[i] if sizes.get(i) else rh
            i += 1
        istart = i + 1
        i += 1
        while real_h < mend:
            real_h += sizes[i] if sizes.get(i) else rh
            i+= 1
        iend = i

        istart = max(0, istart - 1)
        iend = max(0, iend - 1)

        if istart < self._wstart:
            rstart = max(0, istart - 10)
            self.populate(rstart, iend)
            self._wstart = rstart
            self._wend = iend
        elif iend > self._wend:
            self.populate(istart, iend + 10)
            self._wstart = istart
            self._wend = iend + 10

    def _update_sizes(self, instance, value):
        self._sizes[instance.index] = value
        self.populate()

    def populate(self, istart=None, iend=None):
        container = self.container
        sizes = self._sizes
        rh = self.row_height

        # ensure we know what we want to show
        if istart is None:
            istart = self._wstart
            iend = self._wend

        # clear the view, remove bindings
        for w in container.children:
            w.unbind(height=self._update_sizes)
        container.clear_widgets()

        # guess only ?
        if iend is not None and iend != -1:

            # fill with a "padding"
            fh = 0
            for x in range(istart):
                fh += sizes[x] if x in sizes else rh
            container.add_widget(Widget(size_hint_y=None, height=fh))

            # now fill with real item_view
            index = istart
            count = 0
            while index <= iend:
                item_view = self.adapter.get_view(index)
                index += 1
                if item_view is None:
                    continue
                sizes[index-1] = item_view.height
                item_view.fbind('height', self._update_sizes)
                container.add_widget(item_view)
                count += 1
            if count:
                self.row_height = sum(self._sizes.values()) / len(self._sizes)
                container.height = sum(self._sizes.values()) \
                        + (self.adapter.get_count() - len(self._sizes)) * self.row_height
        else:
            available_height = self.height
            real_height = 0
            index = self._index
            count = 0
            while available_height > 0:
                item_view = self.adapter.get_view(index)
                if item_view is None:
                    break
                sizes[index] = item_view.height
                item_view.fbind('height', self._update_sizes)
                index += 1
                count += 1
                container.add_widget(item_view)
                available_height -= item_view.height
                real_height += item_view.height

            # extrapolate the full size of the container from the size
            # of view instances in the adapter
            if count:
                if self.row_height is None:
                    self.row_height = sum(self._sizes.values()) / len(self._sizes)
                container.height = sum(self._sizes.values()) \
                        + (self.adapter.get_count() - len(self._sizes)) * self.row_height
