#!/usr/bin/env python
import kivy
# kivy.require('1.9.0')
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.slider import Slider
from .tickmarker import TickMarker
from .misc import MyButton

Builder.load_string("""
<TransposeBar>:
    orientation: "horizontal" if (app.tablet or app.landscape) else "vertical"
    size_hint_y: None
    height: label.height if (app.tablet or app.landscape) else label.height*2
    BoxLayout:
        id: box
        orientation: "horizontal"
        TickSlider:
            id: bar_slider
        Label:
            id: label
            text: "+" + str(int(bar_slider.value)) if bar_slider.value > 0 else str(int(bar_slider.value))
            size_hint: 0.1, None
            padding: 10, 10
            size: self.texture_size
    ButtonGridLayout:
        pos_hint: {'right': 1.0, 'y': 0 if root.height == 0 else 0.5*(root.height - self.height)/root.height}
        rows: 1
        MyButton:
            text: "Apply"
            _name: "transpose_apply"
            on_press: root.transpose_apply()
        MyButton:
            text: "Sharp/Flat"
            _name: "transpose_sharpflat"
            on_press: root.transpose_sharpflat()
<TickSlider>:
    min: -6
    max: 6
    value: 0
    step: 1
    ticks_major: 1
    ticks_minor: 1
""")

class TransposeBar(BoxLayout):
    def on_pos(self, instance, value):
        focus = False if value[1] < 0.0 else True
        for widget in self.walk(restrict=True):
            if isinstance(widget, MyButton):
                widget.is_focusable = focus

    def transpose_apply(self):
        print("ACTION: Apply the current transpose value")

    def transpose_sharpflat(self):
        print("ACTION: Change current chords from sharp to flat based")


class TickSlider(Slider, TickMarker):
    '''
    A slider with tick marks.
    '''
    pass
