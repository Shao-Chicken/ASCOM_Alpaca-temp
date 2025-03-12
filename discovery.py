# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# discovery.py - Discovery Responder
#
# Part of the MyAlpacaDriver sample device driver
#
# MIT License
# -----------------------------------------------------------------------------
import os
import socket
from threading import Thread
from logging import Logger

logger: Logger = None

class DiscoveryResponder(Thread):
    """
    通过监听 32227 UDP 来响应 "alpacadiscovery1" 消息，返回当前服务所在的 port。
    """

    def __init__(self, ADDR, PORT):
        Thread.__init__(self, name='Discovery')

        self.device_address = (ADDR, 32227)
        self.alpaca_response = "{\"AlpacaPort\": " + str(PORT) + "}"
        self.rsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.rsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        if os.name != 'nt':
            self.rsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        try:
            self.rsock.bind(self.device_address)
        except:
            logger.error('DiscoveryResponder: failed to bind receive socket')
            self.rsock.close()
            self.rsock = 0
            raise

        self.tsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.tsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self.tsock.bind((ADDR, 0))
        except:
            logger.error('DiscoveryResponder: failed to bind send socket')
            self.tsock.close()
            self.tsock = 0
            raise

        self.daemon = True
        self.start()

    def run(self):
        while True:
            data, addr = self.rsock.recvfrom(1024)
            datastr = data.decode('ascii', errors='ignore')
            logger.info(f'Discovery received "{datastr}" from {addr}')
            if 'alpacadiscovery1' in datastr:
                self.tsock.sendto(self.alpaca_response.encode(), addr)
