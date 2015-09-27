#!/usr/bin/env python
import kivy
# kivy.require('1.9.0')
from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.properties import ListProperty, ObjectProperty, DictProperty
from kivy.properties import StringProperty
from kivy.uix.button import Button
from kivy.uix.stencilview import StencilView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.carousel import Carousel
from .transposebar import TransposeBar
from .mainmenu import MainMenu
from .list import MinSetList, MaxSetList
from .edit import MinSongEdit, MaxSongEdit, PhoneSongEdit
from .browse import MinBrowse, MaxBrowse
from .search import MinSearch, MaxSearch, PhoneSearch
from .tabletlayout import TabletLayout
from .phonelayout import PhoneLayout
from .misc import set_initial_focus

Builder.load_string("""
<BaseWidget>:
    base: base.__self__
    BoxLayout:
        orientation: "horizontal" if app.landscape else "vertical"
        StencilView:
            size: self.size
            RelativeLayout:
                size: self.parent.size
                pos: self.parent.pos
                id: base
        MainMenu:

<PresentWidget>:
    base: base
    size_hint: None, None
    RelativeLayout:
        id: base
        size: self.parent.size
        pos: self.parent.pos
""")


class PresentWidget(StencilView):
    pass


class BaseWidget(BoxLayout):
    base = ObjectProperty(None)
    main = ObjectProperty(None)
    _state = StringProperty("main")
    _transposeBar = ObjectProperty(None)
    _minSearchBar = ObjectProperty(None)
    _presentScreen = ObjectProperty(None)
    _presentWidget = ObjectProperty(None)
    _presentBase = ObjectProperty(None)
    _tabletScreen = ObjectProperty(None)
    _phoneScreen = ObjectProperty(None)
    _allowed_transitions = DictProperty(None)
    _stateHistory = ListProperty([])

    def __init__(self, **kwargs):
        super(BaseWidget, self).__init__(**kwargs)
        self._transposeBar = TransposeBar()
        self._minSearchBar = MinSearch(size_hint=(1, None))
        # self._presentScreen = Carousel(size_hint=(1, 1))
        self._presentScreen = Button(text="Song Displayed Here")
        self._presentWidget = PresentWidget()
        self._presentBase = self._presentWidget.base
        self._tabletScreen = TabletLayout(self)
        self._phoneScreen = PhoneLayout(self)
        self._allowed_transitions = {
                "list": ["browse", "search", "edit", "settings"],
                "edit": ["settings"],
                "transpose": ["settings"],
                "settings": [],
                "browse": ["edit", "settings", "search"],
                "search": ["edit", "settings", "browse"],
                "main": ["list", "edit", "browse",
                         "search", "settings", "transpose"]
                }
        Clock.schedule_once(self._finish_init)

    def _finish_init(self, dt):
        self._transposeBar.y = -200  # A hack for putting it off screen
        self._minSearchBar.y = -200
        self._presentBase.add_widget(self._transposeBar)
        self._presentBase.add_widget(self._minSearchBar)
        self._presentBase.add_widget(self._presentScreen,
                                     index=len(self._presentBase.children))
        app = App.get_running_app()
        if app.tablet:
            self.base.add_widget(self._tabletScreen,
                                 index=len(self.base.children))
            self.main = self._tabletScreen
            self._tabletScreen.add_present_widget(self._presentWidget)
        else:
            self.base.add_widget(self._phoneScreen,
                                 index=len(self.base.children))
            self.main = self._phoneScreen
            self._phoneScreen.add_present_widget(self._presentWidget)
        app.bind(tablet=self._monitor_tablet)
        app.bind(minimal=self._monitor_minimal)

    def _monitor_minimal(self, instance, value):
        if self._state == "search":
            self._teardown(self._state)
            self._setup(self._state)
        else:
            self._teardown(self._state)
            self._setup(self._state)

    def _monitor_tablet(self, instance, value):
        app = App.get_running_app()
        self._teardown(self._state)
        if self.main == self._phoneScreen and app.tablet:
            self.base.remove_widget(self._phoneScreen)
            self._phoneScreen.remove_present_widget(self._presentWidget)
            self._tabletScreen.add_present_widget(self._presentWidget)
            self.base.add_widget(self._tabletScreen,
                                 index=len(self.base.children))
            self.main = self._tabletScreen
        elif self.main == self._tabletScreen and not app.tablet:
            self.base.remove_widget(self._tabletScreen)
            self._tabletScreen.remove_present_widget(self._presentWidget)
            self._phoneScreen.add_present_widget(self._presentWidget)
            self.base.add_widget(self._phoneScreen,
                                 index=len(self.base.children))
            self.main = self._phoneScreen
        self._setup(self._state)

    def _advance(self, targetState):
        app = App.get_running_app()
        if self._state == targetState:
            if not app.tablet and targetState == "edit":
                if not self.main._editprimary.collapse:
                    self.main._editprimary.collapse = True
                else:
                    self._back()
            elif (not app.tablet and targetState == "search" and
                    not app.landscape):
                if not self.main._searchprimary.collapse:
                    self.main._searchprimary.collapse = True
                else:
                    self._back()
            else:
                self._back()
        else:
            if targetState in self._allowed_transitions[self._state]:
                self._setButtons(targetState)
                if ((self._state, targetState) not in
                        (("browse", "search"), ("search", "browse"))):
                    self._stateHistory.append(self._state)
                self._teardown(self._state)
                self._state = targetState
                self._setup(targetState)

    def _setButtons(self, targetState):
        app = App.get_running_app()
        for i in app.buttons.keys():
            butName = i.split("menu_")[-1]
            if butName in self._allowed_transitions[targetState]:
                app.buttons[i].disabled = False
                app.buttons[i].state = 'normal'
            elif butName == targetState:
                app.buttons[i].disabled = False
                app.buttons[i].state = 'down'
            else:
                app.buttons[i].disabled = True
                app.buttons[i].state = 'normal'

    def _back(self):
        if len(self._stateHistory) is 0:
            print("Exit this app")
        else:
            self._teardown(self._state)
            returnTo = self._stateHistory.pop()
            self._setButtons(returnTo)
            self._state = returnTo
            self._setup(returnTo)

    def _setup(self, targetState):
        app = App.get_running_app()

        def setup_list():
            self.main.updateState(targetState)

        def setup_edit():
            if app.minimal and app.tablet:
                setup_transpose()
            self.main.updateState(targetState)

        def setup_transpose():
            anim = Animation(y=-self._transposeBar.height, duration=0)
            anim = anim + Animation(y=0, duration=0.1)
            anim.stop(self._transposeBar)
            def transpose_focus(*args):
                set_initial_focus(self._transposeBar)
            if targetState == "transpose":
                anim.bind(on_complete=transpose_focus)
            anim.start(self._transposeBar)

        def setup_settings():
            app.open_settings()
            self.main.updateState(targetState)

        def setup_browse():
            self.main.updateState(targetState)

        def setup_search():
            if app.minimal and app.tablet:
                anim = Animation(y=-self._minSearchBar.height, duration=0)
                anim = anim + Animation(y=0, duration=0.1)
                anim.stop(self._minSearchBar)
                def minsearchfocus(*args):
                    set_initial_focus(self._minSearchBar)
                anim.bind(on_complete=minsearchfocus)
                anim.start(self._minSearchBar)
            self.main.updateState(targetState)

        def setup_main():
            self.main.updateState(targetState)

        {"list": setup_list,
         "edit": setup_edit,
         "transpose": setup_transpose,
         "settings": setup_settings,
         "browse": setup_browse,
         "search": setup_search,
         "main": setup_main}.get(targetState)()

    def _teardown(self, targetState):
        app = App.get_running_app()

        def teardown_list():
            pass

        def teardown_edit():
            teardown_transpose()

        def teardown_transpose():
            if self._transposeBar.height > -self._transposeBar.height:
                anim = Animation(y=-self._transposeBar.height, duration=0.1)
                anim = anim + Animation(y=-app.height, duration=0)
                anim.stop(self._transposeBar)
                anim.start(self._transposeBar)

        def teardown_settings():
            app.close_settings()

        def teardown_browse():
            pass

        def teardown_search():
            if self._minSearchBar.y > -self._minSearchBar.height:
                anim = Animation(y=-self._minSearchBar.height, duration=0.1)
                anim = anim + Animation(y=-app.height, duration=0)
                anim.stop(self._minSearchBar)
                anim.start(self._minSearchBar)

        def teardown_main():
            pass

        {"list": teardown_list,
         "edit": teardown_edit,
         "transpose": teardown_transpose,
         "settings": teardown_settings,
         "browse": teardown_browse,
         "search": teardown_search,
         "main": teardown_main}.get(targetState)()
