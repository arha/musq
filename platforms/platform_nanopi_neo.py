__author__ = 'arha'
from platforms import platform_abstract, platform_linux
import logging
import socket, fcntl, struct    # needed to get the IPs of this device
import sys, hashlib
from enum import Enum

class nanopi_neo_board(Enum):
    UNKNOWN = 0

class platform_nanopi_neo(platform_linux.platform_linux):
    def __init__(self):
        super(  platform_nanopi_neo, self).__init__()
        self.name = "nanopi_neo"
        logging.debug("Platform init: rpi")

    def setup(self):
        super(  platform_nanopi_neo, self).setup()
        self.platform_detect_extended()

    def signal_exit(self):
        super(  platform_nanopi_neo, self).setup()

    def get_env_data(self):
        result = super(  platform_nanopi_neo, self).get_env_data()
        result.update({"platform": "nanopi neo"})
        return result

    def platform_detect_extended(self):
        self.model_string = ""
        self.model = nanopi_neo_board.UNKNOWN
        logging.debug("NanoPi model: %s (%s)" % (self.model, self.model_string))

