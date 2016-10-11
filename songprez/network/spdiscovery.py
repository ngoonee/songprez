#!/usr/bin/env python
from twisted.internet import reactor
from twisted.internet.protocol import DatagramProtocol
import socket
import logging
logger = logging.getLogger(__name__)

def get_my_ip():
    '''
    Gets the IP address on the internet-connected network interface. Prevents
    use of the loopback interface (which won't receive anything from wlan).
    '''
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('8.8.8.8', 0))
    s.setblocking(False)
    ip = s.getsockname()[0]
    logger.debug(u'SPDiscovery: IP is %s', ip)
    return ip


class SPDiscovery(DatagramProtocol):
    def __init__(self, name='SongPrez Default'):
        self.name = name
        reactor.listenMulticast(1044, self, listenMultiple=True)

    def startProtocol(self):
        logger.debug(u'SPDiscovery: Starting now')
        my_ip = get_my_ip()
        self.transport.setTTL(20)
        self.transport.joinGroup("239.10.4.4", my_ip)
        self.targets = []

    def findTargets(self):
        self.targets = []
        self.transport.write(b'SongPrezSeeking', ('239.10.4.4', 1044))

    def datagramReceived(self, datagram, address):
        logger.debug(u'SPDiscovery: Received %s from %s', datagram, address)
        if datagram.startswith('SongPrezTarget'):
            name = datagram.split(':', 1)[1]
            self.targets.append({'name': name, 'addr': address[0]})
        elif datagram.startswith('SongPrezSeeking'):
            name = self.name
            retval = b'SongPrezTarget:' + name
            self.transport.write(retval, address)
