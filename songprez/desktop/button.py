#!/usr/bin/env python
import kivy
# kivy.require('1.9.0')
from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.button import Button
from kivy.graphics import Color, Line

Builder.load_string("""
<NormalSizeFocusButton>:
    size_hint_x: None
""")


class FocusButton(FocusBehavior, Button):
    def __init__(self, **kwargs):
        super(FocusButton, self).__init__(**kwargs)
        self.bind(pos=self._draw_outline)
        self.bind(size=self._draw_outline)
        self.bind(focus=self._draw_outline)

    def _draw_outline(self, instance, value):
        try:
            self.canvas.remove(self._outline)
        except AttributeError:
            pass
        if self.focus:
            with self.canvas:
                Color(1, 0, 0, 0.6)
                rectOpt = (self.pos[0], self.pos[1], self.size[0], self.size[1])
                self._outline = Line(rectangle=rectOpt, width=2)

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
        self.width = value
