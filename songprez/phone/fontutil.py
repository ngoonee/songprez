#!/usr/bin/env python
import kivy
import os
# kivy.require('1.9.2')
from kivy.core.text import LabelBase

"""
Material Icon Fonts from https://github.com/Templarian/MaterialDesign-Webfont
"""


def font_register():
    iconfont = os.path.join('songprez', 'resources', 'fonts',
                                'materialdesignicons-webfont.ttf')
    notosans = os.path.join('songprez', 'resources', 'fonts',
                            'NotoSansCJK-Regular.ttc')
    if not os.path.exists(notosans):
        notosans = os.path.join('songprez', 'resources', 'fonts',
                                'NotoSans-Regular.ttf')
    notosansmono = os.path.join('songprez', 'resources', 'fonts',
                                'NotoSansMonoCJKsc-Regular.otf')
    if not os.path.exists(notosansmono):
        notosansmono = os.path.join('songprez', 'resources', 'fonts',
                                    'DroidSansMono.ttf')
    LabelBase.register(name="IconFonts", fn_regular=iconfont)
    LabelBase.register(name="NotoSans", fn_regular=notosans)
    LabelBase.register(name="NotoSansMono", fn_regular=notosansmono)

icon_map = {'donate': u'\uf4cb',  # square-inc-cash
            'menu': u'\uf35c',  # menu
            'sets': u'\uf5da',  # book-open-page-variant
            'present': u'\uf429',  # presentation-play
            'songs': u'\uf219',  # file-document
            'scripture': u'\uf0a2',  # bible
            'settings': u'\uf493',  # settings
            'search': u'\uf349',  # magnify
            'edit': u'\uf3eb',  # pencil
            'save': u'\uf193',  # content-save
            'chordoff': u'\uf38a',  # music-note-off
            'delete': u'\uf1c0',  # delete
            'cancel': u'\uf159',  # close-circle
            'ok': u'\f134',  # checkbox-marked-circle-outline
            'new': u'\uf415',  # plus
            'listadd': u'\uf412',  # playlist-plus
            'listremove': u'\uf413',  # playlist-remove
            'sort': u'\uf4ba',  # sort
            'copy': u'\uf18f',  # content-copy
            'saveas': u'\uf065',  # at
            'language': u'\uf4bb',  # alphabetical
            'showset': u'\uf276',  # format-indent-increase
            'listmoveup': u'\uf05e',  # arrow-up-bold
            'listmovedown': u'\uf046',  # arrow-down-bold
            'bibleversion': u'\uf4e5',  # sword
            'plus': u'\uf419',  # plus-circle-outline
            'transpose': u'\uf387',  # music-note
            'expand': u'\uf140',  # chevron-down
            'collapse': u'\uf143',  # chevron-up
            'reorder': u'\uf687',  # reorder-horizontal
            '0': u'\uf3a1',  # numeric-0-box
            '1': u'\uf3a4',  # numeric-1-box
            '2': u'\uf3a7',  # numeric-2-box
            '3': u'\uf3aa',  # numeric-3-box
            '4': u'\uf3ad',  # numeric-4-box
            '5': u'\uf3b0',  # numeric-5-box
            '6': u'\uf3b3',  # numeric-6-box
            '7': u'\uf3b6',  # numeric-7-box
            '8': u'\uf3b9',  # numeric-8-box
            '9': u'\uf3bc',  # numeric-9-box
            '9+': u'\uf3bf',  # numeric-9-plus-box
            }

def iconfont(name, size=None):
    icon = icon_map[name]
    if size:
        try:
            float(str(size))
            size = str(int(size))
        except ValueError:
            pass
        return (u'[font=IconFonts][size='
                + size + u']' + icon
                + u'[/size][/font]')
    else:
        return (u'[font=IconFonts]'
                + icon
                + u'[/font]')
