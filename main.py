#!/usr/bin/env python
__version__ = '0.1'
import sys

if __name__ == '__main__':
    if 'desktop' in sys.argv:
        from songprez.desktop.app import SongPrezApp
    else:
        from songprez.phone.app import SongPrezApp
    SongPrezApp().run()
