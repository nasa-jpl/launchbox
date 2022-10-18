from api.connect import LBConnect
from manage.network import LBNetwork
from manage.util import LBDNS, LBEnv, LBPath


class LBNetworkManage:
    @staticmethod
    def create():
        # Create server blocks
        base = LBNetworkManage.base()
        connect = LBNetworkManage.connect()

        # Create management site file
        LBNetwork.nginx.sites.create("management", [base, connect])

        # Reload Nginx
        LBNetwork.nginx.sites.reload()

    @staticmethod
    def base():
        # Base management server block
        server = LBNetwork.nginx.server()
        server.description = "[Launchbox]: Management"
        server.add_hostname(LBDNS.root())
        server.listen(8080, proxy=LBEnv.aws(), default=True)

        # Create base uWSGI vassal
        LBNetwork.uwsgi.vassals.create("api", chdir=LBPath.app(), plugin="python3", module="api.management:app")

        # Add base management routes
        server.include_routes("manage")

        # Result
        return server

    @staticmethod
    def connect():
        # Connect management server block
        server = LBNetwork.nginx.server()
        server.description = "[Connect]: Internal API from Services -> Launchbox"
        server.add_hostname(LBConnect.hostname)
        server.listen(LBConnect.port)

        # Create connect uWSGI vassal
        LBNetwork.uwsgi.vassals.create("connect", chdir=LBPath.app(), plugin="python3", module="api.connect.app:app")
        # Add connect server route
        server.loc_uwsgi("/", "connect", rewrite=True)

        # Result
        return server
