#!/usr/bin/env python
import logging, threading, time, sys
import serial

from .exceptions import TimeoutException
from .packetizer import LaxCRLFPacketizer

logging.basicConfig(level=logging.DEBUG)

""" this is a serial class inspired by Francois' Aucamp version
    https://github.com/faucamp/python-gsmmodem/blob/master/gsmmodem/serial_comms.py
    disabling a lot of the request/response features, but including a pluggable packetizing scheme
    this can allow you to encapsulate serial data in packets/frames, which can be as simple as an \r\n
    or use something like SLIP, KISS, COBS, c-style escaping, escaping to ascii HEX, etc
"""

class Serialbox:
    log = logging.getLogger('arha.serialbox.Serialbox')
    timeout = 2
    packetizer = None

    def __init__(self, port, baudrate=115200, packetReceivedCallbackFunc=None, fatalErrorCallbackFunc=None, packetizer=LaxCRLFPacketizer,  *args, **kwargs):
        self.alive = False
        self.port = port
        self.baudrate = baudrate
        self.packetizer = packetizer()
        self._responseEvent = None # threading.Event()
        # Reentrant lock for managing concurrent write access to the underlying serial port
        self._txLock = threading.RLock()
        self.packetReceivedCallback = packetReceivedCallbackFunc or self._dummyCallback
        self.fatalErrorCallback = fatalErrorCallbackFunc or self._dummyCallback
        self.packetizer.packetAssembledCallback = self._packetAssembledCallback
        self._response = None

    def connect(self):
        """ Open port, fork the blocking read thread """                
        self.serial = serial.Serial(port=self.port, baudrate=self.baudrate, timeout=self.timeout)
        self.alive = True 
        self.rxThread = threading.Thread(target=self._readLoop)
        self.rxThread.daemon = True
        self.rxThread.start()

    def close(self):
        """ Stops the read thread, waits for it to exit cleanly, then closes the underlying serial port """        
        self.alive = False
        self.rxThread.join()
        self.serial.close()

    def _dummyCallback(self, *args, **kwargs):
        """ does nothing """
    
    def _packetAssembledCallback(self, data):
        self._response = data
        #print("Packetizer received data: %s" % data)
        if self._responseEvent:
            self._responseEvent.set()
        self.packetReceivedCallback(data)
        
    def _readLoop(self):
        """ Read thread main loop """
        try:
            while self.alive:
                data = self.serial.read(1)
                if data != b'':
                    self.packetizer.feed(data)
        except serial.SerialException as e:
            self.alive = False
            try:
                self.serial.close()
            except Exception: #pragma: no cover
                pass
            # Notify the fatal error handler
            self.fatalErrorCallback(e)
        
    def write(self, data, waitForResponse=False, timeout=2):
        """ write data (optionally return a response and a timeout exception) """
        self.waitingForResponse = False
        if (not isinstance(data, (bytes, bytearray))):
            data = data.encode("UTF-8")
            self.waitingForResponse = waitForResponse

        with self._txLock:
            if self.waitingForResponse:
                self._response = b''
                self._responseEvent = threading.Event()                
                self.serial.write(data)
                if self._responseEvent.wait(timeout):
                    # thread Event was set from somewhere else (the packetizer), return the result
                    self._responseEvent = None
                    return self._response
                else:
                    # Response timed out
                    logging.debug("Error waiting for response for command [%s]" % data)
                    self._responseEvent = None
                    self._expectResponseTermSeq = False
                    print("Response: %s" % self._response)
                    if len(self._response) > 0:
                        # Add the partial response to the timeout exception
                        raise TimeoutException(self._response)
                    else:
                        raise TimeoutException()
            else:
                # just write it, without waiting for a response
                self.serial.write(data)