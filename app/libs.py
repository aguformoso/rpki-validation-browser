from requests import post, get
from rpki_validation_browser.settings import DEBUG
from rpki_validation_browser.utils import config


class HttpClient:
    pass

class MattermostClient(HttpClient):

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


class HeClient:
    # "https://bgp.he.net/AS3333"
    pass


class RipestatClient(HttpClient):

    def fetch_info(self, resource=None):

        if resource is None:
            return None

        return get("https://stat.ripe.net/data/as-overview/data.json?resource={resource}".format(
            resource=resource
        )).json()
