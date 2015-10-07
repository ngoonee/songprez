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
    pass


class SingleLineTextInput(RegisteredTextInput):
    '''
    TextInput which only accepts a single line of text. The 'enter' key is
    consumed while typing here, and parent widgets may bind to the action
    property to take the appropriate action. The value of the property is
    not significant (may be True or False at anytime).
    '''
    action = BooleanProperty(False)
    textupdate = BooleanProperty(False)

    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        super(SingleLineTextInput, self).keyboard_on_key_down(window, keycode, text, modifiers)
        print(keycode)
        if keycode[1] == "enter":
            # Catch the 'enter' key, which by default causes loss of focus in
            # single line TextInput widgets. Also modify action so that parents
            # of this widget can bind to it and fire the appropriate action.
            self.focus = True
            self.action = not self.action
            return True
        elif keycode[1] == "escape":
            # Have to catch escape as well, because otherwise it would call 'back'
            return True
        elif keycode[1] == "spacebar":
            self.textupdate = True
            self.textupdate = False
        return False
