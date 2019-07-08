import os
from logging import info, error
import yaml

CFG_FILE = os.path.dirname(os.path.realpath(__file__)) + '/ripe.yaml'


class Config:

    def __init__(self):
        self.database = {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': '',
            'USER': '',
            'PASSWORD': '',
            'HOST': '',
            'PORT': ''
        }
        self.memcached = ''
        self.server_id = ''
        self.mattermost_token = ''

        self.load_config_file()

    def load_config_file(self):
        """Load global configuration from /etc"""

        if not os.path.exists(CFG_FILE):
            return

        self.raw = yaml.safe_load(open(CFG_FILE, "r"))

        if not isinstance(self.raw, dict):
            error("%s is not a map - ignoring" % CFG_FILE)
            return

        for k, v in self.raw.items():
            if not hasattr(self, k):
                error("unknown configuration key: %s (%s)", k, CFG_FILE)
            if v == "None":
                v = None
            self.__setattr__(k, v)

        info("config: %s [pid %i]", self.raw, os.getpid())


config = Config()
