import bottle

from api.connect import identity, resources
from api.connect.util import req_auth
from manage.util import LBEnv

# Application
app = bottle.Bottle()
version = 0.1

# Debugging
bottle.debug(LBEnv.local())


# Core response functions
# Other response functions are located in the rest of the files in this folder.
def index():
    """Respond to calling /"""
    return {
        "api": "connect",
        "version": version,
    }


@req_auth
def site_index(site_id, deploy_id, **kwargs):
    """Respond to calling /<site_id>/<deploy_id>"""
    return {
        "api": "connect",
        "version": version,
        "service": kwargs["site"]["service_id"],
        "site": site_id,
    }


# URL routes
app.route("/", "GET", index)
app.route("/<site_id>/<deploy_id>", "GET", site_index)

app.route("/<site_id>/<deploy_id>/identity", "GET", identity.index)
app.route("/<site_id>/<deploy_id>/identity/<plugin_id>", "GET", identity.plugin)
app.route("/<site_id>/<deploy_id>/identity/<plugin_id>/group/<group_id>", "GET", identity.group)
app.route("/<site_id>/<deploy_id>/identity/<plugin_id>/search/<user_id>", "GET", identity.search)
app.route("/<site_id>/<deploy_id>/identity/<plugin_id>/user/<user_id>", "GET", identity.user)
app.route("/<site_id>/<deploy_id>/identity/<plugin_id>/user/<user_id>/groups", "GET", identity.user_groups)

app.route("/<site_id>/<deploy_id>/resources", "GET", resources.index)
app.route("/<site_id>/<deploy_id>/resources/<resource_name>", "GET", resources.by_name)


if __name__ == "__main__":
    # Run webserver
    bottle.run(
        app=app,
        host="0.0.0.0",
        port=8002,
    )
