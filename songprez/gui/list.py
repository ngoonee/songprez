#!/usr/bin/env python
import kivy
# kivy.require('1.9.0')
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout

Builder.load_string("""
#:import sla kivy.adapters.listadapter
#:import ListItemButton kivy.uix.listview.ListItemButton
<SetList>:
    tabletmode: 1 if app.tablet else 0
    landscapemode: 1 if app.landscape else 0
    orientation: "vertical"
    Label:
        text: "Existing Sets"
        size_hint: (1,None)
        size: (0, self.texture_size[1]*1.5)
    ListView:
        size_hint: (1,1)
        adapter:
            sla.ListAdapter(data=[], cls=ListItemButton)
        item_strings: ["Set " + str(i) for i in range(100)]
        allow_empty_selection: False
    ButtonGridLayout:
        cols: 4 if app.landscape != app.tablet else 2
        MyButton:
            text: "New"
            _name: "list_newset"
            on_press: root.new_set()
        MyButton:
            text: "Save"
            _name: "list_saveset"
            on_press: root.save_set()
        MyButton:
            text: "Rename"
            _name: "list_renameset"
            on_press: root.rename_set()
        MyButton:
            text: "Delete"
            _name: "list_deleteset"
            on_press: root.delete_set()
<SongList>:
    orientation: "vertical"
    Label:
        text: "Songs"
        size_hint: (1,None)
        size: (0, self.texture_size[1]*1.5)
    ListView:
        size_hint: (1,1)
        adapter:
            sla.ListAdapter(data=[], cls=ListItemButton)
        item_strings: ["Song " + str(i) for i in range(10)]
        allow_empty_selection: False
    ButtonGridLayout:
        cols: 4 if app.landscape != app.tablet else 2
        MyButton:
            text: "Move Up"
            _name: "list_up"
            on_press: root.move_up()
        MyButton:
            text: "Move Down"
            _name: "list_down"
            on_press: root.move_down()
        MyButton:
            text: "Add"
            _name: "list_addsong"
            on_press: root.add_song()
        MyButton:
            text: "Delete"
            _name: "list_deletesong"
            on_press: root.delete_song()
<MinSetList>:
    orientation: "vertical" if app.landscape else "horizontal"
    SetList:
    SongList:
<MaxSetList>:
    orientation: "horizontal" if app.landscape or app.tablet else "vertical"
    SetList:
    SongList:
""")


class SetList(BoxLayout):
    def new_set(self):
        print("ACTION: Create a new set")

    def save_set(self):
        print("ACTION: Save the currently shown set")

    def rename_set(self):
        print("ACTION: Save the currently shown set as another name")

    def delete_set(self):
        print("ACTION: Delete the currently shown set")


class SongList(BoxLayout):
    def move_up(self):
        print("ACTION: Move the current song higher in the current set")

    def move_down(self):
        print("ACTION: Move the current song lower in the current set")

    def add_song(self):
        print("ACTION: Add a song to the current set, switch state to browse?")

    def delete_song(Self):
        print("ACTION: Delete the current song from the current set")

class MinSetList(BoxLayout):
    pass


class MaxSetList(BoxLayout):
    pass
