#!/usr/bin/env python
__version__ = '0.1'
import sys
# Workaround so logging module calls go to the Kivy log
from kivy.logger import Logger
import logging
logging.Logger.manager.root = Logger
from kivy.support import install_twisted_reactor
install_twisted_reactor()

from twisted.internet import reactor
if sys.platform == 'linux2':
    from twisted.cred import portal, checkers
    from twisted.conch import manhole, manhole_ssh
    from twisted.conch.ssh import keys

    def getManholeFactory(namespace, **passwords):
        realm = manhole_ssh.TerminalRealm()
        def getManhole(_):
            return manhole.ColoredManhole(namespace)
        realm.chainedProtocolFactory.protocolFactory = getManhole
        p = portal.Portal(realm)
        p.registerChecker(
            checkers.InMemoryUsernamePasswordDatabaseDontUse(**passwords))
        f = manhole_ssh.ConchFactory(p)
        return f
publicKey = 'ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAGEArzJx8OYOnJmzf4tfBEvLi8DVPrJ3\
/c9k2I/Az64fxjHf9imyRJbixtQhlH9lfNjUIx+4LmrJH5QNRsFporcHDKOTwTTYLh5KmRpslkYHR\
ivcJSkbh/C+BR3utDS555mV'
privateKey = """-----BEGIN RSA PRIVATE KEY-----
MIIByAIBAAJhAK8ycfDmDpyZs3+LXwRLy4vA1T6yd/3PZNiPwM+uH8Yx3/YpskSW
4sbUIZR/ZXzY1CMfuC5qyR+UDUbBaaK3Bwyjk8E02C4eSpkabJZGB0Yr3CUpG4fw
vgUd7rQ0ueeZlQIBIwJgbh+1VZfr7WftK5lu7MHtqE1S1vPWZQYE3+VUn8yJADyb
Z4fsZaCrzW9lkIqXkE3GIY+ojdhZhkO1gbG0118sIgphwSWKRxK0mvh6ERxKqIt1
xJEJO74EykXZV4oNJ8sjAjEA3J9r2ZghVhGN6V8DnQrTk24Td0E8hU8AcP0FVP+8
PQm/g/aXf2QQkQT+omdHVEJrAjEAy0pL0EBH6EVS98evDCBtQw22OZT52qXlAwZ2
gyTriKFVoqjeEjt3SZKKqXHSApP/AjBLpF99zcJJZRq2abgYlf9lv1chkrWqDHUu
DZttmYJeEfiFBBavVYIF1dOlZT0G8jMCMBc7sOSZodFnAiryP+Qg9otSBjJ3bQML
pSTqy7c3a2AScC/YyOwkDaICHnnD3XyjMwIxALRzl0tQEKMXs6hH8ToUdlLROCrP
EhQ0wahUTCk1gKA4uPD6TMTChavbh4K63OvbKg==
-----END RSA PRIVATE KEY-----"""

if __name__ == '__main__':
    if 'desktop' in sys.argv:
        from songprez.desktop.app import SongPrezApp
    else:
        from songprez.phone.app import SongPrezApp
    app = SongPrezApp()
    #def interact():
        #import IPython
        #IPython.embed()
    #from twisted.internet import reactor
    #reactor.callInThread(interact)
    if sys.platform == 'linux2':
        f = getManholeFactory(globals(), admin='kivy')
        f.publicKeys[b'ssh-rsa'] = keys.Key.fromString(data=publicKey)
        f.privateKeys[b'ssh-rsa'] = keys.Key.fromString(data=privateKey)
        reactor.listenTCP(2222, f)
    app.run()
