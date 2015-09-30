#!/usr/bin/env python
import kivy
# kivy.require('1.9.0')
from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.uix.scrollview import ScrollView
from kivy.uix.listview import ListItemButton, ListView
from kivy.adapters.listadapter import ListAdapter

from kivy.event import EventDispatcher
from kivy.compat import PY2
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.adapters.simplelistadapter import SimpleListAdapter
from kivy.uix.abstractview import AbstractView
from kivy.properties import ObjectProperty, DictProperty, \
        NumericProperty, ListProperty, BooleanProperty
from math import ceil, floor

Builder.load_string("""
<ListView>:
    container: container
    ScrollView:
        pos: root.pos
        on_scroll_y: root._scroll(args[1])
        do_scroll_x: False
        bar_width: 20
        scroll_type: ['bars', 'content']
        effect_cls: 'ScrollEffect'
        GridLayout:
            cols: 1
            id: container
            size_hint_y: None
<ItemList>:
""")


class ItemList(ListView):
    def __init__(self, **kwargs):
        super(ItemList, self).__init__(**kwargs)
        Clock.schedule_once(self._finish_init)

    def _finish_init(self, dt):
        data = [('path', 'title '+str(i)) for i in range(100)]
        #self.set_data(data)
        #Clock.schedule_once(self._resize)

    def _resize(self, dt):
        if self.row_height:
            self.height = self.row_height*100

    def set_data(self, datalist):
        return
        self.adapter = ListAdapter(data=datalist,
                                   args_converter=args_converter,
                                   cls=ListItemButton,
                                   selection_mode='single',
                                   allow_empty_selection=False)


def args_converter(row_index, an_obj):
    app = App.get_running_app()
    return {'text': an_obj[1],
            'size_hint_y': None,
            'height': app.root.rowheight}

class ListView(AbstractView, EventDispatcher):
    ''':class:`~kivy.uix.listview.ListView` is a primary high-level widget,
    handling the common task of presenting items in a scrolling list.
    Flexibility is afforded by use of a variety of adapters to interface with
    data.

    The adapter property comes via the mixed in
    :class:`~kivy.uix.abstractview.AbstractView` class.

    :class:`~kivy.uix.listview.ListView` also subclasses
    :class:`EventDispatcher` for scrolling. The event *on_scroll_complete* is
    used in refreshing the main view.

    For a simple list of string items, without selection, use
    :class:`~kivy.adapters.simplelistadapter.SimpleListAdapter`. For list items
    that respond to selection, ranging from simple items to advanced
    composites, use :class:`~kivy.adapters.listadapter.ListAdapter`. For an
    alternate powerful adapter, use
    :class:`~kivy.adapters.dictadapter.DictAdapter`, rounding out the choice
    for designing highly interactive lists.

    :Events:
        `on_scroll_complete`: (boolean, )
            Fired when scrolling completes.
    '''

    divider = ObjectProperty(None)
    '''[TODO] Not used.
    '''

    divider_height = NumericProperty(2)
    '''[TODO] Not used.
    '''

    container = ObjectProperty(None)
    '''The container is a :class:`~kivy.uix.gridlayout.GridLayout` widget held
    within a :class:`~kivy.uix.scrollview.ScrollView` widget.  (See the
    associated kv block in the Builder.load_string() setup). Item view
    instances managed and provided by the adapter are added to this container.
    The container is cleared with a call to clear_widgets() when the list is
    rebuilt by the populate() method. A padding
    :class:`~kivy.uix.widget.Widget` instance is also added as needed,
    depending on the row height calculations.

    :attr:`container` is an :class:`~kivy.properties.ObjectProperty` and
    defaults to None.
    '''

    row_height = NumericProperty(None)
    '''The row_height property is calculated on the basis of the height of the
    container and the count of items.

    :attr:`row_height` is a :class:`~kivy.properties.NumericProperty` and
    defaults to None.
    '''

    item_strings = ListProperty([])
    '''If item_strings is provided, create an instance of
    :class:`~kivy.adapters.simplelistadapter.SimpleListAdapter` with this list
    of strings, and use it to manage a no-selection list.

    :attr:`item_strings` is a :class:`~kivy.properties.ListProperty` and
    defaults to [].
    '''

    scrolling = BooleanProperty(False)
    '''If the scroll_to() method is called while scrolling operations are
    happening, a call recursion error can occur. scroll_to() checks to see that
    scrolling is False before calling populate(). scroll_to() dispatches a
    scrolling_complete event, which sets scrolling back to False.

    :attr:`scrolling` is a :class:`~kivy.properties.BooleanProperty` and
    defaults to False.
    '''

    _index = NumericProperty(0)
    _sizes = DictProperty({})
    _count = NumericProperty(0)

    _wstart = NumericProperty(0)
    _wend = NumericProperty(-1)

    __events__ = ('on_scroll_complete', )

    def __init__(self, **kwargs):
        # Check for an adapter argument. If it doesn't exist, we
        # check for item_strings in use with SimpleListAdapter
        # to make a simple list.
        if 'adapter' not in kwargs:
            if 'item_strings' not in kwargs:
                # Could be missing, or it could be that the ListView is
                # declared in a kv file. If kv is in use, and item_strings is
                # declared there, then item_strings will not be set until after
                # __init__(). So, the data=[] set will temporarily serve for
                # SimpleListAdapter instantiation, with the binding to
                # item_strings_changed() handling the eventual set of the
                # item_strings property from the application of kv rules.
                list_adapter = SimpleListAdapter(data=[],
                                                 cls=Label)
            else:
                list_adapter = SimpleListAdapter(data=kwargs['item_strings'],
                                                 cls=Label)
            kwargs['adapter'] = list_adapter

        super(ListView, self).__init__(**kwargs)

        self._trigger_populate = Clock.create_trigger(self._spopulate, -1)
        self._trigger_reset_populate = \
            Clock.create_trigger(self._reset_spopulate, -1)

        self.bind(size=self._trigger_populate,
                  pos=self._trigger_populate,
                  item_strings=self.item_strings_changed,
                  adapter=self._trigger_populate)

        self._trigger_bind_adapter = Clock.create_trigger(
            lambda dt: self.adapter.bind_triggers_to_view(
                self._trigger_reset_populate),
            -1)
        self.bind(adapter=self._trigger_bind_adapter)

        # The bindings setup above sets self._trigger_populate() to fire
        # when the adapter changes, but we also need this binding for when
        # adapter.data and other possible triggers change for view updating.
        # We don't know that these are, so we ask the adapter to set up the
        # bindings back to the view updating function here.
        self._trigger_bind_adapter()

    # Added to set data when item_strings is set in a kv template, but it will
    # be good to have also if item_strings is reset generally.
    def item_strings_changed(self, *args):
        self.adapter.data = self.item_strings

    def _scroll(self, scroll_y):
        if self.row_height is None:
            return
        self._scroll_y = scroll_y
        scroll_y = 1 - min(1, max(scroll_y, 0))
        container = self.container
        mstart = (container.height - self.height) * scroll_y
        mend = mstart + self.height

        # convert distance to index
        rh = self.row_height
        istart = int(ceil(mstart / rh))
        iend = int(floor(mend / rh))

        istart = max(0, istart - 1)
        iend = max(0, iend - 1)

        if istart < self._wstart:
            rstart = max(0, istart - 10)
            self.populate(rstart, iend)
            self._wstart = rstart
            self._wend = iend
        elif iend > self._wend:
            self.populate(istart, iend + 10)
            self._wstart = istart
            self._wend = iend + 10

    def _spopulate(self, *args):
        self.populate()

    def _reset_spopulate(self, *args):
        self._wend = -1
        self.populate()
        # simulate the scroll again, only if we already scrolled before
        # the position might not be the same, mostly because we don't know the
        # size of the new item.
        if hasattr(self, '_scroll_y'):
            self._scroll(self._scroll_y)

    def populate(self, istart=None, iend=None):
        container = self.container
        sizes = self._sizes
        rh = self.row_height

        # ensure we know what we want to show
        if istart is None:
            istart = self._wstart
            iend = self._wend

        # clear the view
        container.clear_widgets()

        # guess only ?
        if iend is not None and iend != -1:

            # fill with a "padding"
            fh = 0
            for x in range(istart):
                fh += sizes[x] if x in sizes else rh
            container.add_widget(Widget(size_hint_y=None, height=fh))

            # now fill with real item_view
            index = istart
            while index <= iend:
                item_view = self.adapter.get_view(index)
                index += 1
                if item_view is None:
                    continue
                sizes[index] = item_view.height
                container.add_widget(item_view)
        else:
            available_height = self.height
            real_height = 0
            index = self._index
            count = 0
            while available_height > 0:
                item_view = self.adapter.get_view(index)
                if item_view is None:
                    break
                sizes[index] = item_view.height
                index += 1
                count += 1
                container.add_widget(item_view)
                available_height -= item_view.height
                real_height += item_view.height

            self._count = count

            # extrapolate the full size of the container from the size
            # of view instances in the adapter
            if count:
                container.height = \
                    real_height / count * self.adapter.get_count()
                if self.row_height is None:
                    self.row_height = real_height / count

    def scroll_to(self, index=0):
        if not self.scrolling:
            self.scrolling = True
            self._index = index
            self.populate()
            self.dispatch('on_scroll_complete')

    def on_scroll_complete(self, *args):
        self.scrolling = False
