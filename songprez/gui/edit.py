#!/usr/bin/env python
import kivy
# kivy.require('1.9.0')
from kivy.app import App
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.accordion import Accordion

Builder.load_string("""
<SongEditScroller@ScrollView>:
    txtinput: txtinput
    do_scroll_y: True
    scroll_type: ['bars', 'content']
    bar_width: 10
    effect_cls: "ScrollEffect"
    MyTextInput:
        id: txtinput
        size_hint: 1, None
        height: max(self.minimum_height, self.parent.height)
        font_name: "/usr/share/fonts/TTF/consola"
<SongPrimaryInfo@BoxLayout>:
    orientation: "vertical"
    BoxLayout:
        id: box
        size_hint_y: None
        height: txt.height*2 if app.minimal and app.tablet and app.landscape else txt.height
        orientation: "vertical" if app.minimal and app.tablet and app.landscape else "horizontal"
        SingleLineTextInput:
            id: txt
            text: "Title"
        SingleLineTextInput:
            text: "Author"
    SongEditScroller:
        height: root.height
<SongSecondaryInfo>:
    base: self
    orientation: "vertical" if app.tablet == app.landscape else "horizontal"
    height: 12*txt.height if app.tablet == app.landscape else 6*txt.height
    BoxLayout:
        orientation: "vertical"
        size_hint_y: None
        height: 5*txt.height
        pos_hint: {'top': 1.0}
        SingleLineTextInput:
            text: "Presentation Order"
        SingleLineTextInput:
            text: "AKA"
        SingleLineTextInput:
            text: "Key Line"
        GridLayout:
            cols: 2
            SingleLineTextInput:
                id: txt
                text: "Key"
            Spinner:
                text: "Capo"
                values: "0", "1", "2", "3", "4", "5" 
                size_hint: 1, None
                size: txt.size
            Spinner:
                text: "Time Signature"
                values: "2/4", "3/4", "4/4", "3/8", "6/8", "Custom"
                size_hint: 1, None
                size: txt.size
            Spinner:
                text: "Tempo"
                values: "Very Slow", "Slow", "Moderate", "Fast", "Very Fast"
                size_hint: 1, None
                size: txt.size
    BoxLayout:
        orientation: "vertical"
        SingleLineTextInput:
            text: "Copyright"
        SingleLineTextInput:
            text: "CCLI"
        SingleLineTextInput:
            text: "Hymn Number"
        BoxLayout:
            orientation: "vertical"
        ButtonGridLayout:
            cols: 3 if app.tablet and not app.landscape else 2
            MyButton:
                text: "New"
                _name: "edit_new"
                on_press: root.base.new()
            MyButton:
                text: "Copy"
                _name: "edit_copy"
                on_press: root.base.copy()
            MyButton:
                text: "Rename"
                _name: "edit_rename"
                on_press: root.base.rename()
            MyButton:
                text: "Delete"
                _name: "edit_delete"
                on_press: root.base.delete()
            MyButton:
                text: "Revert"
                _name: "edit_revert"
                on_press: root.base.revert()
            MyButton:
                text: "Save"
                _name: "edit_save"
                on_press: root.base.save()
<MinSongEdit>:
    orientation: "vertical"
    SongPrimaryInfo:
        height: app.height - button.height
        id: pi
    ButtonGridLayout:
        id: button
        rows: 1
        MyButton:
            text: "Revert"
            _name: "edit_revert"
            on_press: root.revert()
        MyButton:
            text: "Save"
            _name: "edit_save"
            on_press: root.save()
<MaxSongEdit>:
    orientation: "vertical"
    BoxLayout:
        orientation: "horizontal" if app.landscape else "vertical"
        BoxLayout:
            orientation: "vertical"
            size_hint_x: 0.7 if app.landscape else 1
            BoxLayout:
                orientation: "horizontal"
                size_hint_y: None
                height: txt.height
                SingleLineTextInput:
                    id: txt
                    text: "Title"
                SingleLineTextInput:
                    text: "Author"
            SongEditScroller:
        SongSecondaryInfo:
            base: root.__self__
            size_hint_x: 0.3 if app.landscape else 1
            size_hint_y: 1 if app.landscape else None
    TransposeBar:
<PhoneSongEdit>:
    primaryinf: primaryinf
    orientation: "horizontal"
    AccordionItem:
        id: primaryinf
        title: "Primary Information"
        collapse: False
        BoxLayout:
            orientation: "vertical"
            SongPrimaryInfo:
            TransposeBar:
    AccordionItem:
        title: "Secondary Information"
        SongSecondaryInfo:
            base: root.__self__
""")


class SongSecondaryInfo(BoxLayout):
    exceptiontext="The SongSecondaryInfo widget needs its' parent to define "\
                  +"a base object which handle's SongSecondaryInfo's buttons"

    def new(self):
        raise Exception(self.exceptiontext)

    def copy(self):
        raise Exception(self.exceptiontext)

    def delete(self):
        raise Exception(self.exceptiontext)

    def rename(self):
        raise Exception(self.exceptiontext)

    def revert(self):
        raise Exception(self.exceptiontext)

    def save(self):
        raise Exception(self.exceptiontext)


class EditWidget():
    def new(self):
        print("ACTION: Create a new song in this edit widget")

    def copy(self):
        print("ACTION: Copy the current song to a new filename")

    def delete(self):
        print("ACTION: Delete the current song from storage")

    def rename(self):
        print("ACTION: Rename the file containing the current song")

    def revert(self):
        print("ACTION: Revert this song to the current saved version")

    def save(self):
        print("ACTION: Save the current song back to storage")


class MinSongEdit(BoxLayout, EditWidget):
    pass


class MaxSongEdit(BoxLayout, EditWidget):
    pass


class PhoneSongEdit(Accordion, EditWidget):
    primaryinf = ObjectProperty(None)
    pass
