#!/usr/bin/env python
import kivy
# kivy.require('1.9.0')
from kivy.lang import Builder
from kivy.uix.textinput import TextInput
from kivy.properties import BooleanProperty

Builder.load_string("""
<RegisteredTextInput>:
    font_name: 'songprez/fonts/NSimSun.ttf'
    write_tab: False
    #on_focus: app.register_textinput(self, self.focus)

<SingleLineTextInput>:
    multiline: False
    size_hint_y: None
    height: self.minimum_height
""")


class RegisteredTextInput(TextInput):
    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        if keycode[1] == "escape":
            # Prevent escape from defocusing
            return True
        super(RegisteredTextInput, self).keyboard_on_key_down(window, keycode,
                                                              text, modifiers)


class SingleLineTextInput(RegisteredTextInput):
    '''
    TextInput which only accepts a single line of text. The 'enter' key is
    consumed while typing here
    '''
    text_update = BooleanProperty(False)
    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        if keycode[1] == "enter":
            # Catch the 'enter' key, which by default causes loss of focus in
            # single line TextInput widgets.
            self.dispatch('on_text_validate')
            return True
        elif keycode[1] == "spacebar":
            self.text_update = True
            self.text_update = False
        super(SingleLineTextInput, self).keyboard_on_key_down(window, keycode,
                                                              text, modifiers)
