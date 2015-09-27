#!/usr/bin/env python
import kivy
# kivy.require('1.9.0')
from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager
from kivy.properties import ObjectProperty
from .misc import SingleLineTextInput, ButtonGridLayout, LyricPreview

Builder.load_string("""
#:import sla kivy.adapters.listadapter
#:import ListItemButton kivy.uix.listview.ListItemButton
<MinSearch>:
    _resultgrid: resultgrid.__self__
    orientation: "horizontal"
    SingleLineTextInput:
        id: txt
        size_hint: 0.3, None
        on_action: root.search(txt.text)
    ScrollView:
        do_scroll_y: False
        do_scroll_x: True
        size_hint: 0.7, None
        height: txt.height
        scroll_type: ["bars", "content"]
        bar_width: 8
        effect_cls: "ScrollEffect"
        GridLayout:
            id: resultgrid
            rows: 1
            size_hint_x: None
            size_hint_y: None
            width: self.minimum_width
            col_default_width: 100
<SearchLine>
    # When used, must include a base object pointing to the top-level
    # search widget
    size_hint_y: None
    height: txt.height
    orientation: "horizontal"
    SingleLineTextInput:
        id: txt
        on_action: root.base.search(txt.text)
    ButtonGridLayout:
        rows: 1
        MyButton:
            text: "Search"
            _name: "search"
            on_press: root.base.search(txt.text)
<SearchResults@BoxLayout>
    orientation: "vertical"
    GridLayout:
        cols: 2
        size_hint: 1, None
        CheckBox:
            size_hint: None, 1
            size: self.size[1], self.size[1]
        Label:
            id: lbl
            text_size: self.size
            halign: 'left'
            valign: 'middle'
            text: "First option"
        CheckBox:
            size_hint: None, 1
            size: self.size[1], self.size[1]
        Label:
            text_size: self.size
            halign: 'left'
            valign: 'middle'
            text: "Second option"
        CheckBox:
            size_hint: None, 1
            size: self.size[1], self.size[1]
        Label:
            text_size: self.size
            halign: 'left'
            valign: 'middle'
            text: "Third option"
    ListView:
        size_hint: (1,1)
        adapter:
            sla.ListAdapter(data=[], cls=ListItemButton)
        item_strings: ["Song " + str(i) for i in range(60)]
        allow_empty_selection: False
<MaxSearch>: # Also used for landscape mode in phone
    orientation: "vertical"
    SearchLine:
        base: root.__self__
        id: searchline
    BoxLayout:
        orientation: "horizontal"
        size_hint_y: None
        height: self.parent.height - searchline.height
        SearchResults:
        LyricPreview:
            base: root.__self__
<PhoneSearch>
    primaryinf: primaryinf
    transition: NoTransition()
    Screen:
        name: "portrait"
        BoxLayout:
            orientation: "vertical"
            SearchLine:
                base: root.__self__
                id: searchline
            Accordion:
                size_hint_y: None
                height: self.parent.height - searchline.height
                orientation: "horizontal"
                AccordionItem:
                    id: primaryinf
                    title: "Search Screen"
                    collapse: False
                    SearchResults:
                AccordionItem:
                    title: "Song Preview"
                    LyricPreview:
                        base: root.__self__
    Screen:
        name: "landscape"
        MaxSearch:
""")


class SearchLine(BoxLayout):
    exceptiontext = "The SearchLine widget needs its' parent to define "\
                    +"a base object which handles SearchLine's buttons"

    def search(self, text):
        raise Exception(self.exceptiontext)
    
    def previous(self):
        raise Exception(self.exceptiontext)

    def next(self):
        raise Exception(self.exceptiontext)

    def add(self):
        raise Exception(self.exceptiontext)

class SearchWidget():
    def search(self, text):
        print("ACTION: Do a search for the string", text)

    def previous(self):
        print("ACTION: Select previous song in search view")

    def next(self):
        print("ACTION: Select next song in search view")

    def add(self):
        print("ACTION: Add currently selected (by search) song to current list")

class MinSearch(BoxLayout, SearchWidget):
    _resultgrid = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(MinSearch, self).__init__(**kwargs)
        Clock.schedule_once(self._finish_init)

    def _finish_init(self, dt):
        for i in range(1, 20):
            self.add_result("Result Number " + str(i))
    
    def on_pos(self, instance, value):
        focus = False if value[1] < 0.0 else True
        for widget in self.walk(restrict=True):
            if isinstance(widget, FocusBehavior):
                widget.is_focusable = focus

    def add_result(self, name):
        result = Label(size_hint=(None, None), text=name, multiline=False)
        result.texture_update()
        result.width = result.texture_size[0] + 20
        result.height = result.texture_size[1]
        result.texture_update()
        self._resultgrid.add_widget(result)


class MaxSearch(BoxLayout, SearchWidget):
    def __init__(self, **kwargs):
        super(MaxSearch, self).__init__(**kwargs)
        Clock.schedule_once(self._finish_init)

    def _finish_init(self, dt):
        # Walk widget tree to find the ButtonGridLayout in the LyricPreview
        for widget in self.walk(restrict=True):
            if isinstance(widget, LyricPreview):
                for w in widget.walk(restrict=True):
                    if isinstance(w, ButtonGridLayout):
                        gridlayout = w
        for b in gridlayout.children:
            b._name = "search" + b._name


class PhoneSearch(ScreenManager, SearchWidget):
    primaryinf = ObjectProperty(None)
    _sm = ObjectProperty(None)
    def __init__(self, **kwargs):
        super(PhoneSearch, self).__init__(**kwargs)
        Clock.schedule_once(self._finish_init)

    def _finish_init(self, dt):
        app = App.get_running_app()
        app.bind(landscape=self._landscape)
        # Walk widget tree to find the ButtonGridLayout in the LyricPreview
        for widget in self.walk(restrict=True):
            if isinstance(widget, LyricPreview):
                for w in widget.walk(restrict=True):
                    if isinstance(w, ButtonGridLayout):
                        gridlayout = w
        for b in gridlayout.children:
            b._name = "search" + b._name

    def _landscape(self, instance, value):
        if value:
            self.current = "landscape"
        else:
            self.current = "portrait"
