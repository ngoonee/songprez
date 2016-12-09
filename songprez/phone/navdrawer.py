# -*- coding: utf-8 -*-
from kivy.lang import Builder
from kivymd.navigationdrawer import NavigationDrawer


Builder.load_string("""
#:import NavigationDrawerIconButton kivymd.navigationdrawer.NavigationDrawerIconButton
<SPNavDrawer>:
    title: "NavigationDrawer"
    NavigationDrawerIconButton:
        icon: 'presentation-play'
        text: "Present"
        on_release: app.base.to_screen('present')
    NavigationDrawerIconButton:
        icon: 'book-open-page-variant'
        text: "Sets"
        on_release: app.base.to_screen('sets')
    NavigationDrawerIconButton:
        icon: 'file-document'
        text: "Songs"
        on_release: app.base.to_screen('songs')
    NavigationDrawerIconButton:
        icon: 'magnify'
        text: "Search"
        on_release: app.base.to_screen('search')
    NavigationDrawerIconButton:
        icon: 'bible'
        text: "Scripture"
        on_release: app.base.to_screen('scripture')
    NavigationDrawerIconButton:
        icon: 'settings'
        text: "Settings"
        on_release: app.base.to_screen('settings')
    NavigationDrawerIconButton:
        icon: 'remote'
        text: "Scan"
        on_release: app.base.to_screen('scan')
""")

class SPNavDrawer(NavigationDrawer):
    pass
