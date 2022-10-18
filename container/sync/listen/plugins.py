from manage.notify import LBNotify
from manage.util import LBEvent
from sync.network.plugins import LBNetworkPlugins

# Log
LBEvent.log("sync.listen", "Listening for cluster notifications [channel: plugins]")

# Notify: Plugins
LBNotify.listen("plugins", LBNetworkPlugins.notify)
