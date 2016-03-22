#!/usr/bin/env python
__version__ = '0.1'
import sys
# Workaround so logging module calls go to the Kivy log
from kivy.logger import Logger
import logging
logging.Logger.manager.root = Logger

if __name__ == '__main__':
    if 'desktop' in sys.argv:
        from songprez.desktop.app import SongPrezApp
    else:
        from songprez.phone.app import SongPrezApp
    SongPrezApp().run()
