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


class DataProtector:

    @staticmethod
    def protect_entich_received(evt):
        """
        :param evt: Enrich received event coming from the client
        :return: Remove traces of IP in enrichedReceived event
        """
        evt['data']['enrichUrl'] = evt['data']['enrichUrl'].split('resource=')[0]

    @staticmethod
    def protect_initialized(evt):
        """
        :param evt: initialized event coming from the client
        :return: Remove URLs containing hashes
        """
        for o in evt['data']['testUrls']:
            hash = o['url'].split('://')[1].split('.')[0]
            o['url'] = o['url'].replace(hash, '')
            del hash  # no trace of hash

    @staticmethod
    def protect_event(evt):
        """
        :param evt: _regular_ event event coming from the client
        :return: Remove hashes from <hash>.url.tld
        """

        hash = evt['data']['testUrl'].split('://')[1].split('.')[0]
        evt['data']['testUrl'] = evt['data']['testUrl'].replace(hash, '')
        del hash  # no trace of hash

    @staticmethod
    def protect_origin(evt):
        evt["data"]["originLocation"] = evt["data"]["originLocation"].split('/')[2]

    @staticmethod
    def wipe_ip(evt):
        """
        :param evt: event holding an IP address in its .data.ip attribute
        :return:
        """

        if "ip" in evt["data"].keys():
            del evt["data"]["ip"]
