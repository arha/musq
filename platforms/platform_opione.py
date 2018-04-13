__author__ = 'arha'
from platforms import platform_abstract, platform_linux
import logging
import socket, fcntl, struct    # needed to get the IPs of this device
import sys, hashlib

class platform_opione(platform_linux.platform_linux):
    def __init__(self):
        super(  platform_opione, self).__init__()
        self.name = "opione"
        logging.debug("Platform init: opione")

    def setup(self):
        super(  platform_opione, self).setup()

    def signal_exit(self):
        super(  platform_opione, self).setup()

    def get_env_data(self):
        result = super(  platform_opione, self).get_env_data()
        result.update({"platform": "orange pi one"})
        return result

    def get_all_if_data(self):
        nic = []
        for ix in socket.if_nameindex():
            name = ix[1]
            record = self.get_data_for_if( name )
            if (record != None):
                nic.append( record )

        return (nic)
