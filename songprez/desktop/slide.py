#!/usr/bin/env python
import kivy
# kivy.require('1.9.1')
from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.properties import NumericProperty, StringProperty, ObjectProperty
from kivy.properties import OptionProperty
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.stencilview import StencilView
from kivy.properties import ObjectProperty
from kivy.graphics import Color, Rectangle, PopMatrix, PushMatrix, Translate
from math import pi, sin, cos, sqrt

Builder.load_string("""
<SlideElement>:
    id: bl
    label: label
    OutlinedLabel:
        id: label
        mipmap: True
        #text_size: (bl.parent.size[0] - bl.padding[0] - bl.padding[2], None)
        text_size: (bl.size[0] - bl.padding[0] - bl.padding[2], None)
        text: bl.text
        font_name: bl.font_name
        target_font_size: bl.font_size
        halign: bl.halign
        valign: bl.valign
        border_thickness: bl.border_thickness
""")


class SlideElement(BoxLayout):
    text = StringProperty('')
    font_name = StringProperty('')
    font_size = NumericProperty('15sp')
    min_font_size = NumericProperty('5sp')
    halign = OptionProperty('left', options=['left', 'center', 'right',
                            'justify'])
    valign = OptionProperty('bottom', options=['bottom', 'middle', 'top'])
    border_thickness = OptionProperty('regular', options=['thick', 'regular',
                                      'thin', 'minimal', 'none'])

    def on_padding(self, instance, val):
        print(val)


class OutlinedLabel(Label, StencilView):
    min_font_size = NumericProperty('5sp')
    target_font_size = NumericProperty(0)
    border_thickness = OptionProperty('regular', options=['thick', 'regular',
                                      'thin', 'minimal', 'none'])

    def __init__(self, **kwargs):
        super(OutlinedLabel, self).__init__(**kwargs)
        Clock.schedule_once(self._finish_init)

    def _finish_init(self, dt):
        self._outline = []
        self.bind(target_font_size=self._redraw, size=self._redraw,
                  border_thickness=self._redraw, text=self._redraw)
        self._redraw(None, None)

    def _redraw(self, instance, value):
        '''
        Draw the initial background. Called when initialized as well as when
        anything which requires re-drawing happens (font size change, text
        content change, border thickness change, label size change).
        '''
        try:
            # Remove old instructions
            for item in self._outline:
                self.canvas.before.remove(item)
            del self._outline[:]
        except AttributeError:
            pass
        with self.canvas.before:
            self.font_size = self.target_font_size
            self.texture_update()
            if self.texture_size[1] > self.size[1]:
                '''
                Binary search (only if font size is too big, if too small
                nevermind. Find a font size in between current and smallest
                and test again. If its small enough, find a font size between
                current and biggest.
                '''
                upper = self.target_font_size
                lower = self.min_font_size
                while upper-lower > 1:
                    candidate = (upper + lower) // 2
                    self.font_size = candidate
                    self.texture_update()
                    if self.texture_size[1] > self.size[1]:
                        upper = candidate
                    else:
                        lower = candidate
                self.font_size = lower
                self.texture_update()
                # At this point, maximum allowable font size has been achieved

            if self.border_thickness == 'none':
                return
            scale = {'thick': 1.5,
                     'regular': 2,
                     'thin': 3,
                     'minimal': 4}.get(self.border_thickness, 2)
            border = sqrt(self.font_size)/scale
            angle = 0
            spacing = 2 * pi / (border * 4)
            newpos = (self.pos[0],
                      self.pos[1] + (self.size[1]-self.texture_size[1])/2)
            Color(rgba=(0, 0, 0, 1))
            while angle < 2*pi:
                angle += spacing
                PushMatrix()
                Translate(border*sin(angle), border*cos(angle))
                self._outline.append(Rectangle(pos=newpos,
                                               size=self.texture_size,
                                               texture=self.texture))
                PopMatrix()
