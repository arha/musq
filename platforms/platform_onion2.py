__author__ = 'arha'
from platforms import platform_abstract, platform_x86_linux
import logging
import socket, fcntl, struct    # needed to get the IPs of this device
import sys, hashlib
from enum import Enum

class platform_onion2(platform_x86_linux.platform_x86_linux):
    def __init__(self):
        super(  platform_onion2, self).__init__()
        self.name = "omega_onion2"
        logging.debug("Platform init: omega onion2.")

    def setup(self):
        super(  platform_onion2, self).setup()

    def signal_exit(self):
        super(  platform_onion2, self).setup()
