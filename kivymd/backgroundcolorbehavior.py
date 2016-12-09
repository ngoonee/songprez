# -*- coding: utf-8 -*-
from kivy.lang import Builder
from kivy.properties import BoundedNumericProperty, ReferenceListProperty
from kivy.properties import OptionProperty, ListProperty
from kivy.uix.widget import Widget
from kivy.utils import get_color_from_hex
from kivymd.color_definitions import text_colors
from kivymd.theming import ThemableBehavior

Builder.load_string('''
<BackgroundColorBehavior>
    canvas:
        Color:
            rgba: self.background_color
        Rectangle:
            size: self.size
            pos: self.pos
''')


class BackgroundColorBehavior(Widget):
    r = BoundedNumericProperty(1., min=0., max=1.)
    g = BoundedNumericProperty(1., min=0., max=1.)
    b = BoundedNumericProperty(1., min=0., max=1.)
    a = BoundedNumericProperty(0., min=0., max=1.)

    background_color = ReferenceListProperty(r, g, b, a)


class SpecificBackgroundColorBehavior(BackgroundColorBehavior):
    background_palette = OptionProperty(
            'Primary',
            options=['Primary', 'Accent',
                     'Red', 'Pink', 'Purple', 'DeepPurple', 'Indigo', 'Blue',
                     'LightBlue', 'Cyan', 'Teal', 'Green', 'LightGreen',
                     'Lime', 'Yellow', 'Amber', 'Orange', 'DeepOrange',
                     'Brown', 'Grey', 'BlueGrey'])

    background_hue = OptionProperty(
            '500',
            options=['50', '100', '200', '300', '400', '500', '600', '700',
                     '800', '900', 'A100', 'A200', 'A400', 'A700'])

    specific_text_color = ListProperty([0, 0, 0, 1])

    def _update_specific_text_color(self, instance, value):
        if hasattr(self, 'theme_cls'):
            palette = {'Primary': self.theme_cls.primary_palette,
                       'Accent': self.theme_cls.accent_palette
                       }.get(self.background_palette, self.background_palette)
        else:
            palette = {'Primary': 'Blue',
                       'Accent': 'Amber'
                       }.get(self.background_palette, self.background_palette)
        if text_colors[palette].get(self.background_hue):
            self.specific_text_color = get_color_from_hex(text_colors[palette]
                                                          [self.background_hue])
        else:
            # Some palettes do not have 'A100', 'A200', 'A400', 'A700'
            # In that situation just default to using 100/200/400/700
            hue = self.background_hue[1:]
            self.specific_text_color = get_color_from_hex(text_colors[palette][hue])

    def __init__(self, **kwargs):
        super(SpecificBackgroundColorBehavior, self).__init__(**kwargs)
        if hasattr(self, 'theme_cls'):
            self.theme_cls.bind(primary_palette=self._update_specific_text_color)
            self.theme_cls.bind(accent_palette=self._update_specific_text_color)
            self.theme_cls.bind(theme_style=self._update_specific_text_color)
        self.bind(background_hue=self._update_specific_text_color)
        self.bind(background_palette=self._update_specific_text_color)
        self._update_specific_text_color(None, None)
