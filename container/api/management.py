import json

import bottle

from manage.util import LBDNS, LBEnv
from models.deploys import LBDeploys
from models.plugins import LBPlugins
from models.services import LBServices
from models.sites import LBSites
from models.stats import LBStats
from models.users import LBUsers

# Application
app = bottle.Bottle()
version = 0.9

# Debugging
bottle.debug(LBEnv.local())


# Authentication
def req_auth(func):
    def _req_auth(*args, **kwargs):
        if LBUsers.current():
            return func(*args, **kwargs)
        else:
            bottle.response.status = 401
            return {"error": "auth"}

    return _req_auth


# Index
@app.get("/")
def index():
    return {
        "api": "lb",
        "dns": LBDNS.entrypoint(),
        "env": LBEnv.type(),
        "root": LBDNS.root(),
        "version": version,
    }


# [Auth]: Login
@app.post("/auth/login")
def auth_login():
    required = [
        "user_id",
        "password",
    ]
    args = {}
    for name in required:
        if value := bottle.request.params.get(name):
            args[name] = value
        else:
            return {"error", f"invalid parameters, missing: {name}"}
    if result := LBUsers.login(**args):
        return bottle.redirect("/")
    else:
        return bottle.redirect(f"/#auth?error={result.kind}")


# [Auth]: Login
@app.get("/auth/logout")
def auth_logout():
    LBUsers.logout()
    bottle.redirect("/")


# [Auth]: Register
@app.post("/auth/register")
def auth_register():
    required = [
        "user_id",
        "password",
    ]
    args = {}
    for name in required:
        if value := bottle.request.params.get(name):
            args[name] = value
        else:
            return {"error", f"invalid parameters, missing: {name}"}
    if result := LBUsers.create(**args):
        bottle.redirect("/")
    else:
        bottle.redirect(f"/#register?error={result.kind}")


# [Auth]: State
@app.get("/auth/state")
def auth_state():
    if user_id := LBUsers.current():
        return {"user": LBUsers.get(user_id)}
    else:
        return {"user": False}


# [Plugins]: List plugins
@app.get("/plugins")
@req_auth
def plugins():
    results = LBPlugins.list()
    return {"plugins": results}


# [Plugins]: Add plugin
@app.post("/plugins/add")
@req_auth
def add_plugin():
    params = json.loads(bottle.request.body.read())
    if params.get("repo_url"):
        result = LBPlugins.add(
            params.get("repo_url"),
            params.get("provider_id"),
            params.get("branch") if params.get("branch") else None,
        )
        return {"success": result}
    return {"error", "invalid parameters, missing: repo_url"}


# [Plugins]: Get plugin
@app.get("/plugins/<plugin_id>")
@req_auth
def get_plugin(plugin_id):
    result = LBPlugins.get(plugin_id)
    return {"plugin": result}


# [Plugins]: List plugins type
@app.get("/plugins/type")
@req_auth
def plugins_type():
    results = LBPlugins.of_type()
    return {"plugins": results}


# [Plugins]: Remove plugin
@app.post("/plugins/<plugin_id>/remove")
@req_auth
def remove_plugin(plugin_id):
    result = LBPlugins.remove(plugin_id)
    return {"success": result}


# [Plugins]: Update plugin
@app.post("/plugins/<plugin_id>/update")
@req_auth
def update_plugin(plugin_id):
    result = LBPlugins.update(plugin_id)
    return {"success": result}


# [Deploys]: List
@app.get("/deploys")
@req_auth
def list_deploys():
    results = LBDeploys.list()
    return {"deploys": results}


# [Deploys]: Get deploy
@app.get("/deploys/<deploy_id>")
@req_auth
def get_deploy(deploy_id):
    result = LBDeploys.get(deploy_id)
    return {"deploy": result}


# [Services]: List services
@app.get("/services")
@req_auth
def services():
    results = LBServices.list()
    return {"services": results}


# [Services]: Get service
@app.get("/services/<service_id>")
@req_auth
def get_service(service_id):
    result = LBServices.get(service_id)
    return {"service": result}


# [Services]: Add service
@app.post("/services/<service_id>/add")
@req_auth
def add_service(service_id):
    params = json.loads(bottle.request.body.read())
    required = [
        "provider_id",
        "name",
        "repo_url",
        "branch",
        "env_name",
    ]
    args = {}
    for name in required:
        if value := params.get(name):
            args[name] = value
        else:
            return {"error", f"invalid parameters, missing: {name}"}
    result = LBServices.add(service_id, **args)
    return {"success": result}


# [Services]: Deploy service
@app.post("/services/<service_id>/deploy/<commit_sha>")
@req_auth
def deploy_service(service_id, commit_sha):
    result = LBServices.deploy(service_id, commit_sha)
    return {"success": result}


# [Sites]: List sites
@app.get("/sites")
@req_auth
def sites():
    results = LBSites.list()
    return {"sites": results}


# [Sites]: Get site
@app.get("/sites/<site_id>")
@req_auth
def get_site(site_id):
    result = LBSites.get(site_id)
    return {"site": result}


# [Sites]: Add site
@app.post("/sites/<site_id>/add")
@req_auth
def add_site(site_id):
    params = json.loads(bottle.request.body.read())
    if service_id := params.get("service_id"):
        result = LBSites.add(site_id, service_id)
        return {"success": result}
    else:
        return {"error": "invalid parameters"}


# [Sites]: Remove site
@app.post("/sites/<site_id>/remove")
@req_auth
def remove_site(site_id):
    result = LBSites.remove(site_id)
    return {"success": result}


# [Sites]: Update site
@app.post("/sites/<site_id>/update")
@req_auth
def update_site(site_id):
    params = json.loads(bottle.request.body.read())
    if attr := params.get("attr"):
        value = params.get("value", "")
        result = LBSites.update(site_id, attr, value)
        return {"success": result}
    else:
        return {"error": "invalid parameters"}


# [Sites]: List hostnames for site
@app.get("/sites/<site_id>/hostnames")
@req_auth
def list_hostnames(site_id):
    results = LBSites.hostnames.list(site_id)
    return {"hostnames": results}


# [Sites]: Add hostname to site
@app.post("/sites/<site_id>/hostnames/add")
@req_auth
def add_hostname(site_id):
    params = json.loads(bottle.request.body.read())
    if hostname := params.get("hostname"):
        result = LBSites.hostnames.add(site_id, hostname)
        return {"success": result}
    else:
        return {"error": "invalid parameters"}


# [Sites]: Make hostname primary for site
@app.post("/sites/<site_id>/hostnames/primary")
@req_auth
def primary_hostname(site_id):
    params = json.loads(bottle.request.body.read())
    if hostname := params.get("hostname"):
        result = LBSites.hostnames.make_primary(site_id, hostname)
        return {"success": result}
    else:
        return {"error": "invalid parameters"}


# [Sites]: Remove hostname from site
@app.post("/sites/<site_id>/hostnames/remove")
@req_auth
def remove_hostname(site_id):
    params = json.loads(bottle.request.body.read())
    if hostname := params.get("hostname"):
        result = LBSites.hostnames.remove(site_id, hostname)
        return {"success": result}
    else:
        return {"error": "invalid parameters"}


# [Sites]: Add note to site
@app.post("/sites/<site_id>/notes/add")
@req_auth
def add_note(site_id):
    params = json.loads(bottle.request.body.read())
    if text := params.get("text"):
        result = LBSites.notes.add(site_id, text)
        return {"success": result}
    else:
        return {"error": "invalid parameters"}


# [Sites]: List users for site
@app.get("/sites/<site_id>/users")
@req_auth
def list_users(site_id):
    users = LBSites.users.list(site_id)
    return {"users": users}


# [Sites]: Add user to site
@app.post("/sites/<site_id>/users/add")
@req_auth
def add_user(site_id):
    params = json.loads(bottle.request.body.read())
    if username := params.get("username"):
        result = LBSites.users.add(site_id, username)
        return {"results": result}
    else:
        return {"error": "invalid parameters"}


# [Sites]: Import users from LDAP
@app.post("/sites/<site_id>/users/import/ldap")
@req_auth
def import_ldap_users(site_id):
    params = json.loads(bottle.request.body.read())
    if group_name := params.get("group_name"):
        permissions = params.get("permissions", [])
        result = LBSites.users.import_ldap(site_id, group_name, permissions)
        return {"results": result}
    else:
        return {"error": "invalid parameters"}


# [Sites]: Remove user from site
@app.post("/sites/<site_id>/users/remove")
@req_auth
def remove_user(site_id):
    params = json.loads(bottle.request.body.read())
    if username := params.get("username"):
        result = LBSites.users.remove(site_id, username)
        return {"results": result}
    else:
        return {"error": "invalid parameters"}


# [Sites]: Update users for site
@app.post("/sites/<site_id>/users/update")
@req_auth
def update_user(site_id):
    params = json.loads(bottle.request.body.read())
    if delta := params.get("delta"):
        result = LBSites.users.update(site_id, delta)
        return {"results": result}
    else:
        return {"error": "invalid parameters"}


# [Stats]: Latest stats
@app.get("/stats/latest")
@req_auth
def latest_stats():
    results = LBStats.latest()
    return {"latest": results}


# [Stats]: Timeline
@app.get("/stats/timeline")
@req_auth
def timeline_stats():
    results = LBStats.timeline()
    return {"timeline": results}


if __name__ == "__main__":
    # Run webserver
    bottle.run(
        app=app,
        host="0.0.0.0",
        port=8001,
    )
