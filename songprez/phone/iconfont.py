#!/usr/bin/env python
import kivy
# kivy.require('1.9.2')
from kivy.core.text import LabelBase

"""
Fonts from https://github.com/Templarian/MaterialDesign-Webfont
"""


def icon_font_register():
        LabelBase.register(name="MaterialDesignIcons",
                           fn_regular="songprez/fonts/"
                           +"materialdesignicons-webfont.ttf")
icon_map = {'donate': u'\uf5b9',  # square-inc-cash
            'menu': u'\uf44e',  # menu
            'sets': u'\uf423',  # library
            'present': u'\uf518',  # presentation-play
            'songs': u'\uf30e',  # file-document
            'scripture': u'\uf15e',  # audiobook (WILL BE BIBLE, KEEP CHECKING WEBSITE FOR UPDATE)
            'settings': u'\uf582',  # settings
            'search': u'\uf43b',  # magnify
            'edit': u'\uf4da',  # pencil
            'save': u'\uf289',  # content-save
            'chordoff': u'\uf47b',  # music-note-off
            'delete': u'\uf2b5',  # delete
            'cancel': u'\uf250',  # close-circle
            'new': u'\uf504',  # plus
            'listadd': u'\uf501',  # playlist-plus
            'listremove': u'\uf502',  # playlist-remove
            'sort': u'\uf5a8',  # sort
            'copy': u'\uf285',  # content-copy
            'saveas': u'\uf15c',  # at
            'language': u'\uf5a9',  # alphabetical
            'showset': u'\uf36b',  # format-indent-increase
            'listmoveup': u'\uf157',  # arrow-up-bold
            'listmovedown': u'\uf145',  # arrow-down-bold
            'bibleversion': u'\uf5d3',  # sword
            'plus': u'\uf508',  # plus-circle-outline
            'transpose': u'\uf478',  # music-note
            'expand': u'\uf238',  # chevron-right
            'collapse': u'\uf236',  # chevron-down
            '0': u'\uf491',  # numeric-0-box
            '1': u'\uf494',  # numeric-1-box
            '2': u'\uf497',  # numeric-2-box
            '3': u'\uf49a',  # numeric-3-box
            '4': u'\uf49d',  # numeric-4-box
            '5': u'\uf4a0',  # numeric-5-box
            '6': u'\uf4a3',  # numeric-6-box
            '7': u'\uf4a6',  # numeric-7-box
            '8': u'\uf4a9',  # numeric-8-box
            '9': u'\uf4ac',  # numeric-9-box
            '9+': u'\uf4af',  # numeric-9-plus-box
            }

def iconfont(name, size=None):
    icon = icon_map[name]
    if size:
        try:
            float(str(size))
            size = str(int(size))
        except ValueError:
            pass
        return (u'[font=MaterialDesignIcons][size='
                + size + u']' + icon
                + u'[/size][/font]')
    else:
        return (u'[font=MaterialDesignIcons]'
                + icon
                + u'[/font]')
