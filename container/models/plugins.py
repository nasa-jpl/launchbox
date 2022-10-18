import requests
from packaging import version

from manage.git import LBGithub
from manage.notify import LBNotify
from manage.result import LBError
from manage.util import LBDB, LBEnv, LBEvent


class LBPlugins:
    token = LBEnv.get("GIT_TOKEN", False)

    @staticmethod
    def add(repo_url, provider_id, branch=None):
        if repo := LBGithub.repo(repo_url, token=LBPlugins.token):
            branch = branch if branch else repo["default_branch"]
            # Check
            if not (config := LBPlugins.config(repo["url"], branch=branch)["plugin"]):
                return LBError("LBPlugins.add", "Error getting config file", log_level="warn")
            if LBPlugins.exists(config["identifier"]):
                return LBError("LBPlugins.add", "Plugin already exists", log_level="warn")
            # Add to DB
            with LBDB() as db:
                if db.connect(LBDB.core):
                    query = """
                        INSERT INTO plugins(
                            "plugin_id", "provider_id", "name", "type",
                            "repo_url", "branch", "version", "requirements"
                        )
                        VALUES(%s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    args = [
                        config["identifier"],
                        provider_id,
                        config["name"],
                        config["type"],
                        repo["url"],
                        branch,
                        config["version"],
                        config["requirements"],
                    ]
                    if db.execute(query, args):
                        # Log
                        LBEvent.complete("LBPlugins.add", f"Added plugin [plugin_id: {config['identifier']}]")
                        return True
            return False

    @staticmethod
    def config(repo_url, branch=None):
        if config := LBGithub.content(repo_url, path="plugin.yaml", branch=branch, token=LBPlugins.token):
            return config

    @staticmethod
    def exists(plugin_id):
        with LBDB() as db:
            if db.connect(LBDB.core):
                query = """SELECT 1 FROM plugins WHERE "plugin_id" = %s LIMIT 1"""
                if results := db.select(query, [plugin_id]):
                    return len(results) == 1
        return False

    @staticmethod
    def get(plugin_id):
        with LBDB() as db:
            if db.connect(LBDB.core):
                query = """SELECT * FROM plugins WHERE "plugin_id" = %s"""
                if results := db.select(query, [plugin_id]):
                    return results[0]
        return False

    @staticmethod
    def list():
        with LBDB() as db:
            if db.connect(LBDB.core):
                query = """
                    SELECT * FROM plugins ORDER BY "type", "name"
                """
                if plugins := db.select(query):
                    return plugins
        return []

    @staticmethod
    def of_type(plugin_type):
        with LBDB() as db:
            if db.connect(LBDB.core):
                query = """
                    SELECT * FROM plugins WHERE "type" = %s ORDER BY "type", "name"
                """
                if plugins := db.select(query, [plugin_type]):
                    return plugins
        return []

    @staticmethod
    def remove(plugin_id):
        if LBPlugins.exists(plugin_id):
            with LBDB() as db:
                if db.connect(LBDB.core):
                    if db.execute("""DELETE FROM plugins WHERE "plugin_id" = %s""", [plugin_id]):
                        # Log
                        LBEvent.complete("LBPlugins.remove", f"[{plugin_id}] Removed")
                        # Sync
                        LBNotify.send("plugins", "remove", {"plugin_id": plugin_id})
                        return True
        return False

    @staticmethod
    def update(plugin_id):
        if plugin := LBPlugins.get(plugin_id):
            # Check
            if not (config := LBPlugins.config(plugin["repo_url"], branch=plugin["branch"])["plugin"]):
                return LBError("Config", "Error getting config file", log_level="warn")
            if not isinstance(version.parse(config["version"]), version.Version):
                return LBError("Version", "Invalid version", log_level="warn")
            if not version.parse(plugin["version"]) < version.parse(config["version"]):
                text = f"No new versions found. Installed [{plugin['version']}], " f"Source [{config['version']}]"
                return LBError("Version", text, log_level="warn")
            # Update DB
            with LBDB() as db:
                if db.connect(LBDB.core):
                    query = """
                        UPDATE plugins
                        SET "name" = %s, "version" = %s, "requirements" = %s
                        WHERE "plugin_id" = %s
                    """
                    if db.execute(query, [config["name"], config["version"], config["requirements"], plugin_id]):
                        # Log
                        LBEvent.complete(
                            "LBPlugins.update",
                            f"Plugin [{plugin_id}] updated. {plugin['version']} -> " f"{config['version']}",
                        )
                        return True
            return False

    class API:
        hostname = "localhost"
        port = 8004
        url = f"http://{hostname}:{port}"

        @staticmethod
        def endpoint(path, resource, query):
            return f"{LBPlugins.API.url}/{path}/{resource}/{query}"

        @staticmethod
        def query(url):
            # Call
            response = requests.get(url, timeout=15)
            # Results
            if response.status_code == 200:
                try:
                    payload = response.json()
                    return payload
                except Exception as e:
                    return LBError("LBPlugins.API.query", f"Exception [{e}]", log_level="error")
            else:
                return LBError("LBPlugins.API.query", f"Invalid response [{response.status_code}]", log_level="warn")

    class identity:
        @staticmethod
        def get_group(plugin_id, group_id):
            result = LBPlugins.API.query(LBPlugins.API.endpoint(plugin_id, "group", group_id))
            return result["group"]

        @staticmethod
        def get_user(plugin_id, user_id):
            result = LBPlugins.API.query(LBPlugins.API.endpoint(plugin_id, "user", user_id))
            return result["user"]

        @staticmethod
        def search_user(plugin_id, user_id):
            result = LBPlugins.API.query(LBPlugins.API.endpoint(plugin_id, "search", user_id))
            return result["search"]

        @staticmethod
        def user_groups(plugin_id, user_id):
            result = LBPlugins.API.query(LBPlugins.API.endpoint(plugin_id, "groups", user_id))
            return result["groups"]

    class auth:
        # TODO: Add callback method
        @staticmethod
        def callback():
            pass

        # TODO: Add login method
        @staticmethod
        def login(plugin_id, callback):
            pass

        # TODO: Add metadata method
        @staticmethod
        def metadata():
            pass
