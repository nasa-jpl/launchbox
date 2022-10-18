from manage.util import LBEvent
from sync.deploy.plugins import LBDeployPlugins
from sync.deploy.services import LBDeployServices
from sync.deploy.sites import LBDeploySites
from sync.util import LBEC

# Deployments: eventual consistency
steps = [
    LBDeployServices.complete.check,
    LBDeploySites.complete.check,
    LBDeployServices.pending.check,
    LBDeploySites.pending.check,
    LBDeployPlugins.pending.check,
]

LBEvent.log("sync.run", "Starting eventual consistency loop...")
LBEC.loop(steps)
