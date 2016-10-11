#!/usr/bin/env python
import kivy
# kivy.require('1.9.0')
from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.animation import Animation
from kivy.properties import ListProperty, ObjectProperty
from twisted.internet import defer
from copy import deepcopy
from blinker import signal
from ..control.spset import SPSet
from .fontutil import iconfont
from .chordlabel import ChordLabel
from ..network.messages import GetItem

Builder.load_string("""
<MyStencil@BoxLayout+StencilView>
    padding: 0

<FakeButton@ButtonBehavior+Label>
    size_hint: None, None
    size: 2*app.buttonsize, 2*app.buttonsize
    font_size: 2*app.ui_fs_button
    markup: True
    opacity: 0.4

<AddBar>:
    pbadd: pbadd
    pbsearch: pbsearch
    pbscripture: pbscripture
    pbsave: pbsave
    pbedit: pbedit
    active: 0
    size_hint: None, None
    width: 2*app.buttonsize
    StencilView:
        width: root.width
        height: 2*app.buttonsize + (root.height-2*app.buttonsize) * root.active
        size: root.size
        x: root.x
        y: root.y
        Widget:
            canvas.before:
                Color:
                    rgba: (.125, .125, .125, 1)
                RoundedRectangle:
                    size: root.size
                    pos: root.pos
                    radius: dp(10),
            opacity: 1 if root.active else 0
        FakeButton:
            id: pbedit
            pos: root.x, root.y + 4*self.height + dp(3)
            opacity: root.active*0.6 + 0.4
        FakeButton:
            id: pbsave
            pos: root.x, root.y + 3*self.height + dp(3)
            opacity: root.active*0.6 + 0.4
        Widget:
            size: 2*app.buttonsize - dp(6), dp(3)
            opacity: root.active*0.6 + 0.4
            pos: root.x + dp(3), root.y + 6*app.buttonsize
            canvas.before:
                Color:
                    rgba: (1, 1, 1, 1)
                RoundedRectangle:
                    size: self.size
                    pos: self.pos
                    radius: dp(3),
        FakeButton:
            id: pbscripture
            pos: root.x, root.y + 2*self.height
            opacity: root.active*0.6 + 0.4
        FakeButton:
            id: pbsearch
            pos: root.x, root.y + 1*self.height
            opacity: root.active*0.6 + 0.4
        FakeButton:
            id: pbadd
            pos: root.x, root.y
            opacity: root.active*0.6 + 0.4

<TransposeBar>:
    pbviewchords: pbviewchords
    pbtranspose: pbtranspose
    slider: slider
    apply: None
    active: 0
    size_hint: None, None
    height: 2*app.buttonsize
    StencilView:
        height: root.height
        width: 2*app.buttonsize + (root.width-2*app.buttonsize) * root.active
        x: root.x + (root.width-2*app.buttonsize) * (1-root.active)
        y: root.y
        Widget:
            canvas.before:
                Color:
                    rgba: (.125, .125, .125, 1)
                RoundedRectangle:
                    size: root.size
                    pos: root.pos
                    radius: dp(10),
            opacity: 1 if root.active else 0
        FakeButton:
            id: pbviewchords
            pos: root.x, root.y
            opacity: root.active*0.6 + 0.4
        Label:
            id: transposelabel
            text: ("+" if slider.value > 0 else "") + str(int(slider.value))
            font_size: app.ui_fs_main
            size_hint: None, None
            size: self.texture_size
            x: int(slider.x + slider.width/2 - self.width/2)
            y: slider.y + slider.height
        Slider:
            id: slider
            range: -6, 6
            step: 1
            size_hint: None, None
            width: root.width - pbviewchords.width - pbtranspose.width
            height: app.buttonsize
            pos: root.x + 2*app.buttonsize, root.y + dp(5)
            on_value: root.transpose(self.value) if root.active else 0
        FakeButton:
            id: pbtranspose
            pos: root.x + root.width - self.width, root.y
            opacity: root.active*0.6 + 0.4

<PresentScreen>:
    carousel: carousel
    sendMessage: app.sendMessage
    BoxLayout:
        padding: '10dp'
        MyStencil:
            FloatLayout:
                Carousel:
                    id: carousel
                    size: self.parent.size
                    pos: self.parent.pos
                AddBar:
                    height: self.parent.height - 2*dp(10) - 2*app.buttonsize
                    x: self.parent.x + self.parent.width - 2*app.buttonsize - dp(10)
                    y: dp(10) + 2*app.buttonsize
                    search: root.search
                    scripture: root.scripture
                    save: root.save
                    edit: root.edit
                TransposeBar:
                    width: self.parent.width - 2*dp(10)
                    pos: self.parent.x + dp(10), dp(10)
                    transpose: root.transpose
                    apply: root.apply
""")


class AddBar(Widget):
    def __init__(self, **kwargs):
        super(AddBar, self).__init__(**kwargs)
        Clock.schedule_once(self._finish_init)

    def _finish_init(self, dt):
        self.pbadd.text = iconfont('plus')
        self.pbsearch.text = iconfont('search')
        self.pbscripture.text = iconfont('scripture')
        self.pbsave.text = iconfont('save')
        self.pbedit.text = iconfont('edit')

    def _animate_in(self):
        anim = Animation(active=1, d=0.2)
        anim.start(self)

    def _animate_out(self):
        anim = Animation(active=0, d=0.2)
        anim.start(self)

    def on_touch_down(self, touch):
        if self.active:
            if not self.collide_point(*touch.pos):
                self._animate_out()
            elif self.pbsearch.collide_point(*touch.pos):
                self.search()
                return True
            elif self.pbscripture.collide_point(*touch.pos):
                self.scripture()
                return True
            elif self.pbsave.collide_point(*touch.pos):
                self.save()
                return True
            elif self.pbedit.collide_point(*touch.pos):
                self.edit()
                return True
        if self.pbadd.collide_point(*touch.pos):
            if self.active:
                self._animate_out()
            else:
                self._animate_in()
            return True
        super(AddBar, self).on_touch_down(touch)
        return False

class TransposeBar(Widget):
    def __init__(self, **kwargs):
        super(TransposeBar, self).__init__(**kwargs)
        Clock.schedule_once(self._finish_init)

    def _finish_init(self, dt):
        self.pbviewchords.text = iconfont('chordoff')
        self.pbtranspose.text = iconfont('transpose')

    def _animate_in(self):
        self.slider.value = 0
        anim = Animation(active=1, d=0.2)
        anim.start(self)

    def _animate_out(self):
        anim = Animation(active=0, d=0.2)
        anim.start(self)
        if self.slider.value != 0:
            self.apply(self.slider.value)
            self.slider.value = 0

    def on_touch_down(self, touch):
        if self.active:
            if not self.collide_point(*touch.pos):
                self._animate_out()
            elif self.pbviewchords.collide_point(*touch.pos):
                print('turn off/on chords')
                return True
            elif self.slider.collide_point(*touch.pos):
                return self.slider.on_touch_down(touch)
        if self.pbtranspose.collide_point(*touch.pos):
            if self.active:
                self._animate_out()
            else:
                self._animate_in()
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

    def search(self):
        app = App.get_running_app()
        app.base.to_screen('search')

    def scripture(self):
        app = App.get_running_app()
        app.base.to_screen('scripture')

    def save(self):
        pass

    def edit(self):
        pass
