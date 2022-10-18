import requests

from models.sites import LBSites

from .util import LBEvent


class LBMgmtBridge:
    # Bridge for sites to access data from Launchbox itself
    hostname = "localhost"
    port = 1038
    url = f"http://{hostname}:{port}"

    @staticmethod
    def endpoint(site_id, path=None):
        key = LBSites.get(site_id)["api_key"]
        # key = "temp"
        url = f"{LBMgmtBridge.url}/{key}"
        if path:
            return f"{url}{path}"
        return url
