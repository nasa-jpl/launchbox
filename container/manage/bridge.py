import requests

from .util import LBURL, LBEvent


class LBBridge:
    # Bridge from Launchbox -> Service (optional)
    hostname = "localhost"
    port = 8301
    url = f"http://{hostname}:{port}"

    @staticmethod
    def endpoint(alias, path):
        url = f"{LBBridge.url}/site/{alias}/bridge"
        return LBURL.join(url, path)

    @staticmethod
    def get(alias, path, params={}):
        url = LBBridge.endpoint(alias, path)
        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                return response.json()
        except Exception as error:
            LBEvent.error("LBBridge.get", error)
        return False

    @staticmethod
    def post(alias, path, json={}):
        url = LBBridge.endpoint(alias, path)
        try:
            response = requests.post(url, json=json)
            if response.status_code == 200:
                return response.json()
        except Exception as error:
            LBEvent.error("LBBridge.post", error)
        return False

    class users:
        def create(alias, username):
            return LBBridge.post(alias, "/users/create/", {"username": username})

        def read(alias):
            return LBBridge.get(alias, "/users/")

        def update(alias, users):
            return LBBridge.post(alias, "/users/update/", {"users": users})

        def delete(alias, username):
            return LBBridge.post(alias, "/users/delete/", {"username": username})
