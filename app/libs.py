from requests import post
from rpki_validation_browser.settings import DEBUG
from rpki_validation_browser.utils import config


class MattermostClient():

    def __init__(self):
        super(MattermostClient, self).__init__()

        if DEBUG:
            self.send_msg = self.print
        else:
            self.send_msg = self.post

    def print(self, msg=""):
        return print(msg)

    def post(self, msg=""):
        post(
            "https://mattermost.ripe.net/hooks/{token}".format(token=config.mattermost_token),
            headers={
              'Content-Type': 'application/json'
            },
            json={
                "text": msg
            }
        )
