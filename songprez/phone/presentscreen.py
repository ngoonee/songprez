#!/usr/bin/env python
import kivy
# kivy.require('1.9.0')
from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.animation import Animation
from kivy.properties import ListProperty, ObjectProperty
from twisted.internet import defer
from copy import deepcopy
from blinker import signal
from kivymd.theming import ThemableBehavior
from kivymd.slider import MDSlider
from kivymd import snackbar as Snackbar
from ..control.spset import SPSet
from .chordlabel import ChordLabel
from ..network.messages import GetItem

Builder.load_string("""
<MyStencil@BoxLayout+StencilView>
    padding: 0

<AddBar>:
    pbadd: pbadd
    pbsearch: pbsearch
    pbscripture: pbscripture
    pbsave: pbsave
    pbedit: pbedit
    active: 0
    size_hint: None, None
    width: dp(48)
    height: addbox.minimum_height
    StencilView:
        width: root.width
        height: dp(48) + (root.height-dp(48)) * root.active
        x: root.x
        y: root.y
        Widget:
            canvas.before:
                Color:
                    rgba: root.theme_cls.bg_light
                RoundedRectangle:
                    size: root.size
                    pos: root.pos
                    radius: dp(10),
            opacity: 1 if root.active else 0
        BoxLayout:
            id: addbox
            orientation: 'vertical'
            pos: root.pos
            MDIconButton:
                id: pbedit
                opacity: root.active*0.6 + 0.4
                icon: 'pencil'
                on_release: root.edit()
            MDIconButton:
                id: pbsave
                opacity: root.active*0.6 + 0.4
                icon: 'content-save'
                on_release: root.save()
            Widget:
                size_hint: None, None
                size: root.width, dp(2)
                opacity: root.active*0.6 + 0.4
                canvas.before:
                    Color:
                        rgba: root.theme_cls.divider_color
                    RoundedRectangle:
                        size: self.width - dp(8), dp(2)
                        pos: self.x + dp(4), self.y
                        radius: dp(2),
            MDIconButton:
                id: pbscripture
                opacity: root.active*0.6 + 0.4
                icon: 'bible'
                on_release: root.scripture()
            MDIconButton:
                id: pbsong
                opacity: root.active*0.6 + 0.4
                icon: 'file-document'
                on_release: root.song()
            MDIconButton:
                id: pbsearch
                opacity: root.active*0.6 + 0.4
                icon: 'magnify'
                on_release: root.search()
            MDIconButton:
                id: pbadd
                opacity: root.active*0.6 + 0.4
                icon: 'plus'
                on_release: root.add()

<TransposeBar>:
    pbviewchords: pbviewchords
    pbtranspose: pbtranspose
    slider: slider
    apply: None
    active: 0
    size_hint: None, None
    height: dp(60)
    StencilView:
        height: root.height
        width: dp(48) + (root.width-dp(48)) * root.active
        x: root.x + (root.width-dp(48)) * (1-root.active)
        y: root.y
        Widget:
            canvas.before:
                Color:
                    rgba: root.theme_cls.bg_light
                RoundedRectangle:
                    size: root.size
                    pos: root.pos
                    radius: dp(10),
            opacity: 1 if root.active else 0
        MDLabel:
            id: transposelabel
            text: ("+" if slider.value > 0 else "") + str(int(slider.value))
            font_style: 'Subhead'
            size_hint: None, None
            size: self.texture_size
            x: int(slider.x + slider.width/2 - self.width/2)
            y: slider.y + slider.height
            theme_text_color: 'Primary'
            opacity: root.active*0.6 + 0.4
        MDSlider:
            id: slider
            range: -6, 6
            step: 1
            size_hint: None, None
            width: root.width - pbviewchords.width - pbtranspose.width
            height: dp(48)
            pos: root.x + dp(48), root.y + dp(8)
            on_value: root.transpose(self.value) if root.active else 0
            show_off: False
            opacity: root.active*0.6 + 0.4
        MDIconButton:
            id: pbviewchords
            pos: root.x, root.y + dp(6)
            opacity: root.active*0.6 + 0.4
            icon: 'music-note-off'
        MDIconButton:
            id: pbtranspose
            pos: root.x + root.width - self.width, root.y + dp(6)
            opacity: root.active*0.6 + 0.4
            icon: 'music-note'

<PresentScreen>:
    carousel: carousel
    addbar: addbar
    transposebar: transposebar
    BoxLayout:
        padding: '10dp'
        MyStencil:
            FloatLayout:
                Carousel:
                    id: carousel
                    size: self.parent.size
                    pos: self.parent.pos
                AddBar:
                    id: addbar
                    x: self.parent.x + self.parent.width - dp(56)
                    y: dp(16) + dp(48)
                    search: root.search
                    song: root.song
                    scripture: root.scripture
                    save: root.save
                    edit: root.edit
                TransposeBar:
                    id: transposebar
                    width: self.parent.width - dp(16)
                    pos: self.parent.x + dp(8), dp(8)
                    transpose: root.transpose
                    apply: root.apply
""")


class AddBar(ThemableBehavior, Widget):
    def __init__(self, **kwargs):
        super(AddBar, self).__init__(**kwargs)
        Clock.schedule_once(self._finish_init)

    def _finish_init(self, dt):
        self.pbadd.content.font_size = dp(32)
        self.pbsearch.content.font_size = dp(32)
        self.pbscripture.content.font_size = dp(32)
        self.pbsave.content.font_size = dp(32)
        self.pbedit.content.font_size = dp(32)

    def animate_in(self):
        anim = Animation(active=1, d=0.2)
        anim.start(self)

    def animate_out(self):
        anim = Animation(active=0, d=0.2)
        anim.start(self)

    def on_touch_down(self, touch):
        if self.active:
            if not self.collide_point(*touch.pos):
                self.animate_out()
        if self.pbadd.collide_point(*touch.pos):
            if self.active:
                self.animate_out()
            else:
                self.animate_in()
            return True
        super(AddBar, self).on_touch_down(touch)
        return False

class TransposeBar(ThemableBehavior, Widget):
    def __init__(self, **kwargs):
        super(TransposeBar, self).__init__(**kwargs)
        Clock.schedule_once(self._finish_init)

    def _finish_init(self, dt):
        self.pbviewchords.content.font_size = dp(32)
        self.pbtranspose.content.font_size = dp(32)

    def animate_in(self):
        self.slider.value = 0
        anim = Animation(active=1, d=0.2)
        anim.start(self)

    def animate_out(self):
        anim = Animation(active=0, d=0.2)
        anim.start(self)
        if self.slider.value != 0:
            self.apply(self.slider.value)
            self.slider.value = 0

    def on_touch_down(self, touch):
        if self.active:
            if not self.collide_point(*touch.pos):
                self.animate_out()
            elif self.pbviewchords.collide_point(*touch.pos):
                print('turn off/on chords')
                return True
            elif self.slider.collide_point(*touch.pos):
                return self.slider.on_touch_down(touch)
        if self.pbtranspose.collide_point(*touch.pos):
            if self.active:
                self.animate_out()
            else:
                self.animate_in()
            return True
        super(TransposeBar, self).on_touch_down(touch)
        return False


class PresentScreen(Screen):
    itemlist = ListProperty([])
    
    def __init__(self, **kwargs):
        super(PresentScreen, self).__init__(**kwargs)
        Clock.schedule_once(self._finish_init)

    def _finish_init(self, dt):
        signal('curSet').connect(self.change_set)

    @defer.inlineCallbacks
    def change_set(self, sender=None):
        app = App.get_running_app()
        curSet = app.client.curSet
        carousel = self.carousel
        if curSet and isinstance(curSet, SPSet):
            itemlist = []
            carousel.clear_widgets()
            for item in curSet.list_songs():
                e = yield app.client.get_item('song', relpath=item['filepath'])
                itemlist.append(e)
                s = ChordLabel()
                carousel.add_widget(s)
                s.text = e.lyrics
            self.itemlist = itemlist

    @defer.inlineCallbacks
    def add_item(self, itemtype, relpath):
        app = App.get_running_app()
        carousel = self.carousel
        index = carousel.index + 1 if carousel.index else 0
        e = yield app.client.get_item('song', relpath=relpath)
        self.itemlist.insert(index, e)
        s = ChordLabel()
        carousel.add_widget(s, index)
        s.text = e.lyrics
        carousel.index = index

    def transpose(self, interval):
        # A temporary transposition of this item
        carousel = self.carousel
        index = carousel.index
        if index is not None:
            song = deepcopy(self.itemlist[index])
            song.transpose(interval)
            carousel.remove_widget(carousel.current_slide)
            s = ChordLabel()
            carousel.add_widget(s, index)
            s.text = song.lyrics
    
    def apply(self, interval):
        # Apply the transposition to the actual item in itemlist
        carousel = self.carousel
        index = carousel.index
        if index is not None:
            song = self.itemlist[index]
            song.transpose(interval)
            carousel.remove_widget(carousel.current_slide)
            s = ChordLabel()
            carousel.add_widget(s, index)
            s.text = song.lyrics

    def song(self):
        self.addbar.animate_out()
        app = App.get_running_app()
        app.base.to_screen('songs')
    
    def search(self):
        self.addbar.animate_out()
        app = App.get_running_app()
        app.base.to_screen('search')

    def scripture(self):
        self.addbar.animate_out()
        app = App.get_running_app()
        app.base.to_screen('scripture')

    def save(self):
        self.addbar.animate_out()

    def edit(self):
        self.addbar.animate_out()

    def on_parent(self, instance, parent):
        app = App.get_running_app()
        if parent:
            app.base.hide_toolbar()
            notification = ("Double-tap anywhere to show Toolbar")
            Snackbar.make(notification)
        else:
            app.base.show_toolbar()
