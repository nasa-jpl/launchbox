import bottle

from models.deploys import LBDeploys
from models.sites import LBSites


def req_auth(func):
    """Decorator for validating an API key in a route and passing the relevant site.

    If they key matches the api_key field for a site in the database,
    pass the corresponding site object to the decorated function as a keyword argument.
    If it doesn't match, return a 401 Unauthorized response.
    """

    def _req_auth(*args, **kwargs):
        if site := LBSites.get(kwargs["site_id"]):
            if deployment := LBDeploys.service.get(kwargs["deploy_id"]):
                kwargs["site"] = site
                kwargs["deployment"] = deployment
                return func(*args, **kwargs)
        bottle.response.status = 401
        return {"error": "auth"}

    return _req_auth
