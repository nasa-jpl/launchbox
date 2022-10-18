import json

from api.connect import LBConnect
from manage.bridge import LBBridge
from manage.config import LBConfig
from manage.git import LBGithub
from manage.infra import LBInfra
from manage.util import LBDB, LBUUID, LBDir, LBEnv, LBEvent, LBPath
from models.resources import LBResources


class LBDeploys:
    @staticmethod
    def get(deploy_id):
        with LBDB() as db:
            if db.connect(LBDB.core):
                query = """
                    SELECT "deploy_id", "service_id", "build", "commit_sha", "status", "created"::timestamptz
                    FROM deploy_services
                    WHERE "deploy_id" = %s
                """
                if results := db.select(query, [deploy_id]):
                    deploy = results[0]
                    # Hydrate
                    deploy["actions"] = {
                        "pending": [],
                        "complete": [],
                    }
                    for action in LBDeploys.service.actions.list(deploy_id):
                        match action["step"]:
                            case "pending":
                                deploy["actions"]["pending"].append(action)
                            case "complete":
                                deploy["actions"]["complete"].append(action)
                    deploy["sites"] = LBDeploys.site.list(deploy_id)
                    # Result
                    return deploy

    @staticmethod
    def list():
        with LBDB() as db:
            if db.connect(LBDB.core):
                query = """
                    SELECT d1."deploy_id", d1."service_id",
                    d1."build", d1."commit_sha",
                    d1."status", d1."created"::timestamptz,
                    s1."repo_url", s1."branch", s1."env_name"
                    FROM deploy_services d1
                    LEFT JOIN services s1 ON (d1."service_id" = s1."service_id")
                    ORDER BY "created" DESC
                """
                if results := db.select(query):
                    # Hydrate
                    for result in results:
                        deploy_id = result["deploy_id"]
                        commit_sha = result["commit_sha"]
                        repo_url = result["repo_url"]
                        result["commit_url"] = f"{repo_url}/commits/{commit_sha}"
                        result["sites"] = LBDeploys.site.list(deploy_id)
                    # Result
                    return results
        return []

    class service:
        # Add new service deploy
        @staticmethod
        def add(service_id, commit_sha):
            if LBDeploys.service.verify(service_id, commit_sha):
                with LBDB() as db:
                    if db.connect(LBDB.core):
                        deploy_id = LBUUID.uuid()
                        query = """
                            INSERT INTO deploy_services(
                                "deploy_id", "service_id",
                                "commit_sha", "status"
                            )
                            VALUES(%s, %s, %s, %s)
                        """
                        args = [deploy_id, service_id, commit_sha, "pending"]
                        if db.execute(query, args):
                            return deploy_id

        @staticmethod
        def build_path(deploy_id):
            return LBPath.builds(deploy_id)

        @staticmethod
        def config(deploy_id):
            if deploy := LBDeploys.service.get(deploy_id):
                if LBDir.exists(deploy["path"]):
                    config = LBConfig(deploy["path"])
                    if config.validate():
                        return config

        @staticmethod
        def get(deploy_id):
            with LBDB() as db:
                if db.connect(LBDB.core):
                    query = """
                        SELECT
                        d1."deploy_id", d1."service_id", d1."commit_sha", d1."status",
                        s1."repo_url", s1."branch", s1."env_name"
                        FROM deploy_services d1 LEFT JOIN services s1
                        ON (d1."service_id" = s1."service_id")
                        WHERE d1."deploy_id" = %s
                    """
                    if results := db.select(query, [deploy_id]):
                        deploy = results[0]
                        # Params
                        service_id = deploy["service_id"]
                        path = LBPath.services(f"{service_id}/{deploy_id}")
                        # Related
                        sites = db.select("""SELECT * FROM sites WHERE "service_id" = %s""", [service_id])
                        # Results
                        deploy["path"] = path
                        deploy["sites"] = sites
                        return deploy

        # Get latest deploy for service_id
        @staticmethod
        def latest(service_id):
            with LBDB() as db:
                if db.connect(LBDB.core):
                    query = """
                        SELECT deploy_id FROM deploy_services
                        WHERE "service_id" = %s AND "status" = 'complete'
                        ORDER BY "created" DESC
                        LIMIT 1
                    """
                    if results := db.select(query, [service_id]):
                        deploy_id = results[0]["deploy_id"]
                        return LBDeploys.service.get(deploy_id)
            return False

        # Get all deploys for service_id
        @staticmethod
        def list(service_id):
            with LBDB() as db:
                if db.connect(LBDB.core):
                    query = """
                        SELECT * FROM deploy_services
                        WHERE "service_id" = %s
                        ORDER BY "created" DESC
                    """
                    if results := db.select(query, [service_id]):
                        return results
            return False

        # Get path for service deploy
        @staticmethod
        def path(service_id, deploy_id):
            return LBPath.services(f"{service_id}/{deploy_id}")

        # Verify commit SHA is valid for service
        @staticmethod
        def verify(service_id, commit_sha):
            with LBDB() as db:
                if db.connect(LBDB.core):
                    query = """SELECT "repo_url" FROM services WHERE "service_id" = %s"""
                    if results := db.select(query, [service_id]):
                        repo_url = results[0]["repo_url"]
                        if LBGithub.commit(repo_url, commit_sha, token=LBEnv.get("GIT_TOKEN")):
                            return True

        class actions:
            # Add service deploy action
            @staticmethod
            def add(deploy_id, step, text, status="pending"):
                with LBDB() as db:
                    if db.connect(LBDB.core):
                        action_id = LBUUID.uuid()
                        container_id = LBInfra.current.identifier()
                        metadata = json.dumps({})
                        query = """
                            INSERT INTO deploy_services_actions(
                                "action_id", "container_id", "deploy_id", "step", "text", "metadata", "status"
                            )
                            VALUES(%s, %s, %s, %s, %s, %s, %s)
                        """
                        args = [action_id, container_id, deploy_id, step, text, metadata, status]
                        if db.execute(query, args):
                            # Log
                            LBEvent.log(
                                "LBDeploys.service.action",
                                f"Step: {step} | {text} | Status: {status}",
                                {
                                    "action_id": action_id,
                                    "container_id": container_id,
                                    "deploy_id": deploy_id,
                                },
                            )
                            # Result
                            return action_id

            # Mark service deploy action complete
            @staticmethod
            def complete(action_id, metadata={}):
                return LBDeploys.service.actions.update(action_id, "complete", metadata)

            # Mark service deploy action failed
            @staticmethod
            def failed(action_id, metadata={}):
                return LBDeploys.service.actions.update(action_id, "failed", metadata)

            # Get service deploy action
            @staticmethod
            def get(action_id):
                with LBDB() as db:
                    if db.connect(LBDB.core):
                        query = """
                            SELECT * FROM deploy_services_actions
                            WHERE "action_id" = %s
                        """
                        if results := db.select(query, [action_id]):
                            return results[0]

            # Get service deploy actions for deploy_id
            @staticmethod
            def list(deploy_id):
                with LBDB() as db:
                    if db.connect(LBDB.core):
                        query = """
                            SELECT * FROM deploy_services_actions
                            WHERE "deploy_id" = %s
                            ORDER BY created ASC
                        """
                        if actions := db.select(query, [deploy_id]):
                            return actions

            # Update service deploy action status
            @staticmethod
            def update(action_id, status, metadata={}):
                if action := LBDeploys.service.actions.get(action_id):
                    with LBDB() as db:
                        if db.connect(LBDB.core):
                            query = """
                                UPDATE deploy_services_actions
                                SET "metadata" = %s, "status" = %s
                                WHERE "action_id" = %s
                            """
                            if db.execute(query, [json.dumps(metadata), status, action_id]):
                                # Params
                                step = action["step"]
                                text = action["text"]
                                # Log
                                LBEvent.log(
                                    "LBDeploys.service.action",
                                    f"Step: {step} | {text} | Status: {status}",
                                    {
                                        "action_id": action_id,
                                        "deploy_id": action["deploy_id"],
                                        "container_id": action["container_id"],
                                    },
                                )
                                # Result
                                return True

    class site:
        # Get site env vars for deploy
        @staticmethod
        def env(site_id, deploy_id):
            if deploy := LBDeploys.service.get(deploy_id):
                service_id = deploy["service_id"]
                env_name = deploy["env_name"]
                if config := LBDeploys.service.config(deploy_id):
                    env = config.env
                    # Base environment
                    result = env.get("base", {})
                    result["ENVIRONMENT"] = env_name
                    result["LB_BRIDGE_PORT"] = LBBridge.port
                    result["LB_CONNECT_API"] = LBConnect.endpoint(site_id, deploy_id)
                    result["LB_SERVICE_ID"] = service_id
                    result["LB_SITE_ID"] = site_id
                    # Specific environment
                    if specific := env.get(env_name):
                        result.update(specific)
                    # Resources
                    for name, config in LBDeploys.site.resources(site_id, deploy_id).items():
                        result.update(config["env_vars"])
                    return result
            return False

        # Get latest deploy for site_id
        @staticmethod
        def latest(site_id):
            with LBDB() as db:
                if db.connect(LBDB.core):
                    query = """SELECT "service_id" FROM sites WHERE "site_id" = %s"""
                    if results := db.select(query, [site_id]):
                        service_id = results[0]["service_id"]
                        if deploy := LBDeploys.service.latest(service_id):
                            deploy_id = deploy["deploy_id"]
                            deploy["resources"] = LBDeploys.site.resources(site_id, deploy_id)
                            return deploy
            return False

        # Get all site deploys for deploy_id
        def list(deploy_id):
            with LBDB() as db:
                if db.connect(LBDB.core):
                    query = """
                        SELECT * FROM deploy_sites
                        WHERE deploy_id = %s
                        ORDER BY "site_id" ASC
                    """
                    if results := db.select(query, [deploy_id]):
                        return results
            return []

        # Get path for site deploy
        @staticmethod
        def path(site_id, deploy_id):
            return LBPath.sites(f"{site_id}/{deploy_id}")

        # Get site resources for deploy
        @staticmethod
        def resources(site_id, deploy_id):
            if config := LBDeploys.service.config(deploy_id):
                results = {}
                for name, config in config.resources.items():
                    results[name] = {
                        "env_vars": LBResources.env_vars(name, config, site_id),
                        "params": LBResources.params(name, config, site_id),
                    }
                return results
            return False

        # Get site routes for deploy
        @staticmethod
        def routes(site_id, deploy_id):
            if config := LBDeploys.service.config(deploy_id):
                return config.routes
