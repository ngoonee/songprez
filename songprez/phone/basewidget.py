#!/usr/bin/env python
import kivy
# kivy.require('1.9.1')
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.app import App
from kivy.properties import BooleanProperty
from kivy.uix.screenmanager import ScreenManager
from kivy.uix.boxlayout import BoxLayout
from .mainscreen import MainScreen
from .presentscreen import PresentScreen

Builder.load_string("""
#:import FallOutTransition kivy.uix.screenmanager.FallOutTransition
#:import NoTransition kivy.uix.screenmanager.NoTransition
#:import SwapTransition kivy.uix.screenmanager.SwapTransition
<Widget>:
    # Use same font throughout. Needed because SlideElement is a BoxLayout and
    # needs to have a font_name.
    font_name: 'songprez/fonts/NotoSansCJK-Regular.ttc'
    font_size: '24sp'
    # Sometime between revision 700 (g048821a) and 828 (g132be35) this was made
    # to work. Before that we needed to apply font_size separately to label and
    # TextInput.
<BaseWidget>:
    orientation: "vertical"
    sm: sm
    title: title
    Label:
        id: title
        size_hint_y: None
        height: '48dp'
        markup: True
    ScreenManager:
        id: sm
        Screen:
            name: 'preload'
        MainScreen:
            name: 'main'
        PresentScreen:
            name: 'present'
        Screen:
            name: 'sets'
        Screen:
            name: 'songs'
        Screen:
            name: 'search'
        Screen:
            name: 'scripture'
        Screen:
            name: 'editset'
        Screen:
            name: 'editsong'
        Screen:
            name: 'settings'
""")


class BaseWidget(BoxLayout):
    def __init__(self, **kwargs):
        super(BaseWidget, self).__init__(**kwargs)
        self.sm.bind(current=self._change_title)
        self.sm.current = 'main'

    def _change_title(self, instance, data):
        title = self.title
        if data == 'main':
            title.text = 'SongPrez'
        elif data == 'sets':
            title.text = u'Sets [font=MaterialDesignIcons]\uf423[/font]'
        elif data == 'songs':
            title.text = u'Songs [font=MaterialDesignIcons]\uf30e[/font]'
        elif data == 'present':
            title.text = u'Present [font=MaterialDesignIcons]\uf518[/font]'
        elif data == 'search':
            title.text = u'Search [font=MaterialDesignIcons]\uf43b[/font]'
        elif data == 'scripture':
            title.text = u'Scripture [font=MaterialDesignIcons]\uf5d3[/font]'
        elif data == 'settings':
            title.text = u'Settings [font=MaterialDesignIcons]\uf582[/font]'
        elif data == 'editset':
            title.text = u'''[font=MaterialDesignIcons]\uf4da[\font]
                             Edit Set
                             [font=MaterialDesignIcons]\uf423[/font]'''
        elif data == 'editsong':
            title.text = u'''[font=MaterialDesignIcons]\uf4da[\font]
                             Edit Song
                             [font=MaterialDesignIcons]\uf518[/font]'''
            

    def on_connection(self, connection):
        print('connected successfully')
        app = App.get_running_app()
        app.sendMessage = connection.sendMessage

    def to_screen(self, name):
        self.sm.current = name

    def _running(self):
        app = App.get_running_app()
        app._control_loaded()

    def _song_list(self, listofsong):
        pass

    def _set_list(self, listofset):
        pass

    def _search_list(self, listofsearch):
        pass

    def _scripture_list(self, listofscripture):
        pass

    def _edit_item(self, itemtype, item):
        pass

    def _edit_set(self, item):
        pass
