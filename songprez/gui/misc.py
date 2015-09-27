#!/usr/bin/env python
import kivy
# kivy.require('1.9.0')
from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.properties import BooleanProperty
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from math import ceil

Builder.load_string("""
<SingleLineTextInput>:
    size_hint_y: None
    multiline: False
    height: self.minimum_height

<ButtonGridLayout>:
    size_hint: (None, None)
    pos_hint: {'right': 1.0}

<LyricPreview>:
    base: self
    txtinput: scroller.txtinput
    orientation: "vertical"
    SongEditScroller:
        id: scroller
        size_hint: 1, 1
        font_name: "/usr/share/fonts/TTF/consola"
    ButtonGridLayout:
        rows: 1
        MyButton:
            text: "Previous"
            _name: "_previous"
            on_press: root.base.previous()
        MyButton:
            text: "Next"
            _name: "_next"
            on_press: root.base.next()
        MyButton:
            text: "Add"
            _name: "_add"
            on_press: root.base.add()
""")


class MyButton(FocusBehavior, Button):
    def on_focus(self, instance, value):
        self.bold = value

    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        super(MyButton, self).keyboard_on_key_down(window, keycode, text, modifiers)
        if keycode[1] in ("enter", "spacebar"):
            self.trigger_action()
            return True
        return False


class MyTextInput(TextInput):
    def __init__(self, **kwargs):
        super(MyTextInput, self).__init__(**kwargs)
        self.write_tab = False

    def on_focus(self, instance, value):
        app = App.get_running_app()
        app.register_textinput(instance, value)


class SingleLineTextInput(MyTextInput):
    '''
    TextInput which only accepts a single line of text. The 'enter' key is
    consumed while typing here, and parent widgets may bind to the action
    property to take the appropriate action. The value of the property is
    not significant (may be True or False at anytime).

    For examples of how this is used, see search.py
    '''
    action = BooleanProperty(False)

    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        super(SingleLineTextInput, self).keyboard_on_key_down(window, keycode, text, modifiers)
        if keycode[1] == "enter":
            # Catch the 'enter' key, which by default causes loss of focus in
            # single line TextInput widgets. Also modify _action so that parents
            # of this widget can bind to it and fire the appropriate action.
            self.focus = True
            self.action = not self.action
            return True
        elif keycode[1] == "escape":
            # Have to catch escape as well, because otherwise it would call 'back'
            return True
        return False


class ButtonGridLayout(GridLayout):
    '''
    A GridLayout which will only contain buttons. Currently resizes to max
    size required of buttons contained, and no larger, to avoid very large
    buttons.

    Handles the font sizing of buttons as well, in the case where there's not
    enough space for the default font size (set in app's config).
    '''
    def __init__(self, **kwargs):
        super(ButtonGridLayout, self).__init__(**kwargs)
        Clock.schedule_once(self._finish_init)

    def _finish_init(self, dt):
        self.parent.bind(size=self._resize)
        # Respond to change in system font size
        App.get_running_app().bind(systemFontSize=self._resize)
        for c in self.children:
            c.bind(on_press=self.test)

    def test(self, instance):
        print("hello", self, instance, instance.text, instance._name)

    def _resize(self, instance, value):
        '''
        Find the maximum required size among all buttons, resize all buttons,
        and then resize the grid to match.

        In the situation where the buttons would overflow out of the allowable
        area of the grid, find a suitable scaled down font which would keep
        the buttons within the grid's parent's area. To do this, the parent
        would have to be a BoxLayout.
        '''
        if not isinstance(self.parent, BoxLayout):
            raise Exception("ButtonGridLayout must be in a BoxLayout")
        if self.parent.orientation == "vertical":
            allowed_width = self.parent.width
            allowed_height = self.parent.height / 2
        else:
            allowed_width = self.parent.width / 2
            allowed_height = self.parent.height
        rows = self.rows if self.rows is not None \
            else ceil(len(self.children) / self.cols)
        cols = self.cols if self.cols is not None \
            else ceil(len(self.children) / self.rows)
        max_h = 0
        max_w = 0
        fontsize = App.get_running_app().config.getint('interface', 'fontsize')
        for c in self.children:
            c.font_size = fontsize
            c.padding = (fontsize//3, fontsize//3)
            c.texture_update()
            w, h = c.texture_size
            max_w = w if w > max_w else max_w
            max_h = h if h > max_h else max_h
        if rows * max_h > allowed_height or cols * max_w > allowed_width:
            ratio = min(allowed_height*1.0/(rows * max_h),
                        allowed_width*1.0/(cols * max_w))
            fontsize = ratio * fontsize
            max_h = 0
            max_w = 0
            for c in self.children:
                c.font_size = fontsize
                c.padding = (fontsize//3, fontsize//3)
                c.texture_update()
                w, h = c.texture_size
                max_w = w if w > max_w else max_w
                max_h = h if h > max_h else max_h
        for c in self.children:
            c.width = max_w
            c.height = max_h
        self.height = rows * max_h
        self.width = cols * max_w


class LyricPreview(BoxLayout):
    exceptiontext = "The LyricPreview widget needs its' parent to define "\
                    +"a base object which handles LyricPreview's buttons"
    def __init__(self, **kwargs):
        super(LyricPreview, self).__init__(**kwargs)
        Clock.schedule_once(self._finish_init)

    def _finish_init(self, dt):
        self.txtinput.readonly = True

    def previous(self):
        raise Exception(self.exceptiontext)

    def next(self):
        raise Exception(self.exceptiontext)

    def add(self):
        raise Exception(self.exceptiontext)

def set_initial_focus(basewidget):
    for widget in basewidget.walk(restrict=True):
        if isinstance(widget, MyButton) and widget.is_focusable:
            print(widget, "found a button")
            widget.focus = True
            return
    # Will only focus TextInputs if there are no other valid options
    for widget in basewidget.walk(restrict=True):
        print("trying", widget)
        if isinstance(widget, SingleLineTextInput) and widget.is_focusable:
            print(widget, "found a textinput", widget.is_focusable)
            widget.focus = True
            return

