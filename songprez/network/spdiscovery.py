#!/usr/bin/env python
from twisted.internet import reactor, task
from twisted.internet.protocol import DatagramProtocol
from time import time
import netifaces as ni
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

def get_my_ips():
    '''
    Gets the IP address of all valid network connections. Returns a list.
    '''
    retval = []
    for i in ni.interfaces():
        ip_addr = ni.ifaddresses(i).get(2, None)
        if ip_addr:
            retval.append(ip_addr[0]['addr'])
    return retval


class SPDiscovery(DatagramProtocol):
    def __init__(self, name='SongPrez Default'):
        self.name = name
        self.ips = []
        self.listener = None
        self.expire = None
        self.targets = []

    def start(self):
        if not self.listener:
            self.listener = reactor.listenMulticast(1044, self, listenMultiple=True)
        else:
            self.listener.startListening()
        if not self.expire:
            self.expire = task.LoopingCall(self._expire_targets)
        self.expire.start(1.0)

    def stop(self):
        if self.transport:  # transport is None when already stopped
            self.expire.stop()
            self.listener.stopListening()

    def startProtocol(self):
        logger.debug(u'SPDiscovery: Starting now')
        self.transport.setTTL(20)
        self.ips = get_my_ips()
        for ip in self.ips:
            self.transport.joinGroup("239.10.4.4", ip)

    def findTargets(self):
        if not self.transport:
            self.start()
        self.ips = get_my_ips()
        for ip in self.ips:
            self.transport.setOutgoingInterface(ip)
            self.transport.write(b'SongPrezSeeking', ('239.10.4.4', 1044))

    def _expire_targets(self):
        for i in self.targets[:]:
            last_seen = time() - i['last_seen']
            if last_seen > 5:  # Hasn't been heard off in 5 seconds
                self.targets.remove(i)

    def datagramReceived(self, datagram, address):
        logger.debug(u'SPDiscovery: Received %s from %s', datagram, address)
        if datagram.startswith('SongPrezTarget'):
            ip = address[0]
            #if ip in self.ips:
                #ip = 'localhost'
            name = datagram.split(':', 1)[1]
            index = next((i for (i, d) in enumerate(self.targets)
                          if d['addr'] == ip), None)
            elem = {'name': name, 'addr': ip, 'last_seen': time()}
            if index is None:
                self.targets.append(elem)
            else:
                self.targets[index] = elem
        elif datagram.startswith('SongPrezSeeking'):
            name = self.name
            retval = b'SongPrezTarget:' + name
            self.transport.write(retval, address)
