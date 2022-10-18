import json
import re

from manage.git import LBGithub
from manage.util import LBDB, LBEnv, LBEvent
from models.deploys import LBDeploys


class LBServices:
    # Add service
    @staticmethod
    def add(service_id, provider_id, name, repo_url, branch, env_name, options={}):
        # Check
        if type(options) is not dict:
            return False
        if not LBServices.valid(service_id):
            return False
        if LBServices.exists(service_id):
            return False
        with LBDB() as db:
            if db.connect(LBDB.core):
                query = """
                    INSERT INTO services(
                        "service_id", "provider_id", "name", "repo_url", "branch",
                        "env_name", "options"
                    )
                    VALUES(%s, %s, %s, %s, %s, %s, %s)
                """
                args = [
                    service_id,
                    provider_id,
                    name,
                    repo_url,
                    branch,
                    env_name,
                    json.dumps(options),
                ]
                if db.execute(query, args):
                    LBEvent.complete("LBServices.add", f"Added service [service_id: {service_id}]")
                    return True
        return False

    # Deploy service
    @staticmethod
    def deploy(service_id, commit_sha):
        if deploy_id := LBDeploys.service.add(service_id, commit_sha):
            return deploy_id

    # Check if service exists
    @staticmethod
    def exists(service_id):
        with LBDB() as db:
            with LBDB() as db:
                if db.connect(LBDB.core):
                    query = """SELECT 1 FROM services WHERE "service_id" = %s LIMIT 1"""
                    if results := db.select(query, [service_id]):
                        return len(results) == 1
            return False

    # Get service
    @staticmethod
    def get(service_id):
        with LBDB() as db:
            with LBDB() as db:
                if db.connect(LBDB.core):
                    query = """SELECT * FROM services WHERE "service_id" = %s"""
                    if results := db.select(query, [service_id]):
                        service = results[0]
                        # Params
                        repo_url = service["repo_url"]
                        branch = service["branch"]
                        token = LBEnv.get("GIT_TOKEN")
                        # Hydrate
                        service["commits"] = LBGithub.commits(repo_url, branch, token)
                        service["deployments"] = LBDeploys.service.list(service_id)
                        return results[0]
            return False

    # List services
    @staticmethod
    def list():
        with LBDB() as db:
            if db.connect(LBDB.core):
                query = """SELECT * FROM services ORDER BY "service_id" ASC"""
                if services := db.select(query):
                    return services
        return []

    # Validate service_id
    @staticmethod
    def valid(service_id):
        return re.match(r"^[A-Za-z0-9-]+$", service_id) is not None
