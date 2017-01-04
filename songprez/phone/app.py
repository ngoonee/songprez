#!/usr/bin/env python
import kivy
# kivy.require('1.9.2')
from kivy.config import Config
Config.set('kivy', 'desktop', 0)
Config.set('kivy', 'keyboard_mode', "")
# install_twisted_rector must be called before importing the reactor, so do
# it here before anything else is loaded
from kivy.support import install_twisted_reactor
install_twisted_reactor()
from twisted.internet import reactor
from twisted.internet.endpoints import clientFromString
import os
import logging
logger = logging.getLogger(__name__)
from kivy.app import App
from kivy.clock import Clock
from kivy.properties import StringProperty, BooleanProperty, ListProperty
from kivy.properties import NumericProperty, ObjectProperty, DictProperty
from kivy.metrics import dp, sp
from kivymd.theming import ThemeManager
from ..control.spservercontrol import SPServerControl
from ..control.spclientcontrol import SPClientControl
from .basewidget import BaseWidget
from .navdrawer import SPNavDrawer
from .settings import SPSettings
from .settingsjson import default_settings, build_settings
from ..network.spdiscovery import SPDiscovery
from .fontutil import font_register

# Monkey patch to use Noto Sans rather than kivymd's default Roboto
from kivymd.label import MDLabel
MDLabel._font_styles = DictProperty({'Body1': ['NotoSans', False, 14, 13],
                                 'Body2': ['NotoSans', True, 14, 13],
                                 'Caption': ['NotoSans', False, 12, None],
                                 'Subhead': ['NotoSans', False, 16, 15],
                                 'Title': ['NotoSans', True, 20, None],
                                 'Headline': ['NotoSans', False, 24, None],
                                 'Display1': ['NotoSans', False, 34, None],
                                 'Display2': ['NotoSans', False, 45, None],
                                 'Display3': ['NotoSans', False, 56, None],
                                 'Display4': ['NotoSans', False, 112, None],
                                 'Button': ['NotoSans', True, 14, None],
                                 'Icon': ['Icons', False, 24, None]})
from kivymd.textfields import MDTextField
MDTextField.font_name = StringProperty('NotoSans')

# Monkey patch to allow adding icontextbutton
from kivymd.dialog import MDDialog
from .icontextbutton import IconTextButton
def add_icontext_button(self, text, icon, action=None):
    button = IconTextButton(text=text,
                            icon=icon,
                            size_hint=(None, None))
    if action:
        button.bind(on_release=action)
    self._action_buttons.append(button)
def _update_action_buttons(self, *args):
    self._action_area.clear_widgets()
    for btn in self._action_buttons:
        if isinstance(btn, IconTextButton):
            if btn.text == 'delete':
                btn.md_bg_color = (1., 0., 0., 1.)
            elif btn == self._action_buttons[-1]:
                btn.md_bg_color = self.theme_cls.accent_color
            else:
                btn.md_bg_color = self.theme_cls.primary_color
        self._action_area.add_widget(btn)
MDDialog.add_icontext_button = add_icontext_button
MDDialog._update_action_buttons = _update_action_buttons

# Monkey patch to allow touch_multiselect/multiselect from
# CompoundSelectionBehavior to work with RecycleView's
# LayoutSelectionBehavior
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
def select_node(self, node):
    super(LayoutSelectionBehavior, self).select_node(node)
def on_selected_nodes(self, grid, nodes):
    for node in nodes:
        view = self.recycleview.view_adapter.get_visible_view(node)
        if view is not None:
            self.apply_selection(node, view, True)
LayoutSelectionBehavior.select_node = select_node
LayoutSelectionBehavior.on_selected_nodes = on_selected_nodes

class SongPrezApp(App):
    base = ObjectProperty(None)
    nav_drawer = ObjectProperty(None)
    dataDir = StringProperty('')
    indexDir = StringProperty('')
    sendMessage = ObjectProperty(None)
    buttonsize = NumericProperty(dp(32))
    theme_cls = ThemeManager()
    ui_fs_button = NumericProperty(sp(24))
    ui_fs_title = NumericProperty(sp(24))
    ui_fs_main = NumericProperty(sp(18))
    ui_fs_detail = NumericProperty(sp(15))

    def build(self):
        self.settings_cls = SPSettings
        self.server = None
        self.client = None
        self.seeker = None
        font_register()
        self.base = BaseWidget()
        self.nav_drawer = SPNavDrawer(side='right')
        self.theme_cls.theme_style = 'Dark'
        self.theme_cls.primary_palette = 'Teal'
        self.theme_cls.primary_hue = '800'
        self.theme_cls.primary_light_hue = '600'
        self.theme_cls.primary_dark_hue = '900'
        self.theme_cls.accent_palette = 'Green'
        Clock.schedule_once(self._verify_server)
        return self.base

    def _verify_server(self, dt):
        '''
        If previously been run and properly set up, just go straight in
        If not properly set up, need to either join other host or set up local
        '''
        try:
            indexDir = self.config.get("general", "indexdir")
            dataDir = self.config.get("general", "datadir")
            self.server = SPServerControl(indexDir, dataDir)
            self.client = SPClientControl()
            self.seeker = SPDiscovery()
        except Exception as e:
            logger.exception(e.message)
            self.base.to_screen('settings')
            title = 'Could not start service'
            message = 'Please set up the SongPrez media folder.'
            content = MDLabel(font_style='Body1',
                              theme_text_color='Secondary',
                              text=message,
                              size_hint_y=None,
                              valign='top')
            content.bind(texture_size=content.setter('size'))
            dialog = MDDialog(title=title,
                              content=content,
                              size_hint=(.8, .6),
                              auto_dismiss=True)
            dialog.open()

    def on_pause(self):
        return True

    def on_resume(self):
        pass

    def on_stop(self):
        pass

    def _control_loaded(self):
        pass

    def get_application_config(self):
        return os.path.join(self.user_data_dir, 'songprez.ini')

    def build_config(self, config):
        default_settings(config)

    def build_settings(self, settings):
        build_settings(settings, self.config)

    def on_config_change(self, config, section,
                         key, value):
        logger.debug('App: key %s in section %s is now %s',
                     key, section, value)

    def display_settings(self, settings):
        screen = self.base.sm.get_screen('settings')
        if settings not in screen.children:
            screen.add_widget(settings)

    def close_settings(self, *largs):
        super(SongPrezApp, self).close_settings(*largs)
        if not self.server:
            Clock.schedule_once(self._verify_server)
        if len(largs) and largs[0] is self._app_settings:
            # Called using close button
            self.base.back()
            return True
