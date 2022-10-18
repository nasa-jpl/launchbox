from manage.config import LBConfig
from manage.util import LBDB, LBDir, LBEnvdir, LBPath
from models.deploys import LBDeploys
from models.resources import LBResources
from models.sites import LBSites
from runtimes import LBRuntime
from sync.network.sites import LBNetworkSites
from sync.util import LBEC


class LBDeploySites:
    class complete:
        @staticmethod
        def check():
            with LBDB() as db:
                if db.connect(LBDB.core):
                    # Get latest complete site deployments by site_id
                    query = """
                        SELECT DISTINCT ON ("site_id") "site_id", "deploy_id", "status", "created"
                        FROM deploy_sites
                        WHERE "status" = 'complete'
                        ORDER BY "site_id", "created" DESC
                    """
                    results = db.select(query)
                    # Check if query succeeded
                    if results is not False:
                        # Verify each deployment has been handled
                        for deploy_site in results:
                            # Params
                            deploy_id = deploy_site["deploy_id"]
                            site_id = deploy_site["site_id"]
                            # Check if site deployment folder exists
                            if not LBDeploySites.complete.exists(deploy_id, site_id):
                                # Create site deployment folder
                                if LBDeploySites.complete.create(deploy_id, site_id):
                                    # Action
                                    return LBEC.action
                        # No action
                        return LBEC.inaction
            # Connection or query failed
            return LBEC.failure

        @staticmethod
        def create(deploy_id, site_id):
            # Get site
            if site := LBSites.get(site_id):
                service_id = site["service_id"]
                # Params
                env_path = LBDeploys.site.path(site_id, deploy_id)
                service_path = LBDeploys.service.path(service_id, deploy_id)
                site_path = LBPath.sites(site_id)
                # Check service deployment folder exists
                if LBDir.exists(service_path):
                    # Create site folder
                    if not LBDir.exists(site_path):
                        LBDir.create(LBPath.parent(site_path), LBPath.basename(site_path))
                    # Create site deployment envdir
                    env_vars = LBDeploys.site.env(site_id, deploy_id)
                    if LBEnvdir.write(env_path, env_vars):
                        # Create site networking
                        LBNetworkSites.update(site_id)
                        # Result
                        return True

        @staticmethod
        def exists(deploy_id, site_id):
            path = LBDeploys.site.path(site_id, deploy_id)
            return LBDir.exists(path)

    class pending:
        @staticmethod
        def check():
            # Add any missing site deployment rows
            LBDeploySites.pending.add()
            with LBDB() as db:
                if db.connect(LBDB.core, autocommit=False):
                    query = """
                        SELECT "deploy_id", "site_id", "status", "created"
                        FROM deploy_sites
                        WHERE "status" = 'pending'
                        ORDER BY "created" ASC
                        FOR UPDATE SKIP LOCKED LIMIT 1
                    """
                    results = db.select(query)
                    if results is not False:
                        # Check for results
                        if len(results) == 0:
                            # No action
                            return LBEC.inaction
                        else:
                            # Pending
                            deploy_site = results[0]
                            # Params
                            deploy_id = deploy_site["deploy_id"]
                            site_id = deploy_site["site_id"]
                            # Deploy site
                            if LBDeploySites.pending.deploy(deploy_id, site_id):
                                status = "complete"
                            else:
                                status = "failed"
                            # Update pending row
                            query = """
                                UPDATE deploy_sites SET "status" = %s
                                WHERE "deploy_id" = %s AND "site_id" = %s
                            """
                            if db.execute(query, [status, deploy_id, site_id]):
                                if db.commit():
                                    # Action
                                    return LBEC.action
            # Connection or query failed
            return LBEC.failure

        @staticmethod
        def add():
            with LBDB() as db:
                if db.connect(LBDB.core):
                    # Get latest completed service deployments
                    query = """
                        SELECT DISTINCT ON ("service_id") "service_id",
                        "deploy_id", "build", "status", "created"
                        FROM deploy_services
                        WHERE "status" = 'complete'
                        ORDER BY "service_id", "created" DESC
                    """
                    if deploys := db.select(query):
                        for deploy in deploys:
                            deploy_id = deploy["deploy_id"]
                            service_id = deploy["service_id"]
                            # Get site deployment rows for deploy_id
                            query = """
                                SELECT * FROM deploy_sites
                                WHERE "deploy_id" = %s
                            """
                            results = db.select(query, [deploy_id]) or []
                            # Check for missing site deployment rows
                            current = [result["site_id"] for result in results]
                            target = [site["site_id"] for site in LBSites.for_service(service_id)]
                            for site_id in list(set(target) - set(current)):
                                # Add pending site deployment row
                                query = """
                                    INSERT INTO deploy_sites("deploy_id", "site_id", "status")
                                    VALUES(%s, %s, %s)
                                """
                                if db.execute(query, [deploy_id, site_id, "pending"]):
                                    return True

        @staticmethod
        def deploy(deploy_id, site_id):
            # Get site
            if site := LBSites.get(site_id):
                # Params
                service_id = site["service_id"]
                service_path = LBDeploys.service.path(service_id, deploy_id)
                # Check service deployment folder exists
                if LBDir.exists(service_path):
                    # Get config
                    config = LBConfig(service_path)
                    # Resources
                    LBResources.update(config.resources, site_id)
                    # Environment
                    env_vars = LBDeploys.site.env(site_id, deploy_id)
                    # Phase: Tenant
                    for action in config.phases.get("tenant", []):
                        if not LBRuntime.python3.action(service_path, action, env_vars):
                            return False
                    # Result
                    return True
