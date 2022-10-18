from manage.network import LBNetwork
from manage.util import LBDir, LBEnv, LBPath
from models.deploys import LBDeploys
from models.sites import LBSites
from runtimes import LBRuntime


class LBNetworkSites:
    @staticmethod
    def create(site_id):
        # Get site
        if site := LBSites.get(site_id):
            # Get current site deployment
            if deploy := site.get("deployment"):
                # Params
                deploy_id = deploy["deploy_id"]
                routes = LBDeploys.site.routes(site_id, deploy_id)
                # Paths
                deploy_path = deploy["path"]
                env_path = LBDeploys.site.path(site_id, deploy_id)
                venv_path = LBRuntime.python3.venv(deploy_path)
                # Verify service deployment folder exists
                if not LBDir.exists(deploy_path):
                    return False
                # Verify site deployment folder exists
                if not LBDir.exists(env_path):
                    return False
                # Create site server blocks
                blocks = []
                for hostname in site["hostnames"]:
                    server = LBNetwork.nginx.server()
                    server.description = f"[Site]: {site_id}"
                    server.add_hostname(hostname["name"])
                    server.listen(8080, proxy=LBEnv.aws())
                    for name, route in routes.items():
                        # Params
                        options = route.get("options", {})
                        # Type
                        match route["type"]:
                            case "static":
                                if path := options.get("path"):
                                    path = LBPath.join(deploy_path, path)
                                    server.loc_static(route["route"], path)
                            case "wsgi":
                                if "path" in options and "var" in options:
                                    vassal = f"{site_id}_{name}"
                                    path = options["path"].replace("/", ".")
                                    var = options["var"]
                                    if path.endswith(".py"):
                                        path = path[:-3]
                                    module = f"{path}:{var}"
                                    LBNetwork.uwsgi.vassals.create(
                                        vassal,
                                        chdir=deploy_path,
                                        plugin="python3",
                                        module=module,
                                        envdir=env_path,
                                        venv=venv_path,
                                    )
                                    server.loc_uwsgi(route["route"], vassal)
                    blocks += [server]
                # Create site networking
                if blocks:
                    LBNetwork.nginx.sites.create(site_id, blocks)
                    LBNetwork.nginx.sites.reload()

    @staticmethod
    def notify(kind, data):
        if site_id := data.get("site_id"):
            LBNetworkSites.update(site_id)

    @staticmethod
    def reset(site_id):
        LBNetwork.nginx.sites.reset(site_id)
        LBNetwork.uwsgi.vassals.reset_site(site_id)

    @staticmethod
    def update(site_id):
        LBNetworkSites.reset(site_id)
        LBNetworkSites.create(site_id)
