#!/usr/bin/env python
import kivy
# kivy.require('1.9.0')
from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import StringProperty, ObjectProperty, BooleanProperty
from .misc import set_initial_focus


Builder.load_string("""
#:import NoTransition kivy.uix.screenmanager.NoTransition

<TabletLayout>
    _sm: sm.__self__
    ScreenManager:
        id: sm
        size_hint: None, None
        transition: NoTransition()
        Screen:
            name: "minlist"
            MinSetList:
        Screen:
            name: "maxlist"
            MaxSetList:
        Screen:
            name: "minedit"
            MinSongEdit:
        Screen:
            name: "maxedit"
            MaxSongEdit:
        Screen:
            name: "settings"
        Screen:
            name: "minbrowse"
            MinBrowse:
        Screen:
            name: "maxbrowse"
            MaxBrowse:
        Screen:
            name: "search"
            MaxSearch:
        Screen:
            name: "blank"
""")


class TabletLayout(FloatLayout):
    _state = StringProperty("main")
    _p = ObjectProperty(None)
    _sm = ObjectProperty(None)
    _active = BooleanProperty(False)
    _base = ObjectProperty(None)

    def __init__(self, base, **kwargs):
        super(TabletLayout, self).__init__(**kwargs)
        self._base = base
        Clock.schedule_once(self._finish_init)

    def _finish_init(self, dt):
        self.bind(size=self._resize)
        self._base.bind(_state=self._monitor_state)

    def _monitor_state(self, instance, value):
        self._state = value
        self._resize(instance, self.size)

    def _resize(self, instance, new_size):
        if not self._active:
            return
        w, h = new_size
        app = App.get_running_app()
        ratio = 0.7 if app.minimal else 0.5
        if app.landscape:
            self._sm.size = (w * (1-ratio), h)
        else:
            self._sm.size = (w, h * (1-ratio))
        if (self._state in ("main", "transpose") or
                (self._state is "search" and app.minimal)):
            # Maximize the present screen, both transpose and minimal search
            # will float above it
            self._p.size = (w, h)
            self._p.pos = (0, 0)
            self._sm.pos = (w, 0) if app.landscape else (0, h)
        elif ((self._state == "edit" and not app.minimal) or
              (self._state == "settings")):
            # Edit screen is full screen, so need to set the side bar widget
            # to maximum and hide the present screen. Same for settings screen
            self._p.pos = (w, 0) if app.landscape else (0, h)
            self._sm.size = (w, h)
            self._sm.pos = (0, 0)
        else:
            # Calculate (based on ratio) the relative sizes of the present
            # screen and the side bar
            self._p.size = (w * ratio, h) if app.landscape else (w, h * ratio)
            self._p.pos = (0, 0) if app.landscape else (0, h * (1-ratio))
            self._sm.pos = (w * ratio, 0) if app.landscape else (0, 0)

    def updateState(self, targetState):
        app = App.get_running_app()
        if app.minimal:
            page = {"list": "minlist",
                    "edit": "minedit",
                    "settings": "settings",
                    "browse": "minbrowse"}.get(targetState)
        else:
            page = {"list": "maxlist",
                    "edit": "maxedit",
                    "settings": "settings",
                    "browse": "maxbrowse",
                    "search": "search"}.get(targetState)
        if page is not None:
            self._sm.current = page
        else:
            self._sm.current = "blank"
        set_initial_focus(self._sm.current_screen)

    def add_present_widget(self, widget):
        self.add_widget(widget, len(self._sm.children))
        self._p = widget
        self._active = True

    def remove_present_widget(self, widget):
        self.remove_widget(widget)
        self._active = False
