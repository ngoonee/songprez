import json
from collections import OrderedDict

_settings_object = OrderedDict()

_settings_object['User Interface'] = [
            {'type': 'title',
                'title': 'Font Settings'},
            {'type': 'numeric',
                'title': 'Size',
                'desc': 'Font Size in pixels',
                'section': 'interface',
                'key': 'fontsize',
                'default': 15}
            ]

_settings_object['Panel Name'] = [
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


def _default_settings(config):
    for sect in _settings_object:
        sectionName = _settings_object[sect][1]['section']
        sectionDefaults = {}
        for i in _settings_object[sect]:
            if i['type'] != 'title':
                sectionDefaults[i['key']] = i['default']
        config.setdefaults(sectionName, sectionDefaults)


def _build_settings(settings, config):
    for sect in _settings_object:
        settings.add_json_panel(sect, config,
                                data=json.dumps(_settings_object[sect]))
