from requests import post
from rpki_validation_browser.settings import DEBUG


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
            "https://mattermost.ripe.net/hooks/635wqnwnaiy6xqaq4b9frp8awe",
            headers={
              'Content-Type': 'application/json'
            },
            json={
                "text": msg
            }
        )
