from api.connect.util import req_auth
from models.deploys import LBDeploys


@req_auth
def index(site_id, deploy_id, **kwargs):
    """Respond to calling /<site_id>/<deploy_id>/resources"""
    return LBDeploys.site.resources(site_id, deploy_id)


@req_auth
def by_name(site_id, deploy_id, resource_name, **kwargs):
    """Respond to calling /<site_id>/<deploy_id>/resources/<resource_name>"""
    return index(site_id=site_id, deploy_id=deploy_id, **kwargs)[resource_name]
