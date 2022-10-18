from manage.network import LBNetwork
from manage.util import LBDir, LBEvent, LBPath
from sync.network.manage import LBNetworkManage
from sync.network.plugins import LBNetworkPlugins

# Networking: Reset
LBNetwork.nginx.certs.reset_all()
LBNetwork.nginx.sites.reset_all()
LBNetwork.uwsgi.vassals.reset_all()

# Log
LBEvent.complete("sync.reset", "Reset network configuration")

# Networking: Management
LBNetworkManage.create()

# Networking: Plugins
LBNetworkPlugins.update()

# Log
LBEvent.complete("sync.run", "Created management network config")

# Sites: Reset
for path in LBPath.list(LBPath.sites("*")):
    LBDir.remove(LBPath.parent(path), LBPath.basename(path))

# Log
LBEvent.complete("sync.reset", "Reset all sites")
