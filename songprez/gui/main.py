#!/usr/bin/env python
import kivy
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput


class MyTextInput(TextInput):
    def __init__(self, **kwargs):
        super(MyTextInput, self).__init__(**kwargs)
        self.write_tab = False
        self.is_focusable = False

class TestApp(App):
    def build(self):
        self.box = BoxLayout()
        self.box.add_widget(MyTextInput(text="starting text"))
        but = Button(text="do this")
        but.bind(on_press=self.test)
        self.box.add_widget(but)
        return self.box

    def test(self, instance):
        for widget in self.box.walk():
            if isinstance(widget, TextInput):
                widget.focus = True
                return

if __name__=='__main__':
    TestApp().run()
