from manage.notify import LBNotify
from manage.util import LBEvent
from sync.network.sites import LBNetworkSites

# Log
LBEvent.log("sync.listen", "Listening for cluster notifications [channel: sites]")

# Notify: Sites
LBNotify.listen("sites", LBNetworkSites.notify)
