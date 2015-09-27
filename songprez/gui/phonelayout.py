#!/usr/bin/env python
import kivy
# kivy.require('1.9.0')
from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.uix.screenmanager import ScreenManager
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty
from .misc import set_initial_focus

Builder.load_string("""
#:import NoTransition kivy.uix.screenmanager.NoTransition

<PhoneLayout>
    _sm: self.__self__
    _editprimary: phoneedit.primaryinf
    _searchprimary: search.primaryinf
    transition: NoTransition()
    Screen:
        name: "main"
    Screen:
        name: "list"
        MinSetList:
    Screen:
        name: "edit"
        PhoneSongEdit:
            id: phoneedit
    Screen:
        name: "settings"
        Settings:
    Screen:
        name: "browse"
        MaxBrowse:
    Screen:
        name: "search"
        PhoneSearch:
            id: search
""")


class PhoneLayout(ScreenManager):
    _sm = ObjectProperty(None)
    _state = StringProperty("main")
    _p = ObjectProperty(None)
    _active = BooleanProperty(False)
    _editprimary = ObjectProperty(None)
    _base = ObjectProperty(None)

    def __init__(self, base, **kwargs):
        super(PhoneLayout, self).__init__(**kwargs)
        self._base = base
        Clock.schedule_once(self._finish_init)

    def _finish_init(self, dt):
        self.bind(size=self._resize)
        self._base.bind(_state=self._monitor_state)

    def _monitor_state(self, instance, value):
        self._state = value
        self._resize(instance, self.size)

    def _resize(self, instance, new_size):
        w, h = new_size
        if self._active:
            self._p.size = (w, h)
            self._p.pos = (0, 0)

    def updateState(self, targetState):
        app = App.get_running_app()
        page = {"main": "main",
                "list": "list",
                "edit": "edit",
                "settings": "settings",
                "browse": "browse",
                "search": "search"}.get(targetState)
        if page == "edit":
            self._editprimary.collapse = False
        if page == "search":
            self._searchprimary.collapse = False
        if page is not None:
            self.current = page
        set_initial_focus(self._sm.current_screen)

    def add_present_widget(self, widget):
        self.get_screen("main").add_widget(widget)
        self._p = widget
        self._active = True

    def remove_present_widget(self, widget):
        self.get_screen("main").remove_widget(widget)
        self._active = False
