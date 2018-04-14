__author__ = 'arha'
import logging

class platform_abstract:
    musq = None
    def __init__(self):
        self.name = "abstract"
        logging.debug("Platform init: abstract")

    def setup(self):
        pass

    def signal_exit(self):
        self.kill_thread = True

    def get_env_data(self):
        return {"platform": "abstract"}
