#!/usr/bin/env python
import kivy
# kivy.require('1.9.0')
from kivy.app import App
from kivy.lang import Builder
from kivy.adapters.listadapter import ListAdapter
from kivy.uix.listview import ListItemButton
from kivy.uix.settings import SettingsWithSidebar
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.properties import BooleanProperty
import os
import sys
sys.path.append('/home/data/Coding/python/songprez')
from songprez.IO.docxexport import write_docx

Builder.load_string("""
<DocxExport>:
    list: list
    path: path
    leader: leader
    piano: piano
    guitar: guitar
    drum: drum
    tambourine: tambourine
    colour: colour
    docx: docx
    orientation: "horizontal"
    ListView:
        id: list
    BoxLayout:
        orientation: "vertical"
        Button:
            text: "Settings"
            on_press: app.open_settings()
        SingleLineTextInput:
            id: path
            text: "Set path here"
        SingleLineTextInput:
            id: leader
            text: "Worship Leader"
        SingleLineTextInput:
            id: piano
            text: "Piano"
        SingleLineTextInput:
            id: guitar
            text: "Guitar"
        SingleLineTextInput:
            id: drum
            text: "Drum"
        SingleLineTextInput:
            id: tambourine
            text: "Tambourinist"
        SingleLineTextInput:
            id: colour
            text: "Colour"
        SingleLineTextInput:
            id: docx
            text: "Output filename here.docx"
        Button:
            text: "Save"
            on_press: root.save_docx()
<SingleLineTextInput>:
    size_hint_y: None
    multiline: False
    height: self.minimum_height
""")

class SingleLineTextInput(TextInput):
    '''
    TextInput which only accepts a single line of text. The 'enter' key is
    consumed while typing here, and parent widgets may bind to the action
    property to take the appropriate action. The value of the property is
    not significant (may be True or False at anytime).

    For examples of how this is used, see search.py
    '''
    action = BooleanProperty(False)

    def __init__(self, **kwargs):
        super(SingleLineTextInput, self).__init__(**kwargs)
        self.write_tab = False

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

class DocxExport(BoxLayout):
    def save_docx(self):
        app = App.get_running_app()
        fullpath = os.path.join(app.config.get('Paths', 'setdir'), self.path.text)
        write_docx(fullpath, self.docx.text,
                        pianist=self.piano.text,
                        guitar=self.guitar.text,
                        drum=self.drum.text,
                        tambourinists=self.tambourine.text,
                        colour=self.colour.text)

class DocxExportApp(App):
    def __init__(self, **kwargs):
        super(DocxExportApp, self).__init__(**kwargs)

    def build(self):
        self.settings_cls = SettingsWithSidebar
        self.use_kivy_settings = False
        data = [{'text':str(i), 'is_selected': False} for i in range(100)]
        args_converter = lambda row_index, rec: {'text': rec['text'],
                                                 'size_hint_y': None,
                                                 'height': 25}
        list_adapter = ListAdapter(data=data,
                                   args_converter=args_converter,
                                   cls=ListItemButton,
                                   selection_mode='single',
                                   allow_empty_selection=False)
        self.root = DocxExport()
        self.root.list.adapter = list_adapter
        path = self.config.get('Paths', 'setdir')
        self._load_sets(path)
        self.root.list.adapter.bind(selection=self._update_selection)
        return self.root

    def get_application_config(self):
        return os.path.join(self.user_data_dir, 'songprez.ini')

    def build_config(self, config):
        config.setdefaults('Paths', {
            'setdir': '/home/data/Dropbox/OpenSong/Sets/',
            'outputdir': '/home/data/ChurchWork/Children\'sChurch/2015-CCWorship/'
        })

    def build_settings(self, settings):
        jsondata = """[{ "type": "title", "title": "Test Application" },
                       { "type": "path", "title": "Set Directory",
                         "desc": "Directory for OpenSong Sets",
                         "section": "Paths", "key": "setdir"},
                       { "type": "path", "title": "Docx Directory",
                         "desc": "Directory for Children's Church Worship Documents",
                         "section": "Paths", "key": "outputdir"}
                      ]"""
        settings.add_json_panel('Test Application', self.config, data=jsondata)

    def _load_sets(self, path):
        names = (file for file in os.listdir(path)
                if os.path.isfile(os.path.join(path, file)))
        data = []
        for item in names:
            data.append({'text': item, 'is_selected': False})
        data.reverse()
        self.root.list.adapter.data = data
    
    def _update_selection(self, adapter, item):
        if (len(item)):
            self.root.path.text = item[0].text

if __name__ == "__main__":
    DocxExportApp().run()
