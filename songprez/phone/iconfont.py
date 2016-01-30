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
            'copy': u'\uf285',  # content-copy
            'saveas': u'\uf15c',  # at
            'language': u'\uf5a9',  # alphabetical
            'showset': u'\uf36b',  # format-indent-increase
            'listmoveup': u'\uf157',  # arrow-up-bold
            'listmovedown': u'\uf145',  # arrow-down-bold
            'bibleversion': u'\uf5d3',  # sword
            'plus': u'\uf508',  # plus-circle-outline
            'transpose': u'\uf478',  # music-note
            }

def iconfont(name, size=None):
    icon = icon_map[name]
    if size:
        return (u'[font=MaterialDesignIcons][size='
                + size + u']' + icon
                + u'[/size][/font]')
    else:
        return (u'[font=MaterialDesignIcons]'
                + icon
                + u'[/font]')
