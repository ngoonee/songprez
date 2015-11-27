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
        pass


class OutlinedLabel(Label, StencilView):
    min_font_size = NumericProperty('5sp')
    target_font_size = NumericProperty(0)
    border_thickness = OptionProperty('regular', options=['thick', 'regular',
                                      'thin', 'minimal', 'none'])
    '''
    Cached value of last best font size found, used to initialize the next
    search. Worst case performance identical to search from scratch, best case
    is less than half the iterations. Cuts down search time by about 1/3rd.

    This is accessed using the class, not the instance, i.e.
        OutlinedLabel._candidate_font_size
        not myLabel._candidate_font_size or self._candidate_font_size
    '''
    _candidate_font_size = 0

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
        if self.size[1] <= 100:
            '''
            Default size of 100 or 0 is unlikely to ever appear in the wild,
            so ignore that case to cut out half of the possible iterations.
            '''
            return
        with self.canvas.before:
            self.font_size = self.target_font_size
            self.texture_update()
            if self.texture_size[1] > self.size[1]:
                '''
                Simple interpolation search to be run if font size is too big.
                Attempts to find the largest font size which would fit in
                self.size. Candidate is estimated from the ratio of current
                height to desired height, with a fall back to binary search
                (mid point) if the estimate is obviously wrong.
                '''
                upper = self.target_font_size
                lower = self.min_font_size
                # Bootstrap using a class variable cache (if it is not 0)
                if OutlinedLabel._candidate_font_size:
                    candidate = OutlinedLabel._candidate_font_size
                else:  # Otherwise just initialize with mid-point
                    candidate = (upper + lower) // 2
                # Stop when there are no more integers to search
                while upper-lower > 1:
                    # Apply the candidate font size and test it, resetting
                    # upper and lower bounds
                    self.font_size = candidate
                    self.texture_update()
                    if self.texture_size[1] > self.size[1]:
                        upper = candidate
                    else:
                        lower = candidate
                    # Obtain newer candidate font size using interpolation
                    candidate = round(candidate * self.size[1]/self.texture_size[1])
                    if candidate >= upper or candidate <= lower:
                        # Fall back to binary if result would cause a loop
                        candidate = (upper + lower) // 2
                # At this point, upper is slightly too large (otherwise it
                # would not have been assigned as upper limit) so pick lower
                self.font_size = lower
                # Cache the selected font size value. TODO: multiple cached?
                OutlinedLabel._candidate_font_size = lower
                self.texture_update()  # Update texture to prepare for borders

            '''
            Draw borders around fonts, based on both font_size and a
            border_thickness input. Basically duplicates current texture
            which contains the text in a circle with offset according to
            border thickness.
            '''
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
