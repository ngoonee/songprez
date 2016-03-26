#!/usr/bin/env python
import kivy
# kivy.require('1.9.1')
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.modalview import ModalView

Builder.load_string("""
<FlatButton@ButtonBehavior+Label>:
    markup: True
    font_size: app.ui_fs_button

<ModalPopUp>:
    message: ''
    lefttext: ''
    leftcolor: (0.2, 0.2, 0.2, 0)
    righttext: ''
    rightcolor: (0.2, 0.2, 0.2, 0)
    inputtext: 'test'
    input: input
    size_hint_x: 0.7
    size_hint_y: None
    height: mainbox.height
    BoxLayout:
        id: mainbox
        orientation: 'vertical'
        padding: '20dp'
        pos: root.pos
        size_hint_y: None
        height: messagebox.height + input.height + dp(10) + app.buttonsize + 2*dp(20)
        Label:
            id: messagebox
            text: root.message
            font_size: app.ui_fs_title
            halign: 'left'
            text_size: self.width, None
            size_hint_y: None
            height: self.texture_size[1]
            markup: True
        TextInput:
            id: input
            text: root.inputtext
            font_size: app.ui_fs_detail
            size_hint_y: None
            height: self.minimum_height if self.text else 0
            opacity: 1 if self.text else 0
        Widget:
            size_hint_y: None
            height: '10dp'
        BoxLayout:
            orientation: 'horizontal'
            size_hint_y: None
            height: app.buttonsize
            spacing: '5dp'
            FlatButton:
                canvas.before:
                    Color:
                        rgba: root.leftcolor
                    Rectangle:
                        pos: self.pos
                        size: self.size
                text: root.lefttext
                on_press: root.dispatch('on_left_action')
            FlatButton:
                canvas.before:
                    Color:
                        rgba: root.rightcolor
                    Rectangle:
                        pos: self.pos
                        size: self.size
                text: root.righttext
                on_press: root.dispatch('on_right_action')
""")


class ModalPopup(ModalView):
    """
    Defaults to dismissing itself on button press, return True from a bound
    function to disable this behaviour.
    """
    def __init__(self, **kwargs):
        super(ModalPopup, self).__init__(**kwargs)
        self.register_event_type('on_left_action')
        self.register_event_type('on_right_action')
        self.message = kwargs.get('message', '')
        self.lefttext = kwargs.get('lefttext', '')
        self.righttext = kwargs.get('righttext', '')
        if self.lefttext:
            self.leftcolor = kwargs.get('leftcolor', (0.2, 0.2, 0.2, 1))
        if self.righttext:
            self.rightcolor = kwargs.get('rightcolor', (0.2, 0.2, 0.2, 1))
        self.inputtext = kwargs.get('inputtext', '')
        self.auto_dismiss = False

    def _on_keyboard_down(self, *args):
        keycode = args[1]
        if keycode == 27:  # 'esc' on desktop, 'back' key on android
            self.dismiss()
            return True

    def on_open(self):
        Window.bind(on_key_down=self._on_keyboard_down)

    def on_dismiss(self):
        Window.unbind(on_key_down=self._on_keyboard_down)

    def on_left_action(self):
        if self.lefttext:
            self.dismiss()

    def on_right_action(self):
        if self.righttext:
            self.dismiss()
