# -*- coding: utf-8 -*-
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import StringProperty, BoundedNumericProperty
from kivymd.button import BaseRaisedButton, BasePressedButton
from kivymd.ripplebehavior import RectangularRippleBehavior
from kivymd.elevationbehavior import RectangularElevationBehavior

Builder.load_string('''
#:import md_icons kivymd.icon_definitions.md_icons
#:import MDLabel kivymd.label.MDLabel
<IconTextButton>:
    canvas:
        Color:
            rgba: self._current_button_color
        RoundedRectangle:
            size: self.size
            pos: self.pos
            radius: (dp(2),)
    content: content
    height: dp(36)
    width: content.width + dp(32)
    padding: (dp(8), 0)
    theme_text_color: 'Primary'
    background_color: root.theme_cls.primary_color
    BoxLayout:
        id: content
        size_hint_x: None
        width: icon.width + text.width
        MDLabel:
            id: icon
            font_style: 'Icon'
            text: u"{}".format(md_icons[root.icon])
            size_hint_x: None
            text_size: (None, root.height)
            size: (root.height, self.texture_size[1])
            halign: 'right'
            theme_text_color: root.theme_text_color
            text_color: root.text_color
            opposite_colors: root.opposite_colors
            disabled: root.disabled
            valign: 'middle'
        MDLabel:
            id: text
            text: root._capitalized_text
            font_style: 'Button'
            size_hint_x: None
            text_size: (None, root.height)
            theme_text_color: root.theme_text_color
            text_color: root.text_color
            disabled: root.disabled
            valign: 'middle'
            halign: 'left'
            opposite_colors: root.opposite_colors
''')

class IconTextButton(RectangularRippleBehavior, BaseRaisedButton,
                     RectangularElevationBehavior, BasePressedButton):
    width = BoundedNumericProperty(dp(88), min=dp(88), max=None,
                                   errorhandler=lambda x: dp(88))
    icon = StringProperty('checkbox-blank-circle')
    text = StringProperty('')
    _capitalized_text = StringProperty('')

    def on_text(self, instance, value):
        self._capitalized_text = value.upper()
