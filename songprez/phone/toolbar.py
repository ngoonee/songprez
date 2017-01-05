# -*- coding: utf-8 -*-
from kivy.app import App
from kivy.lang import Builder
from kivy.properties import BooleanProperty
from kivymd.toolbar import Toolbar
from kivy.uix.stencilview import StencilView


Builder.load_string("""
<SPToolbar>:
""")

class SPToolbar(Toolbar, StencilView):
    hidden = BooleanProperty(False)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            if not super(SPToolbar, self).on_touch_down(touch):
                app = App.get_running_app()
                app.base.hide_toolbar()
            return True
        return False
