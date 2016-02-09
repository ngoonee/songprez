import json
import os
from collections import OrderedDict
from kivy import platform

settings_object = OrderedDict()

defaultdatadir = os.path.join(os.path.expanduser('~'), 'SongPrez')
defaultindexdir = os.path.join(os.path.expanduser('~'), '.songprez')
if platform == 'linux':
    pass
elif platform == 'win':
    defaultdatadir = os.path.join(os.path.expanduser('~'), 'SongPrez')
    defaultindexdir = os.path.join(os.path.expanduser('~'), 'AppData',
                                   'Local', 'SongPrez')
    pass
elif platform == 'android':
    pass
elif platform == 'macosx':
    pass
elif platform == 'ios':
    pass

settings_object['Files & Folders'] = [
        {'type': 'pathex',
            'title': 'SongPrez Data Folder',
            'desc': 'SongPrez will not start if this folder does not exist',
            'section': 'filesfolders',
            'key': 'datadir',
            'dirselect': True,
            'default': defaultdatadir},
        {'type': 'pathex',
            'title': 'SongPrez Search Index Folder',
            'desc': 'Indices for searching are stored here. Default values are fine.',
            'section': 'filesfolders',
            'key': 'indexdir',
            'dirselect': True,
            'show_hidden': True,
            'default': defaultindexdir},
        ]

settings_object['User Interface'] = [
            {'type': 'title',
                'title': 'Font Settings'},
            {'type': 'numeric',
                'title': 'Size',
                'desc': 'Font Size in pixels',
                'section': 'interface',
                'key': 'fontsize',
                'default': 15}
            ]

settings_object['Panel Name'] = [
            {'type': 'title',
            'title': 'example title'},
            {'type': 'bool',
            'title': 'A boolean setting',
            'desc': 'Boolean description text',
            'section': 'example',
            'key': 'boolexample',
            'default': True},
            {'type': 'numeric',
            'title': 'A numeric setting',
            'desc': 'Numeric description text',
            'section': 'example',
            'key': 'numericexample',
            'default': 10},
            {'type': 'options',
            'title': 'An options setting',
            'desc': 'Options description text',
            'section': 'example',
            'key': 'optionsexample',
            'options': ['option1', 'option2', 'option3'],
            'default': 'option2'},
            {'type': 'string',
            'title': 'A string setting',
            'desc': 'String description text',
            'section': 'example',
            'key': 'stringexample',
            'default': 'some_string'},
            {'type': 'path',
            'title': 'A path setting',
            'desc': 'Path description text',
            'section': 'example',
            'key': 'pathexample',
            'default': '/some/path/'}
            ]


def default_settings(config):
    for sect in settings_object:
        try:
            sectionName = settings_object[sect][1]['section']
        except IndexError:
            sectionName = settings_object[sect][0]['section']
        sectionDefaults = {}
        for i in settings_object[sect]:
            if i['type'] != 'title':
                sectionDefaults[i['key']] = i['default']
        config.setdefaults(sectionName, sectionDefaults)


def build_settings(settings, config):
    for sect in settings_object:
        settings.add_json_panel(sect, config,
                                data=json.dumps(settings_object[sect]))
