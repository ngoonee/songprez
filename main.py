#!/usr/bin/env python
__version__ = '0.1'
import sys

if __name__ == '__main__':
    if 'phone' in sys.argv:
        from songprez.phone.app import SongPrezApp
        SongPrezApp().run()
    else:
        from songprez.desktop.app import SongPrezApp
        SongPrezApp().run()
