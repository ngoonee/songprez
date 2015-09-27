#!/usr/bin/env python

import kivy
# kivy.require('1.9.0')
from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.uix.behaviors import FocusBehavior
from kivy.properties import NumericProperty
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.boxlayout import BoxLayout

Builder.load_string("""
<MenuButton@FontResizeButton>:
    _ref: self.__self__
    # The _name parameter must be set, this is used by MainMenu to populate app.buttons
    _name: ""
    on_press: app._handle_menu_button(self._ref)
<MainMenu>:
    size_hint: None, None
    # Automatic re-sizing based on app size
    width: 0 if (app.minimal and app.tablet) else (app.height / 8 if app.landscape else app.width)
    height: 0 if (app.minimal and app.tablet) else (app.height if app.landscape else app.width / 8)
    orientation: "vertical" if app.landscape else "horizontal"
    MenuButton:
        text: 'List'
        _name: "menu_list"
    MenuButton:
        text: 'Edit'
        _name: "menu_edit"
    MenuButton:
        text: 'Transpose'
        _name: "menu_transpose"
    MenuButton:
        text: 'Settings'
        _name: "menu_settings"
    MenuButton:
        text: 'Browse'
        _name: "menu_browse"
    MenuButton:
        text: 'Search'
        _name: "menu_search"
""")


class FontResizeButton(ToggleButton):
    '''
    These buttons will use the default systemFontSize and dynamically adjust
    font_size if the button is smaller than the texture_size due to current
    font_size.

    Kivy note: texture_size includes padding, text_size does not
    '''

    def __init__(self, **kwargs):
        super(FontResizeButton, self).__init__(**kwargs)
        app = App.get_running_app()
        # Respond to change in system font size
        app.bind(systemFontSize=self.on_width)

    def on_width(self, instance, value):
        # width and height are already linked hence only need to bind one
        app = App.get_running_app()
        if app.minimal and app.tablet:
            self.font_size = 0
            #self.is_focusable = False
        else:
            # a slight hack to force a change in texture_size, even if
            # font_size does not change
            self.padding_y = 1 if self.padding_y == 0 else 0
            self.font_size = app.config.getint('interface', 'fontsize')
            #self.is_focusable = True

    def on_texture_size(self, instance, value):
        if (self.texture_size[0] > self.width or
                self.texture_size[1] > self.height):
            ratio = min(self.width*1.0/self.texture_size[0],
                        self.height*1.0/self.texture_size[1])
            self.font_size = ratio * self.font_size


class MainMenu(BoxLayout):
    '''
    The application's main menu buttons. Will always take up less than 1/8th of
    the screen, and gets hidden in minimal mode (for tablets/computers).
    '''
    def __init__(self, **kwargs):
        super(MainMenu, self).__init__(**kwargs)
        Clock.schedule_once(self._finish_init)

    def _finish_init(self, dt):
        app = App.get_running_app()
        # Adds all current buttons to the Dict in app.buttons, for easy
        # reference when switching states
        app.buttons.update({i._name: i for i in self.children})
