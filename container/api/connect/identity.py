import bottle

from api.connect.util import req_auth
from models.plugins import LBPlugins


@req_auth
def index(**kwargs):
    """Respond to calling /<site_id>/<deploy_id>/identity

    Returns a list of configured identity provider plugins.
    """
    return {"providers": LBPlugins.of_type("identity")}


@req_auth
def plugin(plugin_id, **kwargs):
    """Respond to calling /<site_id>/<deploy_id>/identity/<plugin_id>

    Returns info about the specified plugin, or false if that plugin doesn't exist.
    """
    if LBPlugins.exists(plugin_id):
        return {"provider": LBPlugins.get(plugin_id)}
    else:
        bottle.response.status = 501
        return {"provider": False}


@req_auth
def group(plugin_id, group_id, **kwargs):
    """Respond to calling /<site_id>/<deploy_id>/identity/<plugin_id>/group/<group_id>

    Returns user data from specified plugin if group_id has an exact match.
    """
    return {"group": LBPlugins.identity.get_group(plugin_id, group_id) or False}


@req_auth
def search(plugin_id, user_id, **kwargs):
    """Respond to calling /<site_id>/<deploy_id>/identity/<plugin_id>/search/<user_id>

    Returns user data from specified plugin if user_id has a close match..
    """
    return {"user": LBPlugins.identity.search_user(plugin_id, user_id) or False}


@req_auth
def user(plugin_id, user_id, **kwargs):
    """Respond to calling /<site_id>/<deploy_id>/identity/<plugin_id>/user/<user_id>

    Returns user data from specified plugin if user_id has an exact match.
    """
    return {"user": LBPlugins.identity.get_user(plugin_id, user_id) or False}


@req_auth
def user_groups(plugin_id, user_id, **kwargs):
    """Respond to calling /<site_id>/<deploy_id>/identity/<plugin_id>/user/<user_id>/groups

    Returns list of user's groups from specified plugin if user_id has an exact match.
    """
    return {"user": LBPlugins.identity.user_groups(plugin_id, user_id) or False}
