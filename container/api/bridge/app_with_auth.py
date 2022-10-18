import bottle

from api.bridge import auth, identity, resources
from api.bridge.util import req_auth
from manage.util import LBEnv, LBEnvdir, LBPath

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
        "api": "lb_management_bridge",
        "version": version,
    }

@req_auth
def site_index(**kwargs):
    """Respond to calling /<api_key>"""
    site = kwargs["site"]
    site_id = site["site_id"]
    return {
        "api": "lb_management_bridge",
        "version": version,
        "service": site['service_id'],
        "site": site_id,
        "env": LBEnvdir.read(LBPath.sites(site_id)),
    }


# URL routes
app.route("/", "GET", index)
app.route("/<api_key>", "GET", site_index)

app.route("/<api_key>/auth", "GET", auth.index)
app.route("/<api_key>/auth/login", "GET", auth.login)
app.route("/<api_key>/auth/verify", "POST", auth.verify)

app.route("/<api_key>/identity", "GET", identity.index)
# Should requests to /<api_key>/identity/user get a response? If so, what?
app.route("/<api_key>/identity/user/<username>", "GET", identity.user)

app.route("/<api_key>/resources", "GET", resources.index)
app.route("/<api_key>/resources/<resource_name>", "GET", resources.by_name)


if __name__ == "__main__":
    # Run webserver
    bottle.run(
        app=app,
        host="0.0.0.0",
        port=8001,
    )
