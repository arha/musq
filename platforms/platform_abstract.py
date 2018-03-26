__author__ = 'arha'
import logging

class platform_abstract:
    def __init__(self):
        self.name = "abstract"
        logging.debug("Platform init: abstract")

    def setup(self):
        pass

    def signal_exit(self):
        pass