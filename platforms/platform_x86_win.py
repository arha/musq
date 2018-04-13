__author__ = 'arha'
from platforms import platform_abstract
import logging

class platform_x86_win(platform_abstract.platform_abstract):
    def __init__(self):
        super(  platform_x86_win, self).__init__()
        self.name = "x86_win"
        logging.debug("Platform init: x86_win")

    def setup(self):
        super(  platform_x86_win, self).setup()

    def signal_exit(self):
        super(  platform_x86_win, self).setup()

    def get_all_ips(self):
        return None

    def generate_musq_id(self):
        return "W_86"

    def get_env_data(self):
        result = super(  platform_x86_win, self).get_env_data()
        result.update({"platform": "windows"})
        return result
