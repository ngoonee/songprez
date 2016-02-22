#!/usr/bin/env python
import kivy
# kivy.require('1.9.0')
from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.uix.stencilview import StencilView
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.selectableview import SelectableView
from kivy.properties import StringProperty, ObjectProperty, ListProperty
from kivy.properties import NumericProperty, BooleanProperty
from .iconfont import iconfont
from kivy.garden.recycleview import RecycleView, RecycleViewMixin
from kivy.metrics import dp
from kivy.animation import Animation

Builder.load_string("""
<SPRecycleView>:
    canvas.before:
        Color:
            rgba: (.125, .125, .125, 1)
        RoundedRectangle:
            size: self.size
            pos: self.pos
            radius: dp(10),
    key_viewclass: 'viewclass'
    key_size: 'height'

<ListItem>:
    title_fs: app.ui_fs_main
    detail_fs: app.ui_fs_detail
    button_fs: app.ui_fs_button
    buttonsize: app.buttonsize

    title: title
    expand: expand
    subtitle: subtitle
    edit: edit
    delete: delete
    move_up: move_up
    move_down: move_down
    scripture: scripture
    remove_item: remove_item
    add_item: add_item
    canvas.before:
        Color:
            rgba: (.25, .25, .25, 1) if self.index % 2 else (.125, .125, .125, 1)
        RoundedRectangle:
            size: self.size
            pos: self.pos
            radius: dp(10),
        Color:
            rgba: 0, 0, 0, 1
        Line:
            rounded_rectangle: [self.pos[0], self.pos[1], self.size[0], self.size[1], 5]
    Label:
        id: title
        size_hint: None, None
        halign: 'left'
        text: root.titletext
        shorten: True
        shorten_from: 'right'
        font_size: root.title_fs
    Label:
        id: expand
        size_hint: None, None
        size: root.buttonsize, root.buttonsize
        font_size: root.button_fs
        markup: True
        canvas.before:
            PushMatrix
            Rotate:
                angle: root.expand_angle
                origin: self.center
        canvas.after:
            PopMatrix
    Label:
        id: edit
        size_hint: None, None
        size: root.buttonsize, root.buttonsize
        font_size: root.button_fs
        markup: True
        opacity: root.button_opacity
    Label:
        id: delete
        size_hint: None, None
        size: root.buttonsize, root.buttonsize
        font_size: root.button_fs
        markup: True
        opacity: root.button_opacity
    Label:
        id: subtitle
        font_size: root.detail_fs
        size_hint: None, None
        halign: 'left'
        text: root.subtitletext
        shorten: True
        shorten_from: 'right'
        markup: True
    Label:
        id: move_up
        size_hint: None, None
        size: root.buttonsize*1.5, root.buttonsize*1.5
        font_size: root.button_fs*1.5
        markup: True
    Label:
        id: move_down
        size_hint: None, None
        size: root.buttonsize*1.5, root.buttonsize*1.5
        font_size: root.button_fs*1.5
        markup: True
    Label:
        id: scripture
        size_hint: None, None
        size: root.buttonsize*1.5, root.buttonsize*1.5
        font_size: root.button_fs*1.5
        markup: True
    Label:
        id: remove_item
        size_hint: None, None
        size: root.buttonsize*1.5, root.buttonsize*1.5
        font_size: root.button_fs*1.5
        markup: True
    Label:
        id: add_item
        size_hint: None, None
        size: root.buttonsize*1.5, root.buttonsize*1.5
        font_size: root.button_fs*1.5
        markup: True
""")


class SPRecycleView(RecycleView):
    edit_action = ObjectProperty(None)
    delete_action = ObjectProperty(None)
    selection = NumericProperty(-1)
    oldselection = NumericProperty(-1)

    def __init__(self, **kwargs):
        super(SPRecycleView, self).__init__(**kwargs)

    def on_selection(self, instance, value):
        if self.oldselection > -1:
            view = self.adapter.get_view(self.oldselection)
            view.is_selected = False
            self.oldselection = -1
        if value > -1:
            view = self.adapter.get_view(value)
            self.oldselection = value


class ListItem(SelectableView, RecycleViewMixin, FloatLayout, StencilView):
    titletext = StringProperty('')
    subtitletext = StringProperty('')
    summarytext = ListProperty([])
    rv = ObjectProperty(None)
    expand_angle = NumericProperty(0)
    button_opacity = NumericProperty(0)
    set_edit = BooleanProperty(False)
    _summary = ListProperty([])

    def __init__(self, **kwargs):
        super(ListItem, self).__init__(**kwargs)
        self.expand.text = iconfont('expand')
        self.edit.text = iconfont('edit')
        self.delete.text = iconfont('delete')
        for i in range(5):
            self._summary.append(Label(font_size=self.detail_fs,
                                      size_hint=(None, None),
                                      halign='left',
                                      shorten=True,
                                      shorten_from='right',
                                      markup=True))
            self.add_widget(self._summary[i])
        self.move_up.text = iconfont('listmoveup')
        self.move_down.text = iconfont('listmovedown')
        self.scripture.text = iconfont('scripture')
        self.remove_item.text = iconfont('listremove')
        self.add_item.text = iconfont('listadd')

    def on_summarytext(self, instance, value):
        for i in range(5):
            self._summary[i].text = ''
        for i, v in enumerate(value):
            self._summary[i].text = v

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            if self.is_selected:
                if self.edit.collide_point(*touch.pos):
                    self.rv.edit_action(self.index)
                    return True
                elif self.delete.collide_point(*touch.pos):
                    self.rv.delete_action(self.index)
                    return True
                elif self.set_edit:
                    if self.move_up.collide_point(*touch.pos):
                        self.rv.move_up_action(self.index)
                        return True
                    if self.move_down.collide_point(*touch.pos):
                        self.rv.move_down_action(self.index)
                        return True
                    if self.scripture.collide_point(*touch.pos):
                        self.rv.scripture_action(self.index)
                        return True
                    if self.remove_item.collide_point(*touch.pos):
                        self.rv.remove_item_action(self.index)
                        return True
                    if self.add_item.collide_point(*touch.pos):
                        self.rv.add_item_action(self.index)
                        return True
            # The below is if nothing matches above
            self.is_selected = not self.is_selected
            return True
        return super(ListItem, self).on_touch_down(touch)

    def update_height(self):
        height = dp(5) + self.title_fs*1.5 + dp(5)
        if self.subtitletext:
            height += self.detail_fs*1.5
        if self.is_selected:
            count = [1 for w in self._summary if w.text != '']
            height_diff = len(count)*self.detail_fs*1.5 + dp(5)
            if height_diff < 2*self.buttonsize:
                # Too few summary lines
                height_diff = 2*self.buttonsize + dp(5)
                if self.is_selected:
                    height_diff -= self.detail_fs*1.5
            if self.set_edit:
                height_diff += 1.5*self.buttonsize
            height = int(height + height_diff)
            angle = -90
            opacity = 1
        else:
            height = int(height)
            angle = 0
            opacity = 0
        anim = Animation(height=height, d=0.2)
        anim &= Animation(expand_angle=angle, d=0.2)
        anim &= Animation(button_opacity=opacity, d=0.2)
        anim.start(self)

    def on_is_selected(self, instance, value):
        self.rv.selection = self.index if value else -1
        self.update_height()

    def on_expand_angle(self, instance, value):
        if self.rv.data[self.index]['expand_angle'] != value:
            self.rv.data[self.index]['expand_angle'] = value

    def on_height(self, instance, value):
        if self.rv.data[self.index]['height'] != value:
            self.rv.data[self.index]['height'] = value
            self.rv.refresh_views(data=True)

    def refresh_view_layout(self, rv, index, pos, size, viewport):
        '''
        Efficiency here is paramount, this gets called a LOT.
        
        For now, what is important is the changes in pos and size. pos changes
        often (and for many items at once) while scrolling, while size only
        changes with resizing (not an issue on mobile) or animating height
        changes (and then only one item at a time).

        In ascii art, here's how things look
        ----------------------------------------------------------------------
            title                                                  | expand
                subtitle                                           |
        --------------------------- base_y -----------------------------------
                    summary[0]                                     | edit
                    summary[1]                                     | delete
                    ...                                            |
                    summary[n]                                     |
        ----------------------------------------------------------------------
                                                                   ^
                                                                   |
                                                                rightbar_x
        '''
        base_y = pos[1] + size[1] - dp(5) - self.title_fs*1.5 - dp(5)
        rightbar_x = pos[0] + size[0] - dp(10) - self.buttonsize
        if self.subtitletext:
            base_y -= self.detail_fs*1.5
        if self.subtitletext:
            expand_pos = (int(rightbar_x),
                          int(base_y + self.detail_fs*1.5))
        else:
            expand_pos = (int(pos[0] + size[0] - dp(10) - self.buttonsize),
                          int(base_y))
        self.expand.pos = expand_pos
        edit_pos = (int(rightbar_x), int(expand_pos[1] - self.buttonsize))
        self.edit.pos = edit_pos
        delete_pos = (int(rightbar_x), int(edit_pos[1] - self.buttonsize))
        self.delete.pos = delete_pos
        if self.subtitletext:
            title_pos = (int(pos[0] + dp(10)), int(base_y + dp(5) + self.detail_fs*1.5))
        else:
            title_pos = (int(pos[0] + dp(10)), int(base_y + dp(5)))
        self.title.pos = title_pos
        subtitle_pos = (int(pos[0] + dp(20)), int(base_y + dp(5)))
        self.subtitle.pos = subtitle_pos
        summary_pos = (int(pos[0] + dp(30)), int(base_y))
        for i in range(len(self.summarytext)):
            summary_pos = (summary_pos[0], int(summary_pos[1] - self.detail_fs*1.5))
            self._summary[i].pos = summary_pos
        if tuple(size) != tuple(self.size):
            title_size = (int(size[0] - dp(10) - dp(10) - self.buttonsize),
                          int(self.title_fs * 1.5))
            self.title.size = title_size
            self.title.text_size = title_size
            subtitle_size = (int(size[0] - dp(20) - dp(10) - self.buttonsize),
                             int(self.title_fs * 1.5))
            self.subtitle.size = subtitle_size
            self.subtitle.text_size = subtitle_size
            for i in range(len(self.summarytext)):
                self._summary[i].size = subtitle_size
                self._summary[i].text_size = subtitle_size
        if len(self._summary):
            last_y = summary_pos[1]
        else:
            last_y = base_y
        pos_y = last_y - 1.5*self.buttonsize
        intra_x = (rightbar_x - 5*1.5*self.buttonsize)/6
        self.move_up.pos = (int(intra_x), int(pos_y))
        self.move_down.pos = (int(1.5*self.buttonsize + 2*intra_x), int(pos_y))
        self.scripture.pos = (int(3*self.buttonsize + 3*intra_x), int(pos_y))
        self.remove_item.pos = (int(4.5*self.buttonsize + 4*intra_x), int(pos_y))
        self.add_item.pos = (int(6*self.buttonsize + 5*intra_x), int(pos_y))
        super(ListItem, self).refresh_view_layout(rv, index, pos, size, viewport)
