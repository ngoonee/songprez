#!/usr/bin/env python
import kivy
# kivy.require('1.9.0')
from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.bubble import Bubble
from kivy.properties import BooleanProperty, StringProperty, ObjectProperty
import string

Builder.load_string("""
<AlphaChar>:
    padding_x: 8
<AlphabetList>:
    _realLayout: realLayout.__self__
    orientation: "vertical"
    size_hint_x: None
    width: realLayout.width
    BoxLayout:
        id: realLayout
        orientation: "vertical"
        pos_hint: {'x': 0, 'y': 0}
""")

class AlphaChar(Label):
    def set_char(self, char):
        self.text = char

    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            self.parent.parent.char_selected(self.text)
            self.parent.parent.close_bubble()
            return True

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.parent.parent.char_mouseover(self.text, touch, max(self.texture_size))
            return True

    def on_touch_move(self, touch):
        if self.collide_point(*touch.pos):
            self.parent.parent.char_mouseover(self.text, touch, max(self.texture_size))
            return True
        elif not self.parent.collide_point(*touch.pos):
            self.parent.parent.close_bubble()


class AlphabetList(FloatLayout):
    monitor = BooleanProperty(False)
    selected_char = StringProperty("")
    _realLayout = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(AlphabetList, self).__init__(**kwargs)
        self.popup = Bubble(arrow_pos="right_mid", size_hint=(None, None),
                            size=(0, 0))
        self.popupLabel = Label(text="", bold=True, font_size=3,
                                padding=(0, 0))
        self.popupLabel.size = self.popupLabel.texture_size
        self.popup.add_widget(self.popupLabel)
        self.add_widget(self.popup)
        app = App.get_running_app()
        # Respond to change in system font size
        app.bind(systemFontSize=self.on_height)
        Clock.schedule_once(self._finish_init)

    def _finish_init(self, dt):
        chars = list(string.ascii_uppercase)
        chars.insert(0, "#")
        for c in chars:
            a = AlphaChar()
            a.set_char(c)
            a.texture_update()
            a.size = a.texture_size
            self._realLayout.add_widget(a)
        
    def on_height(self, instance, value):
        if self._realLayout and len(self._realLayout.children) and self.height:
            app = App.get_running_app()
            font_size = app.config.getint('interface', 'fontsize')
            ratio = 1
            max_width = 0
            if self.height < self._realLayout.children[0].texture_size[1]*27:
                ratio = self.height / (self._realLayout.children[0].texture_size[1]*27.0)
            for c in self._realLayout.children:
                c.font_size = ratio * font_size
                c.texture_update()
                if c.texture_size[0] > max_width:
                    max_width = c.texture_size[0]
            self._realLayout.width = max_width

    def char_selected(self, c):
        if self.selected_char != c:
            self.take_action(c)
        self.selected_char = c

    def char_mouseover(self, c, touch, min_dimension):
        self.char_selected(c)
        self.monitor = True
        self.popupLabel.text = c
        min_d = int(min_dimension*2)
        self.popupLabel.font_size = min_d
        self.popupLabel.size = (min_d*1.5, min_d*1.5)
        self.popup.size = (min_d*1.5, min_d*1.5)
        self.popup.pos = (touch.pos[0] - min_d*1.3,
                          touch.pos[1] - min_d/1.4)

    def close_bubble(self):
        if self.monitor:
            self.popup.size = (0, 0)
            self.popupLabel.size = (0, 0)
            self.popupLabel.font_size = 0
            self.monitor = False

    def take_action(self, c):
        print("Do the action for letter", c)
