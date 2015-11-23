#!/usr/bin/env python
import kivy
# kivy.require('1.9.0')
from kivy.lang import Builder
from kivy.uix.modalview import ModalView
from .button import NormalSizeFocusButton
from .textinput import SingleLineTextInput

Builder.load_string("""
<FilenameDialog>:
    textinput: textinput
    auto_dismiss: False
    size_hint: 0.5, None
    height: app.rowheight + 2*app.rowspace + 3*app.colspace + textinput.height
    padding: app.colspace
    on_open: app.inhibit = True
    on_dismiss: app.inhibit = False
    sendMessage: app.sendMessage
    BoxLayout:
        id: box
        orientation: "vertical"
        padding: app.rowspace//2
        spacing: app.rowspace
        SingleLineTextInput:
            id: textinput
            on_text_validate: root.do_action(); root.dismiss()
        BoxLayout:
            orientation: "horizontal"
            size_hint_y: None
            height: app.rowheight + app.colspace
            padding: app.colspace//2
            spacing: app.colspace
            Widget:
            NormalSizeFocusButton:
                text: "Save"
                on_press: root.do_action(); root.dismiss()
            NormalSizeFocusButton:
                text: "Cancel"
                on_press: root.dismiss()
""")


class FilenameDialog(ModalView):
    def __init__(self, message, inittext=u'', delmessage=None, **kwargs):
        super(FilenameDialog, self).__init__(**kwargs)
        self.message = message
        self.inittext = inittext
        self.delmessage = delmessage
        self.textinput.text = inittext
        self.kwargs = kwargs
        self.open()

    def open(self):
        super(FilenameDialog, self).open()
        self.textinput.focus = True

    def do_action(self):
        self.sendMessage(self.message, relpath=self.textinput.text, **self.kwargs)
        if self.delmessage:
            if self.kwargs.get('itemtype'):
                self.sendMessage(self.delmessage, relpath=self.inittext,
                                 itemtype=self.kwargs['itemtype'])
            else:
                self.sendMessage(self.delmessage, relpath=self.inittext)
