#!/usr/bin/env python
import kivy
# kivy.require('1.9.0')
from kivy.compat import string_types
from kivy.factory import Factory
from kivy.properties import ListProperty, ObjectProperty, BooleanProperty
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.behaviors import FocusBehavior
from kivy.graphics import Color, Line


class SpinnerOption(FocusBehavior, Button):
    def __init__(self, **kwargs):
        super(SpinnerOption, self).__init__(**kwargs)
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
        super(SpinnerOption, self).keyboard_on_key_down(window, keycode, text, modifiers)
        if keycode[1] in ("enter", "spacebar"):
            self.trigger_action()
            return True
        elif keycode[1] == 'down' and modifiers == []:
            next = self._get_focus_next('focus_next')
            if next:
                self.focus = False
                next.focus = True
            return True
        elif keycode[1] == 'up' and modifiers == []:
            next = self._get_focus_next('focus_previous')
            if next:
                self.focus = False
                next.focus = True
            return True
        return False


class Spinner(Button):
    '''Spinner class, see module documentation for more information.
    '''

    values = ListProperty()
    '''Values that can be selected by the user. It must be a list of strings.

    :attr:`values` is a :class:`~kivy.properties.ListProperty` and defaults to
    [].
    '''

    option_cls = ObjectProperty(SpinnerOption)
    '''Class used to display the options within the dropdown list displayed
    under the Spinner. The `text` property of the class will be used to
    represent the value.

    The option class requires at least:

    - a `text` property, used to display the value.
    - an `on_release` event, used to trigger the option when pressed/touched.

    :attr:`option_cls` is an :class:`~kivy.properties.ObjectProperty` and
    defaults to :class:`SpinnerOption`.

    .. versionchanged:: 1.8.0
        If you set a string, the :class:`~kivy.factory.Factory` will be used to
        resolve the class.

    '''

    dropdown_cls = ObjectProperty(DropDown)
    '''Class used to display the dropdown list when the Spinner is pressed.

    :attr:`dropdown_cls` is an :class:`~kivy.properties.ObjectProperty` and
    defaults to :class:`~kivy.uix.dropdown.DropDown`.

    .. versionchanged:: 1.8.0
        If you set a string, the :class:`~kivy.factory.Factory` will be used to
        resolve the class.

    '''

    is_open = BooleanProperty(False)
    '''By default, the spinner is not open. Set to True to open it.

    :attr:`is_open` is a :class:`~kivy.properties.BooleanProperty` and
    defaults to False.

    .. versionadded:: 1.4.0
    '''

    mimic_size = BooleanProperty(False)
    '''Each element in the dropdown list uses a default/user-supplied height.
    Set to True to propagate the Spinner's height value to each dropdown list
    element.

    :attr:`mimic_size` is a :class:`~kivy.properties.BooleanProperty` and
    defaults to False.

    .. versionadded:: No idea
    '''

    def __init__(self, **kwargs):
        self._dropdown = None
        super(Spinner, self).__init__(**kwargs)
        self.bind(
            on_release=self._toggle_dropdown,
            dropdown_cls=self._build_dropdown,
            option_cls=self._build_dropdown,
            values=self._update_dropdown,
            size=self._update_dropdown)
        self._build_dropdown()

    def _build_dropdown(self, *largs):
        if self._dropdown:
            self._dropdown.unbind(on_select=self._on_dropdown_select)
            self._dropdown.unbind(on_dismiss=self._close_dropdown)
            self._dropdown.dismiss()
            self._dropdown = None
        cls = self.dropdown_cls
        if isinstance(cls, string_types):
            cls = Factory.get(cls)
        self._dropdown = cls()
        self._dropdown.bind(on_select=self._on_dropdown_select)
        self._dropdown.bind(on_dismiss=self._close_dropdown)
        self._update_dropdown()

    def _update_dropdown(self, *largs):
        dp = self._dropdown
        cls = self.option_cls
        if isinstance(cls, string_types):
            cls = Factory.get(cls)
        dp.clear_widgets()
        for value in self.values:
            item = cls(text=value)
            item.height = self.height if self.mimic_size else item.height
            item.bind(on_release=lambda option: dp.select(option.text))
            dp.add_widget(item)

    def _toggle_dropdown(self, *largs):
        self.is_open = not self.is_open

    def _close_dropdown(self, *largs):
        self.is_open = False

    def _on_dropdown_select(self, instance, data, *largs):
        self.text = data
        self.is_open = False

    def on_is_open(self, instance, value):
        if value:
            self._dropdown.open(self)
        else:
            if self._dropdown.attach_to:
                self._dropdown.dismiss()


class FocusSpinner(FocusBehavior, Spinner):
    def __init__(self, **kwargs):
        super(FocusSpinner, self).__init__(**kwargs)
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
        super(FocusSpinner, self).keyboard_on_key_down(window, keycode, text, modifiers)
        if keycode[1] in ("enter", "spacebar"):
            self.trigger_action()
            return True

    def on_release(self, **kwargs):
        super(FocusSpinner, self).on_release(**kwargs)
        dp = self._dropdown
        dp.children[0].children[6].focus = True

    def on_is_open(self, instance, value):
        super(FocusSpinner, self).on_is_open(instance, value)
        if not value:
            self.focus = True
