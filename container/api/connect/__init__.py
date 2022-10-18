class LBConnect:
    # Bridge for sites to access data from Launchbox itself
    hostname = "localhost"
    port = 1038
    url = f"http://{hostname}:{port}"

    @staticmethod
    def endpoint(site_id, deploy_id):
        return f"{LBConnect.url}/{site_id}/{deploy_id}"
