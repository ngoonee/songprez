#!/usr/bin/env python
import kivy
# kivy.require('1.9.0')
from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.button import Button

Builder.load_string("""
<NormalSizeFocusButton>:
    size_hint_x: None
""")


class FocusButton(FocusBehavior, Button):
    def on_focus(self, instance, value):
        self.bold = value

    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        super(FocusButton, self).keyboard_on_key_down(window, keycode, text, modifiers)
        if keycode[1] in ("enter", "spacebar"):
            self.trigger_action()
            return True
        return False


class NormalSizeFocusButton(FocusButton):
    def __init__(self, **kwargs):
        super(NormalSizeFocusButton, self).__init__(**kwargs)
        Clock.schedule_once(self._finish_init)

    def _finish_init(self, dt):
        app = App.get_running_app()
        app.bind(colwidth=self._setwidth)

    def _setwidth(self, instance, value):
        print(value)
        self.width = value
