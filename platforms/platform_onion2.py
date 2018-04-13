__author__ = 'arha'
from platforms import platform_abstract, platform_linux
import logging
import socket, fcntl, struct    # needed to get the IPs of this device
import sys, hashlib
from enum import Enum

class platform_onion2(platform_linux.platform_linux):
    def __init__(self):
        super(  platform_onion2, self).__init__()
        self.name = "omega_onion2"
        logging.debug("Platform init: omega onion2.")

    def setup(self):
        super(  platform_onion2, self).setup()

    def signal_exit(self):
        super(  platform_onion2, self).setup()

    def get_env_data(self):
        result = super(  platform_onion2, self).get_env_data()
        result.update({"platform": "omega onion2"})
        return result
