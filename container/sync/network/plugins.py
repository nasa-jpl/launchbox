from manage.network import LBNetwork
from manage.util import LBPath
from models.plugins import LBPlugins


class LBNetworkPlugins:
    @staticmethod
    def create():
        # Get plugins
        if plugins := LBPlugins.list():
            # Plugins server block
            server = LBNetwork.nginx.server()
            server.description = "[Launchbox]: Plugins"
            server.add_hostname("localhost")
            server.listen(8004)
            for plugin in plugins:
                plugin_id = plugin["plugin_id"]
                # Create plugin uWSGI vassal
                vassal = f"plugin_{plugin_id}"
                LBNetwork.uwsgi.vassals.create(
                    vassal,
                    chdir=LBPath.plugins(plugin_id),
                    venv="venv",
                    plugin="python3",
                    module="run:plugin",
                )
                # Create plugin Nginx route
                server.loc_uwsgi(f"/{plugin_id}/", vassal)
            # Create plugins site file
            LBNetwork.nginx.sites.create("plugins", [server])
            # Reload Nginx
            LBNetwork.nginx.sites.reload()

    @staticmethod
    def notify(kind, data):
        if kind == "remove":
            from sync.deploy.plugins import LBDeployPlugins

            LBNetworkPlugins.reset()
            LBDeployPlugins.pending.cleanup(data["plugin_id"])
        LBNetworkPlugins.update()

    @staticmethod
    def reset():
        LBNetwork.nginx.sites.reset("plugins")
        LBNetwork.uwsgi.vassals.reset_plugins()

    @staticmethod
    def update():
        LBNetworkPlugins.reset()
        LBNetworkPlugins.create()
